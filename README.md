# Twilio Deepgram LLM Socket Streamer

## Introduction

This repository provides a synchronous socket streaming Flask server designed to handle VOIP voice agents using Twilio, Deepgram, and Anthropic APIs. The project enables seamless real-time voice communication, transcription, and advanced language model processing. It is ideal for building interactive voice-based applications, such as virtual assistants or automated customer support systems.

This feel free to use this as boilerplate for your voice agent or for studying a socket implementation in flask (using flask_sock). This is a single threaded implementation not suitable for a production environment. A production implementation shared by many users would require an async implementation. But this simpler implementation is a good steeping stone to understanding how to get an async implementation up and running.  

Key features of this project include:
- **Twilio Stream Integration:** Handles VOIP voice calls and routing.
- **Deepgram TTS / STT Stream Integration:** Provides real-time speech-to-text transcription.
- **Anthropic Text Streaming Integration:** Leverages advanced language models for natural language understanding and response generation.
- **Socket Streaming:** Ensures low-latency communication between components.

## Installation

To set up and run this project locally, follow the steps below:

### Prerequisites
- **Install UV**: Install UV Python package manager if you don't already have it: [Download UV](https://docs.astral.sh/uv/getting-started/installation/)
- **Install Ngrok**: Install Ngrok if you don't already have it: [Download Ngrok](https://ngrok.com/downloads)
- **Twilio Account**: Sign up for a Twilio account and obtain your account SID and authentication token.
- **Deepgram API Key**: Sign up for Deepgram and obtain an API key.
- **Anthropic API Key**: Obtain an API key for Anthropic's language model.

Check the .flaskenv.template for configuring up API keys.

### Steps
- Clone the repository:
   ```bash
   git clone https://github.com/smitty42/twilioDeepgramLLMSockerStreamer.git
   cd twilioDeepgramLLMSockerStreamer
   ```

- Install deps:
   ```bash
   uv sync
   ```

- Run Ngrok in a separate terminal:
    ```bash
    ngrok http 127.0.0.1:5000
    ```
    
- Setup config:
  ```bash
  cp .flaskenv.template .flaskenv
  ```

- Copy .flaskenv.template to .flaskenv and fill out envvars. This includes API keys and your ngrok link. Your Ngrok session url needs to go into .flaskenv AND into the twilio answer field for the number you're using with a suffix of `/answer`. The `/answer` suffix goes ONLY in the twilio answer hook for the twilio phone number, NOT in your .flaskenv envvars.

- Activate your env:
   ```bash
   source .venv/bin/activate

* Run the Flask server:
   ```bash
   flask run
   ```

- Now, simply call your twilio number. 
