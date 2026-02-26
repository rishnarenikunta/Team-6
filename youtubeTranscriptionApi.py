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
# from google.cloud import storage
import subprocess
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# BUCKET_NAME = "youtravel_transcripts"
# storage_client = storage.Client()

TRAVEL_KEYWORDS = [
    "travel", "trip", "tour", "itinerary", "vacation",
    "explore", "exploring",
    "city", "country", "island", "beach", "mountain",
    "airport", "flight", "train",
    "hotel", "hostel",
    "vlog"
]

def is_travel_video(info: dict) -> bool:
    text = (
        (info.get("title") or "") + " " +
        (info.get("description") or "")
    ).lower()

    for word in TRAVEL_KEYWORDS:
        if word in text:
            return True

    return False


CHANNEL_BUCKETS: dict[str, list[str]] = {
    "Travel": [
        "https://www.youtube.com/@fearlessandfar/videos",
        "https://www.youtube.com/@drewbinsky/videos",
    ],
    "Food": [
        "https://www.youtube.com/@FoodNetwork/videos",
        "https://www.youtube.com/@buzzfeedtasty/videos",
    ],
    "Lifestyle/Vlog": [
        "https://www.youtube.com/@emmachamberlain/videos",
        "https://www.youtube.com/@casey/videos",
    ],
    "Wellness": [
        "https://www.youtube.com/@bohobeautiful/videos",
        "https://www.youtube.com/@WildWeRoam/videos",
    ],
    "Tech": [
        "https://www.youtube.com/@iJustine/videos",
        "https://www.youtube.com/@OneTechTraveller/videos",
    ],
    "Entertainment": [
        "https://www.youtube.com/@Vogue/videos",
        "https://www.youtube.com/@ELLE/videos",
    ],
    "News": [
        "https://www.youtube.com/@NBCNews/videos",
        "https://www.youtube.com/@CNN/videos",
    ],
}

NON_TRAVEL_BUCKETS = {"Food", "Lifestyle/Vlog", "Tech", "Entertainment", "News", "Wellness"}

DEFAULT_WEIGHTS = {
    "views": 0.34,
    "likes": 0.33,
    "comments": 0.33,
}

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

def safe_int(x) -> int:
    try:
        return int(x) if x is not None else 0
    except Exception:
        return 0


def fetch_channel_top_videos(
    channel_url: str,
    limit: int,
    w_views: float,
    w_likes: float,
    w_comments: float,
) -> list[dict]:

    flat_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "playlistend": limit, 
    }

    with yt_dlp.YoutubeDL(flat_opts) as ydl:
        flat_info = ydl.extract_info(channel_url, download=False)

    entries = flat_info.get("entries") or []
    video_ids = []
    for e in entries:
        vid = e.get("id")
        if vid:
            video_ids.append(vid)

    scored = []

    meta_opts = {
        "quiet": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(meta_opts) as ydl:
        for vid in video_ids:
            url = f"https://www.youtube.com/watch?v={vid}"
            try:
                info = ydl.extract_info(url, download=False)
            except Exception:
                continue

            views = safe_int(info.get("view_count"))
            likes = safe_int(info.get("like_count"))
            comments = safe_int(info.get("comment_count"))

            score = (w_views * views) + (w_likes * likes) + (w_comments * comments)

            scored.append({
                "video_id": info.get("id"),
                "title": info.get("title"),
                "webpage_url": info.get("webpage_url"),
                "upload_date": to_iso_date(info.get("upload_date")),
                "channel": {
                    "name": info.get("uploader"),
                    "channel_id": info.get("channel_id"),
                    "channel_url": info.get("channel_url"),
                },
                "stats": {
                    "view_count": views,
                    "like_count": likes,
                    "comment_count": comments,
                },
                "score": score,
            })

    scored.sort(key=lambda d: d["score"], reverse=True)
    return scored[: min(100, len(scored))]


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

            # gcs_path = upload_transcript_to_gcs(video_id, cleaned_text)

            # return {
            #     "video_id": video_id,
            #     "gcs_path": gcs_path,
            #     "text": cleaned_text
            # }

            
            return {
                "video_id": video_id,
                 "text": cleaned_text
             }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
        
def fetch_transcript_text(video_id: str) -> str | None:
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        def dl(manual: bool, auto: bool):
            opts = {
                "quiet": True,
                "skip_download": True,
                "writesubtitles": manual,
                "writeautomaticsub": auto,
                "subtitleslangs": ["en"],
                "subtitlesformat": "vtt",
                "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])

        try:
            dl(True, False)
            vtts = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".vtt")]
            if not vtts:
                dl(False, True)
                vtts = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".vtt")]
            if not vtts:
                return None

            best = max(vtts, key=lambda p: os.path.getsize(p))
            raw = open(best, "r", encoding="utf-8").read()
            text = clean_vtt_text(raw)
            return text or None
        except Exception:
            return None
        
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

