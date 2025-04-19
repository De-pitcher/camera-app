# Flask Camera App

A simple Flask app for video streaming and image capture using OpenCV.

## Features

- Live video feed
- Capture image and download
- Health check
- Shutdown endpoint

## Getting Started

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the server

```bash
python run.py
```

### Endpoints

- `/video_feed` – Live stream
- `/capture` – Capture an image (POST)
- `/image` – Download the last captured image
- `/health` – Health check
- `/shutdown` – Graceful shutdown
