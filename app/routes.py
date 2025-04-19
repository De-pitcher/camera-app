from flask import Response, jsonify, send_file, request
from app.camera import generate_frames, capture_image, IMAGE_PATH
from app.utils import get_host_ip, shutdown_server
import os

def init_routes(app):

    @app.route("/video_feed")
    def video_feed():
        return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

    @app.route('/capture', methods=['POST'])
    def capture():
        success = capture_image()
        if success:
            return jsonify({"message": "Image captured", "url": f"{request.host_url}image/captured.jpg"})
        return "Capture failed", 500

    @app.route("/image", methods=["GET"])
    def get_image():
        if os.path.exists(IMAGE_PATH):
            return send_file(IMAGE_PATH, mimetype='image/jpeg', as_attachment=True, download_name='captured_image.jpg')
            # return send_from_directory(IMAGE_FOLDER, filename, mimetype='image/jpeg')
        return "No image found", 404

    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        return shutdown_server()
