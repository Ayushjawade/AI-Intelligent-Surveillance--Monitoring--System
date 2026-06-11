# telegram_alert.py

import os
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def is_telegram_configured():
    """
    Checks whether Telegram bot token and chat ID are configured.
    """
    if TELEGRAM_BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("Telegram bot token is not configured.")
        return False

    if TELEGRAM_CHAT_ID == "PASTE_YOUR_CHAT_ID_HERE":
        print("Telegram chat ID is not configured.")
        return False

    return True


def send_telegram_alert(message):
    """
    Sends text-only alert message to Telegram.
    """
    if not is_telegram_configured():
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload, timeout=10)

        if response.status_code == 200:
            print("Telegram text alert sent successfully.")
        else:
            print("Telegram text alert failed:", response.text)

    except Exception as e:
        print("Telegram text alert error:", e)


def send_telegram_photo_alert(photo_path, caption):
    """
    Sends photo alert to Telegram with caption.
    Photo contains RED frame/bounding box.
    Caption contains object name, time, date, camera type, and threat level.
    """
    if not is_telegram_configured():
        return

    if not photo_path or not os.path.exists(photo_path):
        print("Photo not found. Sending text alert instead.")
        send_telegram_alert(caption)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption,
        "parse_mode": "HTML"
    }

    try:
        with open(photo_path, "rb") as photo:
            files = {
                "photo": photo
            }

            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=20
            )

        if response.status_code == 200:
            print("Telegram photo alert sent successfully.")
        else:
            print("Telegram photo alert failed:", response.text)

    except Exception as e:
        print("Telegram photo alert error:", e)