import os
import re
import html
import tempfile
from fastapi import FastAPI, HTTPException
import yt_dlp
from datetime import datetime

app = FastAPI()

@app.get("/")
def home():
    return {
        "status": "Online",
        "message": "Go to /docs to test the transcript tool"
    }

# -------- CLEANING FUNCTION -------- #

def clean_vtt_text(raw: str) -> str:
    """
    Cleans WebVTT subtitle content by:
    - Removing timestamps
    - Removing HTML/cue tags
    - Removing metadata
    - Removing duplicate lines
    - Removing common caption noise
    """

    raw = html.unescape(raw)
    lines = raw.splitlines()

    cleaned_lines = []
    recent_lines = set()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Skip metadata/header lines
        if (
            line.startswith("WEBVTT")
            or line.startswith("Kind:")
            or line.startswith("Language:")
            or "-->" in line
        ):
            continue

        # Remove inline timestamps like <00:01:40.720>
        line = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", line)

        # Remove cue tags like <c>text</c> and any HTML-like tags
        line = re.sub(r"</?c[^>]*>", "", line)
        line = re.sub(r"</?[^>]+>", "", line)

        # Optional: remove caption noise
        if line.lower() in {"[music]", "[applause]", "[laughter]"}:
            continue

        # Normalize whitespace
        line = re.sub(r"\s+", " ", line).strip()

        # Remove repeated lines (common in auto captions)
        if line in recent_lines:
            continue

        cleaned_lines.append(line)
        recent_lines.add(line)

        # Keep dedupe memory small
        if len(recent_lines) > 50:
            recent_lines.pop()

    return " ".join(cleaned_lines).strip()


# -------- TRANSCRIPT ENDPOINT -------- #

@app.get("/transcript/{video_id}")
def get_transcript(video_id: str):

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:

        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "vtt",
            "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
            "quiet": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"yt-dlp error: {str(e)}"
            )

        # Find the downloaded .vtt file
        vtt_file = None
        for file in os.listdir(tmpdir):
            if file.endswith(".vtt"):
                vtt_file = os.path.join(tmpdir, file)
                break

        if not vtt_file:
            raise HTTPException(
                status_code=404,
                detail="No subtitles found for this video"
            )

        try:
            with open(vtt_file, "r", encoding="utf-8") as f:
                raw_vtt = f.read()

            cleaned_text = clean_vtt_text(raw_vtt)

            if not cleaned_text:
                raise HTTPException(
                    status_code=404,
                    detail="Subtitle file found but no readable text extracted"
                )

            return {
                "video_id": video_id,
                "text": cleaned_text
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Parsing error: {str(e)}"
            )
        
def to_iso_date(upload_date: str | None) -> str | None:
    # yt-dlp often returns upload_date like "20240211"
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

    # Build a “safe + useful” response schema
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