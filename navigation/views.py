# Path: echotrail_backend/navigation/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from PIL import Image
import numpy as np
import logging
import time

# Import shared config
from .config import ALLOWED_CLASSES, NAVIGATION_OBJECTS

# Third-party imports
from ultralytics import YOLO

# Configure logging
logger = logging.getLogger(__name__)

# Load YOLO model globally
model = YOLO('yolov8m.pt')

# Global state to track last spoken alerts
last_spoken = {
    "clear_path": False,
    "objects": {},
    "last_update": 0.0
}

cooldown_priorities = {1: 2, 2: 4, 3: 6}  # in seconds

class ObstacleDetectView(APIView):
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
    
    
    parser_classes = [MultiPartParser]

    def post(self, request):
        """
        Handle image upload, run YOLO detection, and return contextual audio messages and bounding boxes.
        """
        file = request.FILES.get('image')
        print("📷 Received image file:", file.name)

        if not file:
            logger.error("No image provided in request")
            return Response({"error": "No image provided"}, status=400)

        try:
            # Convert uploaded image to NumPy array
            img = Image.open(file).convert("RGB")
            frame = np.array(img)
            frame_width, frame_height = frame.shape[1], frame.shape[0]
            current_time = time.time()

            # Enforce minimum interval between announcements (1 second)
            if current_time - last_spoken["last_update"] < 1.0:
                logger.debug("Skipping announcement due to minimum interval")
                return Response({"message": "", "objects": []})

            results = model(frame, conf=0.1, verbose=True)  # Lowered confidence threshold
            print("🎯 YOLO raw results:", results)
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    print(f"👀 Detected: {label}")
            detected_objects = []

            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    conf = float(box.conf[0])

                    if label not in ALLOWED_CLASSES:
                        logger.debug(f"Skipping non-allowed class: {label}")
                        continue

                    obj_info = NAVIGATION_OBJECTS.get(label, {"priority": 2, "height": 80, "alert_distance": 100})
                    center_x = (x1 + x2) / 2

                    # Determine direction
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
                        logger.warning(f"Invalid box height for {label}")
                        continue

                    focal_length = 615
                    distance_cm = int((obj_info["height"] * focal_length) / box_height)

                    if distance_cm > obj_info["alert_distance"]:
                        logger.debug(f"Skipping {label} at {distance_cm}cm (beyond alert_distance {obj_info['alert_distance']}cm)")
                        continue

                    detected_objects.append({
                        'label': label,
                        'distance': distance_cm,
                        'direction': direction,
                        'priority': obj_info['priority'],
                        'confidence': conf,
                        'box': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                    })

            # Sort by priority and distance
            detected_objects.sort(key=lambda x: (x['priority'], x['distance']))

            # Generate contextual messages
            messages = self.generate_alerts(detected_objects, current_time)

            # Prepare objects for rendering (all detected objects)
            response_objects = [
                {
                    'label': obj['label'],
                    'distance': obj['distance'],
                    'box': obj['box']
                }
                for obj in detected_objects
            ]

            last_spoken["last_update"] = current_time

            if not messages:
                logger.debug("No new announcements needed")
                return Response({"message": "", "objects": response_objects})

            logger.info(f"Returning messages: {', '.join(messages)}, objects: {len(response_objects)}")
            environment = self.classify_environment(detected_objects)

            return Response({
                "message": ", ".join(messages),
                "objects": response_objects,
                "environment": environment
            })


        except Exception as e:
            logger.error(f"Error processing image: {str(e)}", exc_info=True)
            return Response({"error": f"Processing failed: {str(e)}"}, status=500)

    def generate_alerts(self, objects, current_time):
        """
        Generate contextual alert messages based on detected objects.
        Avoid repeating alerts unless necessary.
        """
        global last_spoken

        messages = []
        if not objects:
            # Announce clear path only once
            if not last_spoken["clear_path"]:
                messages.append("Clear path ahead")
                last_spoken["clear_path"] = True
                last_spoken["objects"] = {}
                logger.info("Announcing clear path ahead")
            return messages

        # Reset clear path flag when objects are detected
        last_spoken["clear_path"] = False

        important_objects = [obj for obj in objects if obj['priority'] <= 2 and obj['distance'] < 100]

        for obj in important_objects[:3]:  # Limit to 3 important ones

            location_key = "unknown"  # unless you pass GPS coords to backend
            key = f"{obj['label']}-{obj['direction']}-{location_key}"
            priority = obj['priority']
            distance = obj['distance']

            base_cooldown = cooldown_priorities.get(priority, 5)
            should_announce = False

            if key not in last_spoken["objects"]:
                should_announce = True
                logger.info(f"New object detected: {key}, distance: {distance}cm")
            else:
                last_distance = last_spoken["objects"][key]["distance"]
                last_time = last_spoken["objects"][key]["time"]
                if distance < 0.7 * last_distance:
                    should_announce = True
                    logger.info(f"Dangerously close: {key}, from {last_distance}cm to {distance}cm")
                elif current_time - last_time > base_cooldown:
                    should_announce = True
                    logger.info(f"Cooldown expired for {key}, re-announcing at {distance}cm")

            if should_announce:
                message = self.create_contextual_message(obj)
                messages.append(message)
                last_spoken["objects"][key] = {"distance": distance, "time": current_time}

        return messages

    def create_contextual_message(self, obj):
        """
        Create a natural language description of an object.
        """
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
        elif label == "bed":
            return f"Bed {distance_desc} on your {direction}"
        elif label == "tv":
            return f"TV {distance_desc} on your {direction}"
        elif label == "laptop":
            return f"Laptop {distance_desc} on your {direction}"
        elif label == "cell phone":
            return f"Phone {distance_desc} on your {direction}"
        else:
            return f"{label.capitalize()} {distance_desc} on your {direction}"

    def classify_environment(self, objects):
        street_keywords = {"car", "truck", "bus", "traffic light", "stop sign", "bicycle"}
        indoor_keywords = {"chair", "window", "door", "table", "bed", "tv", "laptop", "cell phone"}

        street_score = sum(1 for obj in objects if obj['label'] in street_keywords)
        indoor_score = sum(1 for obj in objects if obj['label'] in indoor_keywords)

        if street_score > indoor_score:
            return "street"
        elif indoor_score > street_score:
            return "indoor"
        else:
            return "unknown"