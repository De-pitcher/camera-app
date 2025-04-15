import cv2

def start_camera():
    # Open the default camera (usually the first one)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    print("📷 Press SPACE to capture, ESC to exit")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("❌ Can't receive frame (stream end?). Exiting ...")
            break

        # Display the live video feed
        cv2.imshow('Live Camera Feed', frame)

        key = cv2.waitKey(1)

        if key % 256 == 27:  # ESC key
            print("🚪 Exiting...")
            break
        elif key % 256 == 32:  # SPACE key
            # Save the captured image
            cv2.imwrite("captured_image.png", frame)
            print("✅ Image captured and saved as captured_image.png")

    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_camera()
