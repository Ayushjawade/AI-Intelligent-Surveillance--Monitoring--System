# detector.py

import cv2
import os
from datetime import datetime
from ultralytics import YOLO

from config import CONFIDENCE_THRESHOLD
from utils import classify_threat, get_threat_color
from database import insert_log
from telegram_alert import send_telegram_alert, send_telegram_photo_alert


class SurveillanceDetector:
    def __init__(self):
        # YOLOv8 nano model: lightweight and suitable for real-time detection
        self.model = YOLO("runs/detect/train-14/weights/best.pt")

        # Prevents continuous Telegram spam
        self.last_red_alert_time = None

    def save_snapshot(self, frame):
        """
        Saves the current frame as an evidence image.
        The saved image contains bounding boxes and labels.
        Microseconds are added in filename to avoid overwriting images.
        """
        os.makedirs("snapshots", exist_ok=True)

        filename = datetime.now().strftime("red_alert_%Y%m%d_%H%M%S_%f.jpg")
        path = os.path.join("snapshots", filename)

        cv2.imwrite(path, frame)

        return path

    def should_send_red_alert(self):
        """
        Sends RED alert every 5 seconds.
        This avoids Telegram spam but gives repeated evidence images.
        """
        now = datetime.now()

        if self.last_red_alert_time is None:
            self.last_red_alert_time = now
            return True

        time_difference = (now - self.last_red_alert_time).total_seconds()

        if time_difference > 5:
            self.last_red_alert_time = now
            return True

        return False

    def process_frame(self, frame, camera_source):
        """
        Main detection pipeline:

        1. Resize frame for speed
        2. Run YOLOv8 detection
        3. Classify object as GREEN / ORANGE / RED
        4. Draw bounding box and label
        5. Save snapshot for ORANGE/RED
        6. Store log in SQLite
        7. Send RED photo alert to Telegram every 5 seconds
        """

        # Resize frame for better speed
        frame = cv2.resize(frame, (640, 480))

        # Run YOLO detection
        results = self.model(frame, imgsz=320, verbose=False)

        highest_threat = "GREEN"
        detected_items = []

        for result in results:
            boxes = result.boxes

            for box in boxes:
                confidence = float(box.conf[0])

                if confidence < CONFIDENCE_THRESHOLD:
                    continue

                class_id = int(box.cls[0])
                object_name = self.model.names[class_id]

                threat_level = classify_threat(object_name)

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                color = get_threat_color(threat_level)

                label = f"{object_name} {confidence:.2f} [{threat_level}]"

                # Draw bounding box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    color,
                    2
                )

                # Prevent label from going outside frame
                label_top = max(y1 - 32, 0)

                # Draw label background
                cv2.rectangle(
                    frame,
                    (x1, label_top),
                    (x2, y1),
                    color,
                    -1
                )

                # Draw label text
                cv2.putText(
                    frame,
                    label,
                    (x1 + 5, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                detected_items.append({
                    "object": object_name,
                    "confidence": round(confidence, 2),
                    "threat": threat_level
                })

                snapshot_path = ""

                # Save snapshot after drawing box
                # This ensures Telegram receives image with RED/ORANGE frame
                if threat_level in ["ORANGE", "RED"]:
                    snapshot_path = self.save_snapshot(frame)

                # Save detection log into SQLite database
                insert_log(
                    camera_source=camera_source,
                    detected_object=object_name,
                    confidence=confidence,
                    threat_level=threat_level,
                    snapshot_path=snapshot_path
                )

                # RED alert logic
                if threat_level == "RED":
                    highest_threat = "RED"

                    if self.should_send_red_alert():
                        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        alert_caption = f"""
🚨 <b>RED ALERT DETECTED</b>

<b>Project:</b> AI Surveillance Monitoring System
<b>Detected Object:</b> {object_name}
<b>Confidence:</b> {confidence:.2f}
<b>Camera Type:</b> {camera_source}
<b>Date & Time:</b> {current_datetime}
<b>Threat Level:</b> RED

Immediate action required.
"""

                        if snapshot_path:
                            send_telegram_photo_alert(snapshot_path, alert_caption)
                        else:
                            send_telegram_alert(alert_caption)

                elif threat_level == "ORANGE" and highest_threat != "RED":
                    highest_threat = "ORANGE"

        return frame, highest_threat, detected_items