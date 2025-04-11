import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".flaskenv"))


class Config(object):
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    FLASK_ENV = os.environ.get("FLASK_CONFIG")
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")
    LOG_LEVEL = int(os.environ.get("LOG_LEVEL", 20))
    NGROK = os.environ.get("NGROK")


class TestingConfig(Config):
    TESTING = True
    FLASK_ENV = "test"
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")
    LOG_LEVEL = int(os.environ.get("LOG_LEVEL", 20))


class ProductionConfig(Config):
    FLASK_ENV = os.environ.get("FLASK_CONFIG")
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")
    LOG_LEVEL = int(os.environ.get("LOG_LEVEL", 20))


config_manager = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig,
}
