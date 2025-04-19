# app/logging_config.py
import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_folder = "app/logs"
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, "camera_server.log")

    # ✅ Safely clear log file contents without deleting (avoids WinError 32)
    open(log_file, 'w').close()

    # Create rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Create stream handler for console
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Setup root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, stream_handler]
    )

    logging.getLogger(__name__).info("Logging setup complete.")
