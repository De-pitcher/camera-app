# Camera Server Application

A Flask-based web server that provides live video feed and image capture functionality from a connected camera.

## Features

- Live video streaming via `/video_feed` endpoint
- Image capture via `/capture` endpoint (POST request)
- Download latest captured image via `/image` endpoint
- Health check endpoint at `/health`
- Graceful shutdown via `/shutdown` endpoint
- Automatic IP detection or manual host/port configuration
- Cross-platform compatibility (works with PyInstaller)

## Prerequisites

- Python 3.7+
- Virtual environment (recommended)
- Camera connected to your system

## Setup

1. Clone this repository or copy the `camera_server.py` file to your project directory.

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
.\venv\Scripts\activate   # Windows
```

3. Install the required dependencies:

```bash
pip install flask opencv-python waitress requests
```

## Running the Server

### Basic Usage
```bash
python camera_server.py
```

### With Custom Host/Port
```bash
python camera_server.py --host 0.0.0.0 --port 8080
```

### Production Deployment (using Waitress)
The server already uses Waitress (a production WSGI server) by default.

## Endpoints

- `GET /video_feed` - Live video stream (MJPEG)
- `POST /capture` - Capture and save an image
- `GET /image` - Download the latest captured image
- `GET /health` - Health check endpoint
- `POST /shutdown` - Gracefully shutdown the server

## Compiling with PyInstaller

To create a standalone executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Compile the application:
```bash
pyinstaller --onefile --add-data "images;images" camera_server.py
```

3. The executable will be in the `dist` folder. Run it with:
```bash
./dist/camera_server
```

## Configuration

- The server automatically creates an `images` directory to store captured images
- Default port is 5000
- Host IP is auto-detected (can be overridden with `--host` argument)

## Troubleshooting

- If the camera isn't working, verify it's properly connected
- Make sure no other application is using the camera
- Check firewall settings if accessing from another machine
- For port conflicts, try a different port with `--port`

## License

[MIT License](LICENSE)
