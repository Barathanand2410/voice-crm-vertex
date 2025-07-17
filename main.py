from fastapi import FastAPI, HTTPException
from google.cloud import storage
from datetime import timedelta
import os

app = FastAPI()

@app.get("/generate-signed-url")
def generate_signed_url(bucket_name: str, blob_name: str, expiration_minutes: int = 15):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
        )
        return {"signed_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
