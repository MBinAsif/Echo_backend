# detect_obstacles.py

import cv2
import time
import numpy as np
from ultralytics import YOLO
import pyttsx3
import threading
import queue
import serial
import math
import speech_recognition as sr
from datetime import datetime
import pygame
import os
import pickle
import json

# Import shared config
from navigation.config import ALLOWED_CLASSES, NAVIGATION_OBJECTS

class NavigationSystem:
    def __init__(self):
        self.model = YOLO('yolov8m.pt')
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.engine_lock = threading.Lock()
        self.user_preferences = self.load_user_preferences() or {
            'speech_rate': 140,
            'volume': 0.9,
            'alert_frequency': 1.0
        }

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone() if sr.Microphone.get_device_count() > 0 else None
        self.voice_commands_active = self.microphone is not None

        self.haptic_device = self.init_haptic_device()

        self.current_location = None
        self.route_history = []
        self.location_memory = {}
        self.last_spoken = {"clear_path": False, "objects": {}, "last_update": 0.0}
        self.cooldown_priorities = {1: 2, 2: 4, 3: 6}  # in seconds
        self.quiet_mode = False

        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except pygame.error:
            print("⚠️ Audio initialization failed")
            self.audio_enabled = False

        self.audio_thread = threading.Thread(target=self.audio_worker, daemon=True)
        self.audio_thread.start()

    def init_haptic_device(self):
        """Try to connect to haptic feedback device"""
        ports = ['/dev/ttyUSB0', '/dev/ttyACM0', 'COM3']
        for port in ports:
            try:
                return serial.Serial(port, 9600)
            except Exception:
                continue
        print("📳 Haptic device not available")
        return None

    def send_haptic_feedback(self, objects):
        if not self.haptic_device or not objects:
            return
        try:
            priority_obj = objects[0]
            direction = priority_obj['direction']
            distance = priority_obj['distance']

            dir_code_map = {
                "far left": 1, "left": 2, "slightly left": 3,
                "center": 4, "slightly right": 5, "right": 6, "far right": 7
            }
            dir_code = dir_code_map.get(direction, 4)

            command = f"1,{dir_code},{distance}\n"
            self.haptic_device.write(command.encode())
        except Exception as e:
            print(f"Haptic feedback error: {e}")

    def play_spatial_audio(self, text, priority, direction_angle=0, distance_factor=1.0):
        if not self.audio_enabled or self.quiet_mode:
            return

        temp_file = f"temp_audio_{priority}.wav"
        try:
            with self.engine_lock:
                engine = pyttsx3.init()
                engine.setProperty('rate', self.user_preferences.get('speech_rate', 140))
                engine.save_to_file(text, temp_file)
                engine.runAndWait()

            sound = pygame.mixer.Sound(temp_file)
            stereo_pos = direction_angle / 180.0
            volume = max(0.3, min(1.0, 1.0 / max(1, distance_factor)))

            left_volume = volume * (1 - max(0, stereo_pos))
            right_volume = volume * (1 + min(0, stereo_pos))

            channel = pygame.mixer.Channel(0)
            channel.set_volume(left_volume, right_volume)
            channel.play(sound)

            while channel.get_busy():
                time.sleep(0.1)

            os.remove(temp_file)
        except Exception as e:
            print(f"Audio playback error: {e}")
            with self.engine_lock:
                self.is_speaking = True
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                self.is_speaking = False

    def create_contextual_message(self, obj):
        label = obj['label']
        distance = obj['distance']
        direction = obj['direction']

        if distance < 30:
            distance_desc = "right in front of you"
        elif distance < 60:
            distance_desc = "very close"
        elif distance < 100:
            distance_desc = "close"
        else:
            distance_desc = f"{distance} centimeters away"

        if label == "person":
            return f"Person {distance_desc} on your {direction} - please be careful"
        elif label in ["car", "truck", "bus"]:
            return f"Vehicle {distance_desc} on your {direction} - caution advised"
        elif label == "door":
            return f"Door approaching on your {direction}"
        elif label == "window":
            return f"Window detected on your {direction}"
        elif label == "chair":
            return f"Chair {distance_desc} on your {direction}"
        elif label == "bicycle":
            return f"Bicycle {distance_desc} on your {direction}"
        elif label == "dog":
            return f"Dog nearby on your {direction}"
        elif label == "cat":
            return f"Cat nearby on your {direction}"
        else:
            return f"{label.capitalize()} {distance_desc} on your {direction}"

    def classify_environment(self, objects):
        street_keywords = {"car", "truck", "bus", "traffic light", "stop sign", "bicycle"}
        indoor_keywords = {"chair", "window", "door", "table", "bed"}
        
        street_score = sum(1 for obj in objects if obj['label'] in street_keywords)
        indoor_score = sum(1 for obj in objects if obj['label'] in indoor_keywords)

        if street_score > indoor_score:
            return "street"
        elif indoor_score > street_score:
            return "indoor"
        else:
            return "unknown"

    def generate_enhanced_alerts(self, objects, current_time):
        if not objects:
            if not self.quiet_mode and not self.last_spoken["clear_path"]:
                self.play_spatial_audio("Clear path ahead", 0, 0.0, 1.0)
                self.last_spoken["clear_path"] = True
                self.last_spoken["objects"] = {}
            return

        self.last_spoken["clear_path"] = False

        for obj in objects[:2]:
            priority = obj['priority']
            distance = obj['distance']
            alert_distance = obj['alert_distance']

            if distance > alert_distance:
                continue

            location_key = f"{self.current_location['lat']:.3f},{self.current_location['lng']:.3f}" if self.current_location else "unknown"
            key = f"{obj['label']}-{obj['direction']}-{location_key}"
            base_cooldown = self.cooldown_priorities.get(priority, 5)
            cooldown = base_cooldown * self.user_preferences.get('alert_frequency', 1.0)

            should_announce = False

            if key not in self.last_spoken["objects"]:
                should_announce = True
            else:
                last_distance = self.last_spoken["objects"][key]["distance"]
                last_time = self.last_spoken["objects"][key]["time"]

                if distance < 0.7 * last_distance or (current_time - last_time) > cooldown:
                    should_announce = True

            if should_announce and not self.quiet_mode:
                message = self.create_contextual_message(obj)
                direction_angle = self.calculate_direction_angle(obj['direction'])
                distance_factor = min(distance / 100, 3.0)
                self.audio_queue.put((message, priority, direction_angle, distance_factor))
                self.last_spoken["objects"][key] = {"distance": distance, "time": current_time}

    def calculate_direction_angle(self, direction):
        angles = {
            "far left": -90,
            "left": -45,
            "slightly left": -20,
            "center": 0,
            "slightly right": 20,
            "right": 45,
            "far right": 90
        }
        return angles.get(direction, 0)

    def update_location_memory(self, objects):
        if not self.current_location:
            return
        loc_key = f"{self.current_location['lat']:.3f},{self.current_location['lng']:.3f}"
        memory_entry = {
            'timestamp': datetime.now().isoformat(),
            'objects': objects[:]
        }
        self.location_memory[loc_key] = memory_entry

    def load_user_preferences(self):
        try:
            with open('user_preferences.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def run(self):
        cap = cv2.VideoCapture(0)
        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                results = self.model.predict(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), conf=0.25, verbose=False)

                frame_height, frame_width = frame.shape[:2]
                current_time = time.time()
                detected_objects = []

                for r in results:
                    for box in r.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cls_id = int(box.cls[0])
                        label = self.model.names[cls_id]

                        if label not in ALLOWED_CLASSES:
                            continue

                        obj_info = NAVIGATION_OBJECTS.get(label, {"priority": 2, "height": 80, "alert_distance": 100})
                        center_x = (x1 + x2) // 2

                        direction_zones = [
                            (0.0, 0.15, "far left"),
                            (0.15, 0.35, "left"),
                            (0.35, 0.45, "slightly left"),
                            (0.45, 0.55, "center"),
                            (0.55, 0.65, "slightly right"),
                            (0.65, 0.85, "right"),
                            (0.85, 1.0, "far right")
                        ]
                        direction = "center"
                        for start, end, dir_name in direction_zones:
                            if start <= center_x / frame_width < end:
                                direction = dir_name
                                break

                        box_height = y2 - y1
                        if box_height <= 0:
                            continue

                        focal_length = 615
                        distance_cm = int((obj_info["height"] * focal_length) / box_height)

                        detected_objects.append({
                            'label': label,
                            'distance': distance_cm,
                            'direction': direction,
                            'priority': obj_info['priority'],
                            'alert_distance': obj_info['alert_distance']
                        })

                detected_objects.sort(key=lambda x: (x['priority'], x['distance']))

                self.update_location_memory(detected_objects)

                self.generate_enhanced_alerts(detected_objects, current_time)

                self.send_haptic_feedback(detected_objects)

                cv2.imshow("Comprehensive Navigation System", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("🛑 Shutting down Comprehensive Navigation System...")
                    break

        finally:
            self.cleanup()
            cap.release()
            cv2.destroyAllWindows()

    def audio_worker(self):
        while True:
            try:
                item = self.audio_queue.get(timeout=1)
                if item is None:
                    break
                if len(item) == 4:
                    message, priority, angle, factor = item
                    self.play_spatial_audio(message, priority, angle, factor)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio worker error: {e}")

    def cleanup(self):
        print("🧹 Cleaning up...")
        self.voice_commands_active = False
        if self.haptic_device:
            try:
                self.haptic_device.close()
            except:
                pass
        self.audio_queue.put((None, 0))
        print("✅ Cleanup completed")

if __name__ == "__main__":
    nav_system = NavigationSystem()
    nav_system.run()