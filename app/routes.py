from flask import Response, jsonify, send_file, request
import os

from app.camera import generate_frames, capture_image,shutdown_camera, shutdown_server, IMAGE_PATH

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
    
    @app.route('/shutdown-camera', methods=['POST'])
    def shutdown_camera_route():
        if shutdown_camera():
            return jsonify({"message": "Camera shut down successfully."})
        return jsonify({"message": "Camera was not active."}), 400


    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        return shutdown_server()
