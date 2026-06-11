from ultralytics import YOLO
import cv2

model = YOLO("runs/detect/train-14/weights/best.pt")

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Camera not working")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    results = model(frame)

    annotated_frame = results[0].plot()

    cv2.imshow("AI Surveillance System", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()