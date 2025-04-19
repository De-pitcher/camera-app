# app/logging_config.py
import logging
import sys, os
from logging.handlers import RotatingFileHandler

# def setup_logging():
#     if not logging.getLogger().hasHandlers():
#         # Only setup logging if there are no handlers yet
#         log_path = os.path.join("logs", "camera_server.log")
#         os.makedirs("logs", exist_ok=True)

#         handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3)
#         handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

#         stream_handler = logging.StreamHandler(sys.stdout)

#         logging.basicConfig(
#             level=logging.INFO,
#             handlers=[handler, stream_handler]
#         )
def setup_logging():
    log_folder = "app/logs"  # Adjust the folder where logs are stored
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, "camera_server.log")

    # Check if the log file exists and remove it to clear content on app start
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Create a rotating file handler that writes to the log file
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Create a stream handler that writes to the console (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    
    # Set up the root logger to use both handlers
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, stream_handler]
    )
    
    # Check if the logger works
    logger = logging.getLogger(__name__)
    logger.info("Logging setup complete.")