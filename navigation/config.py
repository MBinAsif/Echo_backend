# config.py

# ✅ Object labels the model is allowed to react to
ALLOWED_CLASSES = {
    "person", "chair", "bicycle", "car", "dog", "cat",
    "motorbike", "bus", "truck", "door", "window",
    "laptop", "cell phone", "tv", "bed"
}

# ✅ Navigation-related metadata: priority, height (cm), and alert range (cm)
NAVIGATION_OBJECTS = {
    "person": {"priority": 1, "height": 170, "alert_distance": 150},
    "chair": {"priority": 2, "height": 90, "alert_distance": 100},
    "bicycle": {"priority": 2, "height": 100, "alert_distance": 120},
    "car": {"priority": 1, "height": 150, "alert_distance": 200},
    "dog": {"priority": 2, "height": 40, "alert_distance": 80},
    "cat": {"priority": 3, "height": 25, "alert_distance": 50},
    "motorbike": {"priority": 1, "height": 130, "alert_distance": 150},
    "bus": {"priority": 1, "height": 300, "alert_distance": 250},
    "truck": {"priority": 1, "height": 350, "alert_distance": 300},
    "door": {"priority": 2, "height": 200, "alert_distance": 150},
    "window": {"priority": 2, "height": 150, "alert_distance": 100},
    "laptop": {"priority": 2, "height": 30, "alert_distance": 100},
    "cell phone": {"priority": 3, "height": 15, "alert_distance": 60},
    "tv": {"priority": 2, "height": 120, "alert_distance": 150},
    "bed": {"priority": 2, "height": 500, "alert_distance": 200}
}
