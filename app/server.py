import time
import wave
import audioop
import json
import base64
from urllib.parse import urlparse

import pyaudio
from flask import Blueprint
from twilio.twiml.voice_response import VoiceResponse, Connect
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveOptions,
    LiveTranscriptionEvents,
    SpeakWebSocketEvents,
    SpeakWSOptions,
)

from app import sock_config, deep_config, config_manager, app_config

from .anthropic_api import AnthropicLLMConversation


main_bp = Blueprint("main", __name__)


@main_bp.route("/answer", methods=["POST"])
def answer():
    stream_url = f"wss://{urlparse(config_manager[app_config.FLASK_ENV].NGROK).netloc}/stream"
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=stream_url)
    response.append(connect)
    return str(response), 200, {"Content-Type": "text/xml"}


# NOTE Endpoint for twilio bidirectional stream.
@sock_config.sock.route("/stream")
def stream(ws):
    media_stream = MediaStream(ws)

    # NOTE: Start the conversation.
    prompt_llm(media_stream, "Hello")

    while ws.connected:
        message = ws.receive()
        media_stream.process_message(message)


class MediaStream:
    def __init__(self, twilio_ws):
        self.twilio_ws = twilio_ws
        self.deepgram_stt_socket, options = deepgram_stt_socket(self)
        self.deepgram_stt_socket.start(options)
        self.deepgram_tts_socket = deepgram_tts_socket(self)
        self.has_seen_media = False
        self.messages = []
        self.repeat_count = 0
        self.stream_sid = None
        self.conversation_history = []

    def process_message(self, message):
        data = json.loads(message)
        if data["event"] == "connected":
            print("twilio: Connected event received:", data)
        elif data["event"] == "start":
            print("twilio: Start event received:", data)
        elif data["event"] == "media":
            if not self.stream_sid:
                self.stream_sid = data["streamSid"]
                print("twilio: streamSid=", self.stream_sid)

            if data["media"]["track"] == "inbound":
                raw_audio = base64.b64decode(data["media"]["payload"])
                self.deepgram_stt_socket.send(raw_audio)
        elif data["event"] == "mark":
            print("twilio: Mark event received", data)
        elif data["event"] == "close":
            print("twilio: Close event received:", data)
            self.close()
        elif data["event"] == "stop":
            print("stopped by Twilio...")
        else:
            print(data["event"])
            print(f"not handeled: {data}")

    def close(self):
        print("twilio: Closed")


def deepgram_stt_socket(media_stream):
    config = DeepgramClientOptions(
        options={"keepalive": "true", "termination_exception": True, "termination_exception_connect": True},
        # verbose=verboselogs.DEBUG
    )
    deepgram = DeepgramClient(deep_config.deep_gram_api_key, config)
    options = LiveOptions(
        model="nova-3",
        punctuate=True,
        language="en-US",
        encoding="mulaw",
        channels=1,
        sample_rate=8000,
        ## To get UtteranceEnd, the following must be set:
        interim_results=True,
        utterance_end_ms="1000",
        vad_events=True,
    )

    def on_open(self, open, **kwargs):
        print(f"\n\n{open}\n\n")

    def on_message(self, result, **kwargs):
        sentence = result.channel.alternatives[0].transcript
        if len(sentence) == 0:
            return
        print(f"speaker: {sentence}")

    def on_metadata(self, metadata, **kwargs):
        print(f"\n\n{metadata}\n\n")

    def on_speech_started(self, speech_started, **kwargs):
        print(f"\n\n{speech_started}\n\n")

    def on_utterance_end(self, utterance_end, **kwargs):
        print(f"\n\n{utterance_end}\n\n")

    def on_error(self, error, **kwargs):
        print(f"\n\n{error}\n\n")

    def on_close(self, close, **kwargs):
        print(f"\n\n{close}\n\n")

    def handle_transcript(self, result):
        nonlocal media_stream

        transcript = result.channel.alternatives[0].transcript
        if transcript:
            if result.is_final:
                print(f"deepgram STT: [Speech Final] {transcript}")
                prompt_llm(media_stream, transcript)
            else:
                print(f"interupting... \ndeepgram STT: [Interim Result] {transcript}")
                if media_stream.speaking:
                    clear_audio_playback(media_stream)

    dg_connection = deepgram.listen.websocket.v("1")

    dg_connection.on(LiveTranscriptionEvents.Open, on_open)
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
    dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
    dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)
    dg_connection.on(LiveTranscriptionEvents.Close, on_close)
    dg_connection.on(LiveTranscriptionEvents.Transcript, handle_transcript)
    return dg_connection, options


