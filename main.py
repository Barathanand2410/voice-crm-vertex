import functions_framework
from flask import request, jsonify
import os
from google.cloud import storage
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import uuid

vertexai.init(project="cs-poc-jtpmh5tnmdhxxb0ry5j7ljm", location="asia-south1")

BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "voice-crm-audio")

@functions_framework.http
def speak(request):
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Missing 'text' in request"}), 400

        # Use PaLM to generate TTS-style response
        model = GenerativeModel("gemini-1.5-flash-preview-0514")
        response = model.generate_content(
            f"Convert the following text into a short speech audio in SSML format only:\n\n{text}"
        )

        ssml = response.text

        # Wrap in a <speak> tag if not already
        if "<speak>" not in ssml:
            ssml = f"<speak>{ssml}</speak>"

        from google.cloud import texttospeech

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Wavenet-D"
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio_bytes = response.audio_content

        # Upload to GCS
        audio_filename = f"audio_{uuid.uuid4().hex}.mp3"
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(audio_filename)
        blob.upload_from_string(audio_bytes, content_type="audio/mpeg")
        blob.make_public()

        return jsonify({
            "message": "Audio generated and stored",
            "audio_url": blob.public_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
