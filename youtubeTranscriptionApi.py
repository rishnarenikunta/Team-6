import os
import re
import html
import tempfile
from fastapi import FastAPI, HTTPException
import yt_dlp
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import json
from google.cloud import storage
import subprocess
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

BUCKET_NAME = "youtravel_transcripts"
storage_client = storage.Client()

def upload_transcript_to_gcs(video_id: str, transcript_text: str) -> str:
    bucket = storage_client.bucket(BUCKET_NAME)

    blob_path = f"transcripts/{video_id}.json"
    blob = bucket.blob(blob_path)

    payload = {
        "video_id": video_id,
        "text": transcript_text,
    }

    blob.upload_from_string(
        json.dumps(payload, ensure_ascii=False),
        content_type="application/json",
    )

    return f"gs://{BUCKET_NAME}/{blob_path}"

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "travel_app")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "videos")

mongo_client = MongoClient(MONGODB_URI) if MONGODB_URI else None
videos_col = mongo_client[MONGODB_DB][MONGODB_COLLECTION] if mongo_client else None

@app.get("/")
def home():
    return {
        "status": "Online",
        "message": "Go to /docs to test the transcript tool"
    }

def clean_vtt_text(raw: str) -> str:

    raw = html.unescape(raw)
    lines = raw.splitlines()

    cleaned_lines = []
    recent_lines = set()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if (
            line.startswith("WEBVTT")
            or line.startswith("Kind:")
            or line.startswith("Language:")
            or "-->" in line
        ):
            continue

        line = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", line)

        line = re.sub(r"</?c[^>]*>", "", line)
        line = re.sub(r"</?[^>]+>", "", line)

        if line.lower() in {"[music]", "[applause]", "[laughter]"}:
            continue

        line = re.sub(r"\s+", " ", line).strip()

        if line in recent_lines:
            continue

        cleaned_lines.append(line)
        recent_lines.add(line)


    return " ".join(cleaned_lines).strip()


@app.get("/transcript/{video_id}")
def get_transcript(video_id: str):

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:

        def run_ytdlp(write_manual: bool, write_auto: bool):
            ydl_opts = {
                "skip_download": True,
                "writesubtitles": write_manual,
                "writeautomaticsub": write_auto,
                "subtitleslangs": ["en"],
                "subtitlesformat": "vtt",
                "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
                "quiet": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

        try:
            # Prefer manual captions
            run_ytdlp(write_manual=True, write_auto=False)

            vtt_files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".vtt")]

            # Fallback to auto captions
            if not vtt_files:
                run_ytdlp(write_manual=False, write_auto=True)
                vtt_files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".vtt")]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"yt-dlp error: {str(e)}")

        if not vtt_files:
            raise HTTPException(status_code=404, detail="No subtitles found for this video")

        vtt_file = max(vtt_files, key=lambda p: os.path.getsize(p))

        try:
            with open(vtt_file, "r", encoding="utf-8") as f:
                raw_vtt = f.read()

            cleaned_text = clean_vtt_text(raw_vtt)
            if not cleaned_text:
                raise HTTPException(status_code=404, detail="Subtitle file found but no readable text extracted")

            gcs_path = upload_transcript_to_gcs(video_id, cleaned_text)

            return {
                "video_id": video_id,
                "gcs_path": gcs_path,
                "text": cleaned_text
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
        
def to_iso_date(upload_date: str | None) -> str | None:

    if not upload_date:
        return None
    try:
        return datetime.strptime(upload_date, "%Y%m%d").date().isoformat()
    except Exception:
        return None

@app.get("/metadata/{video_id}")
def get_metadata(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"yt-dlp metadata error: {str(e)}")

    return {
        "video_id": info.get("id"),
        "title": info.get("title"),
        "description": info.get("description"),
        "channel": {
            "name": info.get("uploader"),
            "id": info.get("uploader_id"),
            "channel_id": info.get("channel_id"),
            "channel_url": info.get("channel_url"),
        },
        "webpage_url": info.get("webpage_url"),
        "duration_seconds": info.get("duration"),
        "upload_date": to_iso_date(info.get("upload_date")),
        "stats": {
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "comment_count": info.get("comment_count"),
        },
        "tags": info.get("tags") or [],
        "categories": info.get("categories") or [],
        "language": info.get("language"),
    }

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class YouTubeRequest(BaseModel):
    video_id: str
    model: str = "gpt-4o-mini-transcribe"

@app.post("/transcribe/youtube")
def transcribe_youtube(req: YouTubeRequest):
    if not client.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    video_url = f"https://www.youtube.com/watch?v={req.video_id}"

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            outtmpl = os.path.join(tmpdir, "audio.%(ext)s")

            # 1) Download audio stream only (NO conversion, NO ffmpeg)
            cmd = [
                "python", "-m", "yt_dlp",
                "-f", "bestaudio[ext=m4a]/bestaudio",
                "-o", outtmpl,
                video_url,
            ]

            proc = subprocess.run(cmd, capture_output=True, text=True)

            if proc.returncode != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"yt-dlp failed: {proc.stderr.strip() or proc.stdout.strip()}",
                )

            # 2) Locate downloaded audio file
            audio_file = next(
                f for f in os.listdir(tmpdir) if f.startswith("audio.")
            )
            audio_path = os.path.join(tmpdir, audio_file)

            # 3) Read audio bytes
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            # 4) Transcribe with OpenAI / Whisper
            result = client.audio.transcriptions.create(
                model=req.model,
                file=(audio_file, audio_bytes),
            )

            return {
                "video_id": req.video_id,
                "text": result.text,
            }

    except StopIteration:
        raise HTTPException(status_code=400, detail="Audio file not found after download")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))