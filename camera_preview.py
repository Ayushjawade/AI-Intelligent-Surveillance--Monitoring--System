import cv2

for index in range(6):
    cap = cv2.VideoCapture(index)

    if not cap.isOpened():
        print(f"Camera {index}: Not available")
        continue

    print(f"Opening Camera {index}. Press Q to close.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print(f"Cannot read camera {index}")
            break

        cv2.putText(
            frame,
            f"Camera Index: {index}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow(f"Camera Index {index}", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()