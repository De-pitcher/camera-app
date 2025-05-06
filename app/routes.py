# from flask import Response, jsonify, send_file, request
# import os

# from app.camera import generate_frames, capture_image,shutdown_camera, shutdown_server, IMAGE_PATH

# def init_routes(app):

#     @app.route("/video_feed")
#     def video_feed():
#         return Response(generate_frames(), content_type="multipart/x-mixed-replace;boundary=frame")

#     @app.route('/capture', methods=['POST'])
#     def capture():
#         success = capture_image()
#         if success:
#             return jsonify({"message": "Image captured", "url": f"{request.host_url}image/captured.jpg"})
#         return "Capture failed", 500

#     @app.route("/image", methods=["GET"])
#     def get_image():
#         if os.path.exists(IMAGE_PATH):
#             return send_file(IMAGE_PATH, mimetype='image/jpeg', as_attachment=True, download_name='captured_image.jpg')
#             # return send_from_directory(IMAGE_FOLDER, filename, mimetype='image/jpeg')
#         return "No image found", 404

#     @app.route('/health')
#     def health():
#         return {'status': 'healthy'}, 200
    
#     @app.route('/shutdown-camera', methods=['POST'])
#     def shutdown_camera_route():
#         if shutdown_camera():
#             return jsonify({"message": "Camera shut down successfully."})
#         return jsonify({"message": "Camera was not active."}), 400


#     @app.route('/shutdown', methods=['POST'])
#     def shutdown():
#         return shutdown_server()

from flask import Response, jsonify, send_file, request
import os
import tempfile
import time
import logging
import concurrent.futures
import atexit
from werkzeug.exceptions import HTTPException

from app.camera import (
    generate_frames,
    capture_image,
    shutdown_camera,
    shutdown_server,
    IMAGE_PATH,
)

# 🔧 Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ ThreadPoolExecutor for background cleanup
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
atexit.register(executor.shutdown)
atexit.register(lambda: executor.shutdown(wait=False, cancel_futures=True))

# ✅ Actual cleanup function
def cleanup_opencv_temp_files():
    temp_dir = os.environ.get('TEMP') or tempfile.gettempdir()
    now = time.time()
    for fname in os.listdir(temp_dir):
        if fname.lower().startswith('opencv') or fname.lower().endswith(('.dll', '.bin')):
            path = os.path.join(temp_dir, fname)
            if os.path.isfile(path):
                try:
                    if now - os.path.getmtime(path) > 300:  # older than 5 min
                        os.remove(path)
                        logger.info(f"Deleted old OpenCV temp file: {path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temp file {path}: {e}")

# ✅ Non-blocking background scheduler
def schedule_cleanup():
    executor.submit(cleanup_opencv_temp_files)

# ✅ Route registration
def init_routes(app):

    @app.route("/video_feed")
    def video_feed():
        try:
            schedule_cleanup()
            return Response(generate_frames(), content_type="multipart/x-mixed-replace;boundary=frame")
        except Exception as e:
            logger.error(f"Error in /video_feed: {e}", exc_info=True)
            return "Streaming error", 500

    @app.route('/capture', methods=['POST'])
    def capture():
        try:
            schedule_cleanup()
            success = capture_image()
            if success:
                return jsonify({"message": "Image captured", "url": f"{request.host_url}image/captured.jpg"})
            return "Capture failed", 500
        except Exception as e:
            logger.error(f"Error in /capture: {e}", exc_info=True)
            return "Capture error", 500

    @app.route("/image", methods=["GET"])
    def get_image():
        try:
            if os.path.exists(IMAGE_PATH):
                return send_file(IMAGE_PATH, mimetype='image/jpeg', as_attachment=True, download_name='captured_image.jpg')
            return "No image found", 404
        except Exception as e:
            logger.error(f"Error in /image: {e}", exc_info=True)
            return "Failed to retrieve image", 500

    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    @app.route('/shutdown-camera', methods=['POST'])
    def shutdown_camera_route():
        try:
            schedule_cleanup()
            if shutdown_camera():
                return jsonify({"message": "Camera shut down successfully."})
            return jsonify({"message": "Camera was not active."}), 400
        except Exception as e:
            logger.error(f"Error in /shutdown-camera: {e}", exc_info=True)
            return "Shutdown camera error", 500

    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        try:
            return shutdown_server()
        except Exception as e:
            logger.error(f"Error in /shutdown: {e}", exc_info=True)
            return "Server shutdown failed", 500

    # 🌐 Global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({"error": e.description}), e.code
        logger.exception("Unhandled exception")
        return jsonify({"error": "Internal server error"}), 500
