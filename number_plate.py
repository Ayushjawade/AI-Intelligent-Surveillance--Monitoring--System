# number_plate.py

import cv2
import re
import easyocr


class NumberPlateRecognizer:
    def __init__(self):
        # English OCR reader
        self.reader = easyocr.Reader(["en"], gpu=False)

    def clean_plate_text(self, text):
        """
        Cleans OCR result and keeps only letters and numbers.
        Example: MH 31 AB 1234 -> MH31AB1234
        """
        text = text.upper()
        text = re.sub(r"[^A-Z0-9]", "", text)
        return text

    def is_possible_indian_plate(self, text):
        """
        Basic Indian number plate format check.
        Example: MH31AB1234
        """
        pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{3,4}$"
        return re.match(pattern, text) is not None

    def read_plate_from_frame(self, frame):
        """
        Reads possible number plate text from a camera frame.
        Returns best plate number if found.
        """
        try:
            # Resize for OCR stability
            frame = cv2.resize(frame, (640, 480))

            # OCR on full frame
            results = self.reader.readtext(frame)

            detected_plates = []

            for bbox, text, confidence in results:
                cleaned_text = self.clean_plate_text(text)

                if len(cleaned_text) >= 6 and confidence > 0.35:
                    detected_plates.append({
                        "plate": cleaned_text,
                        "confidence": confidence
                    })

            # Prefer valid Indian plate format
            for item in detected_plates:
                if self.is_possible_indian_plate(item["plate"]):
                    return item["plate"], item["confidence"]

            # If strict format not found, return best long OCR text
            if detected_plates:
                best = max(detected_plates, key=lambda x: x["confidence"])
                return best["plate"], best["confidence"]

            return None, None

        except Exception as e:
            print("Number plate OCR error:", e)
            return None, None