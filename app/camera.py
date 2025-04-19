import cv2
import os
from app.config import IMAGE_PATH

camera = None

def init_camera():
    global camera
    camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def capture_image():
    success, frame = camera.read()
    if success:
        cv2.imwrite(IMAGE_PATH, frame)
    return success
