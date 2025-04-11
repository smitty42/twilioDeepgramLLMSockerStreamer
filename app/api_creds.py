from twilio.rest import Client


class TwilioManager:
    def __init__(self, app=None):
        self.app = app

    def init_app(self, app):
        self.twilio_account_sid = app.config["TWILIO_ACCOUNT_SID"]
        self.twilio_auth_token = app.config["TWILIO_AUTH_TOKEN"]
        self.client = Client(self.twilio_account_sid, self.twilio_auth_token)


class DeepGramManager:
    def __init__(self, app=None):
        self.app = app

    def init_app(self, app):
        self.deep_gram_api_key = app.config["DEEPGRAM_API_KEY"]
