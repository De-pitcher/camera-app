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
from requests.exceptions import RequestException
import socket
from urllib.request import urlopen
import json
from urllib.error import URLError

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

# @app.route('/image/<filename>')
# def get_image(filename):
#     return send_from_directory(IMAGE_FOLDER, filename)
@app.route("/image", methods=["GET"])
def get_image():
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype='image/jpeg', as_attachment=True, download_name='captured_image.jpg')
    return "No image found", 404


@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("Shutting down...")
    camera.release()
    threading.Thread(target=lambda: (time.sleep(1), os._exit(0))).start()
    return 'Server shutting down...'

# Add this new endpoint to your Flask server
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

def cleanup():
    """Release resources and clean up"""
    print("Performing cleanup...")
    if camera.isOpened():
        camera.release()
    # Add any other cleanup needed here

def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    print(f"\nReceived shutdown signal {signum}, exiting gracefully...")
    cleanup()
    sys.exit(0)

# Register cleanup handlers
atexit.register(cleanup)
signal.signal(signal.SIGINT, handle_shutdown)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_shutdown)  # Termination signal

if __name__ == "__main__":
    args = parse_arguments()
    # ip_info = get_ip_addresses()
    host = args.host if args.host is not None else get_host_ip()
    port = args.port

    print(f"Server starting on http://{host}:{port}")
    print(f"Video feed available at http://{host}:{port}/video_feed")

    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    try:
        print(f"Starting server on http://{host}:{port}")
        from waitress import serve
        serve(app, host=host, port=port)
    except Exception as e:
        print(f"Server error: {str(e)}")
        cleanup()
        sys.exit(1)
