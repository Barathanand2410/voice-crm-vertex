from fastapi import FastAPI, Request
from tts_vertex import synthesize_text
import uuid
import os

app = FastAPI()

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

@app.post("/speak")
async def speak(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        return {"error": "Missing 'text' field"}

    audio_url = synthesize_text(text, GCS_BUCKET_NAME)
    return {"audio_url": audio_url}