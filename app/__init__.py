from flask import Flask
from app.routes import init_routes
from app.camera import init_camera

def create_app():
    app = Flask(__name__)
    app.debug = True
    init_camera()
    init_routes(app)
    return app
