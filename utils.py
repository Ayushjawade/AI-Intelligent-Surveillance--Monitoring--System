# utils.py

from config import RED_OBJECTS, ORANGE_OBJECTS


def classify_threat(object_name):
    """
    Converts detected object name into threat level.
    """
    object_name = object_name.lower()

    if object_name in RED_OBJECTS:
        return "RED"

    elif object_name in ORANGE_OBJECTS:
        return "ORANGE"

    else:
        return "GREEN"


def get_threat_color(threat_level):
    """
    Returns BGR color for OpenCV bounding box.
    OpenCV uses BGR, not RGB.
    """
    if threat_level == "RED":
        return (0, 0, 255)       # Red

    elif threat_level == "ORANGE":
        return (0, 165, 255)     # Orange

    else:
        return (0, 255, 0)       # Green