def deepgram_tts_socket(media_stream):
    config = DeepgramClientOptions(
        options={
            "keepalive": "true",
            "termination_exception": True,
            "termination_exception_connect": True,
            "speaker_playback": True,
        },
        # verbose=verboselogs.DEBUG
    )
    deepgram = DeepgramClient(deep_config.deep_gram_api_key, config)
    dg_connection = deepgram.speak.websocket.v("1")
    # file_out = wave.open("test.wav", "wb")
    # file_out.setnchannels(1)
    # file_out.setframerate(8000)
    # file_out.setsampwidth(2)

    def on_open(self, open, **kwargs):
        print(f"\n\n{open}\n\n")

    def on_binary_data(self, data, **kwargs):
        nonlocal media_stream
        # nonlocal file_out

        twilio_packet = json.dumps(
            {
                "event": "media",
                "streamSid": media_stream.stream_sid,
                "media": {"payload": str(base64.b64encode(data).decode())},
            }
        )
        media_stream.twilio_ws.send(twilio_packet)
        # file_out.writeframesraw(audioop.ulaw2lin(data, 2))

    def on_metadata(self, metadata, **kwargs):
        print(f"\n\n{metadata}\n\n")

    def on_flush(self, flushed, **kwargs):
        print(f"\n\n{flushed}\n\n")

    def on_clear(self, clear, **kwargs):
        print(f"\n\n{clear}\n\n")

    def on_close(self, close, **kwargs):
        print(f"\n\n{close}\n\n")

    def on_warning(self, warning, **kwargs):
        print(f"\n\n{warning}\n\n")

    def on_error(self, error, **kwargs):
        print(f"\n\n{error}\n\n")

    def on_unhandled(self, unhandled, **kwargs):
        print(f"\n\n{unhandled}\n\n")

    dg_connection.on(SpeakWebSocketEvents.Open, on_open)
    dg_connection.on(SpeakWebSocketEvents.AudioData, on_binary_data)
    dg_connection.on(SpeakWebSocketEvents.Metadata, on_metadata)
    dg_connection.on(SpeakWebSocketEvents.Flushed, on_flush)
    dg_connection.on(SpeakWebSocketEvents.Cleared, on_clear)
    dg_connection.on(SpeakWebSocketEvents.Close, on_close)
    dg_connection.on(SpeakWebSocketEvents.Error, on_error)
    dg_connection.on(SpeakWebSocketEvents.Warning, on_warning)
    dg_connection.on(SpeakWebSocketEvents.Unhandled, on_unhandled)

    # connect to websocket
    options = SpeakWSOptions(
        model="aura-asteria-en",
        encoding="mulaw",
        sample_rate=8000,
    )

    if dg_connection.start(options) is False:
        print("Failed to start connection")
        return

    return dg_connection


def prompt_llm(media_stream, prompt):
    llm = AnthropicLLMConversation("dummy number", "dummy sid")
    response = llm.query_model(user_prompt=prompt, conversation_history=media_stream.conversation_history)
    media_stream.speaking = True
    mega_chunk = ""
    for chunk in response:
        chunk = chunk.to_dict()
        if "delta" in chunk:
            if "text" in chunk["delta"]:
                mega_chunk += chunk["delta"]["text"]

    print(f"LLM Response: {mega_chunk}")
    media_stream.conversation_history.append({"role": "assistant", "content": [{"type": "text", "text": mega_chunk}]})
    media_stream.deepgram_tts_socket.send_text(mega_chunk)
    media_stream.deepgram_tts_socket.flush()


def clear_audio_playback(media_stream):
    print("twilio: clear audio playback", media_stream.stream_sid)

    media_stream.twilio_ws.send(json.dumps({"event": "clear", "streamSid": media_stream.stream_sid}))
    # media_stream.deepgram_tts_socket.send("")
    media_stream.speaking = False
