import os
import sys

BASE_PATH = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_PATH, 'images')
os.makedirs(IMAGE_FOLDER, exist_ok=True)

IMAGE_FILENAME = "captured.jpg"
IMAGE_PATH = os.path.join(IMAGE_FOLDER, IMAGE_FILENAME)
