import cv2
from flask import jsonify
import logging, os
import threading
import time
import atexit
from app.config import IMAGE_PATH

# Global variables
camera = None
camera_lock = threading.Lock()
active_streams = 0  # Track active video streams
shutdown_flag = False  # Global shutdown flag
last_camera_use = 0  # Timestamp of last camera activity

def init_camera():
    """Initialize camera at device 0 with default backend"""
    global camera, shutdown_flag, last_camera_use
    if shutdown_flag:
        return None

    logging.info("Initializing camera...")

    cap = cv2.VideoCapture(0, cv2.CAP_ANY)
    if cap.isOpened():
        logging.info("Camera initialized successfully at device 0")
        time.sleep(1)  # Warmup
        last_camera_use = time.time()
        return cap
    else:
        logging.error("Failed to open camera at device 0")
        cap.release()
        return None
def _ensure_camera():
    """Ensure camera is ready for use"""
    global camera, last_camera_use
    with camera_lock:
        if shutdown_flag:
            logging.warning("Shutdown requested. Not reopening camera.")
            return False

        if camera is None or not camera.isOpened():
            camera = init_camera()
        elif time.time() - last_camera_use > 5:  # Camera was idle
            camera.release()
            camera = init_camera()
    return camera is not None

def reopen_camera():
    """Explicitly allow camera usage again after shutdown"""
    global shutdown_flag
    with camera_lock:
        shutdown_flag = False
    return jsonify({"message": "Camera re-enabled."})

def generate_frames():
    """Video frame generator that properly manages camera lifecycle and auto-reopens camera if needed"""
    global active_streams, camera, last_camera_use, shutdown_flag

    active_streams += 1
    try:
        with camera_lock:
            if shutdown_flag:
                logging.info("Shutdown flag detected — attempting to reopen camera")
                shutdown_flag = False  # Allow reopening

        while True:
            if not _ensure_camera():
                logging.error("Camera unavailable for streaming")
                break

            with camera_lock:
                if shutdown_flag:
                    logging.info("Shutdown detected during streaming")
                    break

                success, frame = camera.read()
                last_camera_use = time.time()
                if not success:
                    logging.warning("Frame grab failed, resetting camera...")
                    _force_camera_reset()
                    continue

            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n\r\n')
    finally:
        active_streams -= 1
        if active_streams == 0:
            _schedule_camera_shutdown()


def capture_image():
    """Capture single image with proper camera management"""
    if not _ensure_camera():
        logging.error("Camera unavailable for capture")
        return False

    try:
        with camera_lock:
            success, frame = camera.read()
            last_camera_use = time.time()
            if success:
                cv2.imwrite(IMAGE_PATH, frame)
                logging.info(f"Image saved to {IMAGE_PATH}")
            return success
    finally:
        if active_streams == 0:
            _schedule_camera_shutdown()

def _force_camera_reset():
    """Force reset camera connection"""
    global camera, last_camera_use
    with camera_lock:
        if camera:
            camera.release()
            camera = None
        camera = init_camera()
        last_camera_use = time.time()

def _schedule_camera_shutdown():
    """Schedule camera shutdown after brief delay"""
    def delayed_shutdown():
        time.sleep(2)  # Wait 2 seconds before shutting down
        _safe_camera_shutdown()
    
    threading.Thread(target=delayed_shutdown, daemon=True).start()

def _safe_camera_shutdown():
    """Safely shutdown camera if no active streams"""
    global camera, active_streams
    with camera_lock:
        if active_streams == 0 and camera and camera.isOpened():
            logging.info("Shutting down camera with no active streams")
            camera.release()
            camera = None

def shutdown_camera():
    """Force shutdown camera regardless of active streams"""
    global camera, shutdown_flag
    with camera_lock:
        shutdown_flag = True
        if camera and camera.isOpened():
            logging.info("Force-releasing camera resources...")
            camera.release()
            camera = None
        return True

def shutdown_server():
    """Complete server shutdown"""
    shutdown_camera()
    threading.Thread(target=lambda: (time.sleep(1), os._exit(0))).start()
    return jsonify({"message": "Server shutting down..."})

# Register cleanup function
atexit.register(shutdown_camera)