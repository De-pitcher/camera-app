from flask import Flask, Response, jsonify, send_file, send_from_directory
import atexit
import signal
import os
import cv2
import threading
import time
import socket
import sys
import argparse
import requests
import psutil
from requests.exceptions import RequestException
import socket
from urllib.request import urlopen
import json
from urllib.error import URLError

import logging
from logging.handlers import RotatingFileHandler


# Determine the correct base path (works for both script and PyInstaller)
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)  # Use the executable's directory
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Define the images folder path
IMAGE_FOLDER = os.path.join(base_path, 'images')
os.makedirs(IMAGE_FOLDER, exist_ok=True)  # Creates folder if it doesn't exist

IMAGE_FILENAME = "captured.jpg"
IMAGE_PATH = os.path.join(IMAGE_FOLDER, IMAGE_FILENAME)


# Setup logging
LOG_FILE = os.path.join(base_path, "camera_server.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


app = Flask(__name__)
camera = cv2.VideoCapture(0)

# Directory where image will be saved


def get_host_ip():
    try:
        # Try to connect to a dummy external IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run the camera server')
    parser.add_argument('--host', type=str, default=None,
                       help='Host IP to run the server on (default: auto-detect local IP)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to run the server on (default: 5000)')
    return parser.parse_args()

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/capture', methods=['POST'])
def capture():
    success, frame = camera.read()
    if success:
        cv2.imwrite(IMAGE_PATH, frame)
        LOCAL_IP = get_host_ip()
        return jsonify({"message": "Image captured", 'url': f"http://{LOCAL_IP}:5000/image/captured.jpg"}) 
    else:
        return 'Capture failed', 500

@app.route("/image", methods=["GET"])
def get_image():
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype='image/jpeg', as_attachment=True, download_name='captured_image.jpg')
    return "No image found", 404


@app.route('/shutdown', methods=['POST'])
def shutdown():
    logger.info("Shutting down...")
    camera.release()
    threading.Thread(target=lambda: (time.sleep(1), os._exit(0))).start()
    return 'Server shutting down...'

# Add this new endpoint to your Flask server
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

def cleanup():
    """Release resources and clean up"""
    logger.info("Performing cleanup...")
    if camera.isOpened():
        camera.release()
    # Add any other cleanup needed here

def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"\nReceived shutdown signal {signum}, exiting gracefully...")
    cleanup()
    sys.exit(0)

def monitor_parent_process():
    """Shut down server if parent process exits."""
    try:
        parent = psutil.Process(os.getppid())
        while True:
            if not parent.is_running():
                logger.info("Parent process exited. Shutting down server...")
                cleanup()
                os._exit(0)
            time.sleep(5)
    except Exception as e:
        logger.error(f"Parent monitoring failed: {e}")

def find_available_port(start_port, host):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                s.close()
                return port
            except OSError:
                logger.warning(f"Port {port} is in use, trying next...")
                port += 1


# Register cleanup handlers
atexit.register(cleanup)
signal.signal(signal.SIGINT, handle_shutdown)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_shutdown)  # Termination signal

if __name__ == "__main__":
    args = parse_arguments()
    # ip_info = get_ip_addresses()
    host = args.host if args.host is not None else get_host_ip()
    port = find_available_port(args.port, host)

    logger.info(f"Server starting on http://{host}:{port}")
    logger.info(f"Video feed available at http://{host}:{port}/video_feed")

    # Start parent process monitoring in the background
    threading.Thread(target=monitor_parent_process, daemon=True).start()

    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    try:
        logger.info(f"Starting server on http://{host}:{port}")
        from waitress import serve
        serve(app, host=host, port=port)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        cleanup()
        sys.exit(1)
