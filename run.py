import argparse
from app import create_app, camera
from app.utils import get_host_ip, find_available_port, monitor_parent_process
from app.logging_config import setup_logging
import threading
import os
import sys
import logging
from waitress import serve

def parse_args():
    parser = argparse.ArgumentParser(description="Start the Flask camera server.")
    parser.add_argument("--host", type=str, help="Host to run on", default=None)
    parser.add_argument("--port", type=int, help="Port to run on", default=5000)
    return parser.parse_args()

def main():
    args = parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    host = args.host or get_host_ip()
    # port = find_available_port(args.port, host)
    port = args.port

    logger.info(f"Starting server on http://{host}:{port}")
    app = create_app()

    threading.Thread(target=monitor_parent_process, daemon=True).start()

    try:
        serve(app, host=host, port=port)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        camera.release()
        sys.exit(1)

if __name__ == "__main__":
    main()