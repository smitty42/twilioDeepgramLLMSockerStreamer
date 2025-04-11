import logging

from flask import Flask
from flask_sock import Sock

from .api_creds import TwilioManager, DeepGramManager
from config import config_manager


class AppConfig:
    def __init__(self, app=None):
        self.app = app

    def init_app(self, app):
        self.FLASK_ENV = app.config["FLASK_ENV"]


class SockConfig:
    def __init__(self, app=None):
        self.app = app

    def init_app(self, app):
        self.sock = Sock(app)


twilio_manager = TwilioManager()
deep_config = DeepGramManager()
app_config = AppConfig()
sock_config = SockConfig()


def create_app(config_name):
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_manager[config_name])
    config_manager[config_name].init_app(app)

    # Instantiate cred managers before further imports.
    twilio_manager.init_app(app)
    app_config.init_app(app)
    sock_config.init_app(app)
    deep_config.init_app(app)

    # NOTE: INFO = 20, DEBUG = 10
    logging.basicConfig(level=app.config["LOG_LEVEL"], format="%(asctime)s - %(levelname)s - %(message)s")

    # Import routes after app creation
    from .server import main_bp

    app.register_blueprint(main_bp)

    return app
