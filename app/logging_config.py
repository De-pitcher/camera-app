# # app/logging_config.py
# import logging
# import sys
# import os
# from logging.handlers import RotatingFileHandler

# def setup_logging():
#     log_folder = "app/logs"
#     os.makedirs(log_folder, exist_ok=True)
#     log_file = os.path.join(log_folder, "camera_server.log")

#     # ✅ Safely clear log file contents without deleting (avoids WinError 32)
#     open(log_file, 'w').close()

#     # Create rotating file handler
#     file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
#     file_handler.setLevel(logging.INFO)
#     file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

#     # Create stream handler for console
#     stream_handler = logging.StreamHandler(sys.stdout)
#     stream_handler.setLevel(logging.INFO)
#     stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

#     # Setup root logger
#     logging.basicConfig(
#         level=logging.INFO,
#         handlers=[file_handler, stream_handler]
#     )

#     logging.getLogger(__name__).info("Logging setup complete.")

# app/logging_config.py
import logging
import sys
import os
import io
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
    # Ensure stdout uses UTF-8 to support Unicode output (e.g., emojis)
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # Use a user-writable directory for logs
    if sys.platform == "win32":
        base_log_dir = os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    elif sys.platform == "darwin":
        base_log_dir = os.path.expanduser("~/Library/Logs")
    else:
        base_log_dir = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))

    log_folder = os.path.join(base_log_dir, "ClockInApp", "logs")
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, "camera_server.log")

    # Optional: clear previous log contents
    open(log_file, 'w', encoding='utf-8').close()

    # Get the root logger and clear existing handlers
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # File handler with UTF-8 encoding
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(file_formatter)
    logger.addHandler(stream_handler)

    logger.info("Logging setup complete.")
    logger.info(f"Logs are being written to: {log_file}")
