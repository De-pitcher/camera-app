import cv2
from flask import jsonify
import logging, threading, time, os

from app.config import IMAGE_PATH

camera = None

def init_camera():
    global camera
    camera = cv2.VideoCapture(0)

def generate_frames():
    global camera

    if camera is None or not camera.isOpened():
        logging.info("Camera not initialized or closed. Reinitializing...")
        init_camera()

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

def shutdown_camera():
    global camera
    if camera and camera.isOpened():
        logging.info("Releasing camera resource...")
        camera.release()
        camera = None
        return True
    return False

def shutdown_server():
    if camera and camera.isOpened():
        logging.info("Shutting down...")
        camera.release()
    # Use a new thread to delay and exit the process completely
    threading.Thread(target=lambda: (time.sleep(1), os._exit(0))).start()
    return jsonify({"message": "Server shutting down..."})