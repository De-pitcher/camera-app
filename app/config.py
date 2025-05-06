import os
import sys

# Determine base directory based on OS
if sys.platform == "win32":
    base_dir = os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
else:
    base_dir = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))

BASE_PATH = os.path.join(base_dir, "ClockInApp")
IMAGE_FOLDER = os.path.join(BASE_PATH, "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

IMAGE_FILENAME = "captured.jpg"
IMAGE_PATH = os.path.join(IMAGE_FOLDER, IMAGE_FILENAME)
