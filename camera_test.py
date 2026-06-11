import cv2

for i in range(6):
    cap = cv2.VideoCapture(i)

    if cap.isOpened():
        print(f"Camera Index {i}: Available")
    else:
        print(f"Camera Index {i}: Not Available")

    cap.release()