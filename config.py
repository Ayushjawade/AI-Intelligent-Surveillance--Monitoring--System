# config.py

PROJECT_NAME = "AI-Based Intelligent Surveillance Monitoring System"

# Admin login details
ADMIN_USERNAME = "Master Ayush"
ADMIN_PASSWORD = "Master"

# Telegram Bot details
# We will add real token and chat ID later
TELEGRAM_BOT_TOKEN = "8912448988:AAGSwQkiQIr_WffXCWh6UJrOdqGlRgc3YnE"
TELEGRAM_CHAT_ID = "6937808828"

# YOLO detection confidence
CONFIDENCE_THRESHOLD = 0.45

# RED means high-risk / dangerous object
RED_OBJECTS = [
    "knife",
    "gun",
    "pistol",
    "rifle",
    "weapon",
    "explosive",
    "cell phone"  # Phones can be used for remote detonation, so we treat them as high-risk in this context
]

# ORANGE means suspicious object
ORANGE_OBJECTS = [
    "backpack",
    "suitcase",
    "handbag",
    "scissors",
    "baseball bat"
]

# GREEN means normal object
GREEN_OBJECTS = [
    "person",
    "car",
    "bus",
    "truck",
    "bicycle",
    "motorcycle",
    "chair",
    "laptop",
    "cell phone"
]