@app.get("/top_videos/buckets")
def top_20_videos_by_bucket_with_transcripts(
    w_views: float = 0.34,
    w_likes: float = 0.33,
    w_comments: float = 0.33,
):

    if (w_views + w_likes + w_comments) <= 0:
        raise HTTPException(status_code=400, detail="Weights must sum to > 0")

    results: dict[str, list[dict]] = {}

    meta_opts = {"quiet": True, "skip_download": True}

    for bucket, channels in CHANNEL_BUCKETS.items():
        results[bucket] = []

        for channel_url in channels:
            flat_opts = {
                "quiet": True,
                "skip_download": True,
                "extract_flat": True,
                "playlistend": 800 if bucket in NON_TRAVEL_BUCKETS else 200,
            }
            with yt_dlp.YoutubeDL(flat_opts) as ydl:
                flat = ydl.extract_info(channel_url, download=False)

            vids = []
            for e in (flat.get("entries") or []):
                vid = e.get("id")
                if not vid:
                    continue

                if vid.startswith("UC"):
                    continue

                if not e.get("url"):
                    continue

                vids.append(vid)

            scored = []
            with yt_dlp.YoutubeDL(meta_opts) as ydl:
                for vid in vids:
                    try:
                        info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
                    except Exception:
                        continue

                    if bucket in NON_TRAVEL_BUCKETS and not is_travel_video(info):
                        continue

                    views = safe_int(info.get("view_count"))
                    likes = safe_int(info.get("like_count"))
                    comments = safe_int(info.get("comment_count"))
                    score = (w_views * views) + (w_likes * likes) + (w_comments * comments)

                    scored.append({
                        "video_id": info.get("id"),
                        "title": info.get("title"),
                        "webpage_url": info.get("webpage_url"),
                        "upload_date": to_iso_date(info.get("upload_date")),
                        "stats": {
                            "view_count": views,
                            "like_count": likes,
                            "comment_count": comments,
                        },
                        "score": score,
                    })

            scored.sort(key=lambda x: x["score"], reverse=True)
            top20 = scored[:20]

            for v in top20:
                v["transcript"] = fetch_transcript_text(v["video_id"])  # None if not available

            results[bucket].append({
                "channel_url": channel_url,
                "weights": {"views": w_views, "likes": w_likes, "comments": w_comments},
                "top_20": top20,
            })

    return {"status": "ok", "results": results}

def fetch_channel_video_entries(channel_url: str, max_videos: int = 200) -> list[dict]:
    url = channel_url.rstrip("/")
    if not url.endswith("/videos"):
        url = url + "/videos"

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "in_playlist",   # faster + more consistent list
        "playlistend": max_videos,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = info.get("entries") or []
    cleaned = []
    for e in entries:
        if not e:
            continue
        vid = e.get("id")
        # Real video ids are usually 11 chars; UC_... is NOT a video
        if not vid or len(vid) != 11:
            continue
        cleaned.append(e)
    return cleaned


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

class YouTubeRequest(BaseModel):
    video_id: str
    model: str = "gpt-4o-mini-transcribe"

@app.post("/transcribe/youtube")
def transcribe_youtube(req: YouTubeRequest):
    if not client:
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