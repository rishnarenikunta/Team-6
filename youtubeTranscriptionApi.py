import os
import re
import html
import json
import time
import tempfile
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from google.cloud import storage
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

app = FastAPI(title="YouTube Transcription API", version="1.0.0")

PY = sys.executable

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "youtravel_transcripts")
storage_client = storage.Client()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "travel_app")
VIDEOS_COLLECTION = os.getenv("VIDEOS_COLLECTION", "videos")
METADATA_COLLECTION = os.getenv("METADATA_COLLECTION", "metadata")
COMMENTS_COLLECTION = os.getenv("COMMENTS_COLLECTION", "comments")
FFMPEG = os.getenv("FFMPEG_PATH", "ffmpeg")

mongo_client = MongoClient(MONGODB_URI) if MONGODB_URI else None
db = mongo_client[MONGODB_DB] if mongo_client else None
videos_col = db[VIDEOS_COLLECTION] if db is not None else None
metadata_col = db[METADATA_COLLECTION] if db is not None else None
comments_col = db[COMMENTS_COLLECTION] if db is not None else None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

TRAVEL_KEYWORDS = [
    "travel", "trip", "tour", "itinerary", "vacation",
    "explore", "exploring",
    "city", "country", "island", "beach", "mountain",
    "airport", "flight", "train",
    "hotel", "hostel",
    "vlog"
]

CHANNEL_BUCKETS: dict[str, list[str]] = {
     "Travel": [
        "https://www.youtube.com/@fearlessandfar/videos",
        "https://www.youtube.com/@drewbinsky/videos",
        "https://www.youtube.com/@KenAbroad/videos",
        "https://www.youtube.com/@SabbaticalTommy/videos",
        "https://www.youtube.com/@MaxRoving/videos",
        "https://www.youtube.com/@TheEndlessAdventure/videos",
        "https://www.youtube.com/@Evazubeck/videos",
        "https://www.youtube.com/@harryjaggardtravel/videos",
        "https://www.youtube.com/@lostleblanc/videos",
        "https://www.youtube.com/@baldandbankrupt/videos",
        "https://www.youtube.com/@ChrisburkardStudio/videos",
        "https://www.youtube.com/@Louis/videos",
        "https://www.youtube.com/@sealontour/videos",
        "https://www.youtube.com/@TopTravel_YT/videos",
    ],
}

NON_TRAVEL_BUCKETS = {"Food", "Lifestyle/Vlog", "Tech", "Entertainment", "News", "Wellness"}

DEFAULT_WEIGHTS = {
    "views": 0.34,
    "likes": 0.33,
    "comments": 0.33,
}

COMMON_YTDLP_OPTS = {
    "quiet": True,
    "ignoreconfig": False,
    "sleep_requests": 0.75,
    "sleep_interval": 10,
    "max_sleep_interval": 20,
    "sleep_subtitles": 5,
    "retries": 10,
    "extractor_retries": 10,
    "fragment_retries": 10,
    "skip_download": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["web"]
        }
    },
}

# ---------------------------------------------------------------------------
# Startup checks
# ---------------------------------------------------------------------------

def verify_ffmpeg():
    try:
        proc = subprocess.run(
            [FFMPEG, "-version"],
            capture_output=True,
            text=True,
            timeout=15
        )
        if proc.returncode == 0:
            print(f"[FFMPEG OK] {FFMPEG}")
        else:
            print(f"[FFMPEG BAD] rc={proc.returncode} err={(proc.stderr or proc.stdout)[:300]}")
    except Exception as e:
        print(f"[FFMPEG MISSING] {str(e)[:300]}")


verify_ffmpeg()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_travel_video(info: dict) -> bool:
    text = ((info.get("title") or "") + " " + (info.get("description") or "")).lower()
    return any(word in text for word in TRAVEL_KEYWORDS)


def upload_transcript_to_gcs(video_id: str, transcript_text: str) -> str:
    bucket = storage_client.bucket(BUCKET_NAME)
    blob_path = f"transcripts/{video_id}.json"
    blob = bucket.blob(blob_path)
    payload = {"video_id": video_id, "text": transcript_text}
    blob.upload_from_string(json.dumps(payload, ensure_ascii=False), content_type="application/json")
    gcs_uri = f"gs://{BUCKET_NAME}/{blob_path}"
    print(f"[GCS UPLOAD OK] {gcs_uri}")
    return gcs_uri


def clean_vtt_text(raw: str) -> str:
    raw = html.unescape(raw)
    lines = raw.splitlines()
    cleaned_lines = []
    prev_line = None

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
        if not line or line == prev_line:
            continue
        cleaned_lines.append(line)
        prev_line = line

    return " ".join(cleaned_lines).strip()


def safe_int(x) -> int:
    try:
        return int(x) if x is not None else 0
    except Exception:
        return 0


def to_iso_date(upload_date: Optional[str]) -> Optional[str]:
    if not upload_date:
        return None
    try:
        return datetime.strptime(upload_date, "%Y%m%d").date().isoformat()
    except Exception:
        return None


def ydl_with_cookies(extra: Optional[dict] = None) -> yt_dlp.YoutubeDL:
    opts = {**COMMON_YTDLP_OPTS}
    if extra:
        opts.update(extra)
    cookies_path = os.getenv("YT_COOKIES_PATH")
    if cookies_path and os.path.exists(cookies_path):
        opts["cookiefile"] = cookies_path
    return yt_dlp.YoutubeDL(opts)


def _insert_cookies_flag(cmd: list[str], cookies_path: Optional[str]) -> list[str]:
    if cookies_path and os.path.exists(cookies_path):
        cmd.insert(3, "--cookies")
        cmd.insert(4, cookies_path)
    return cmd


def _run(cmd: list[str], timeout: int = 1200) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"Command failed rc={proc.returncode}: {err[:600]}")


def _reencode_to_mp3(src_path: str, dst_path: str) -> None:
    _run([
        FFMPEG, "-y", "-i", src_path,
        "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k",
        dst_path,
    ], timeout=1200)


def _split_mp3(mp3_path: str, out_dir: str, segment_seconds: int = 1200) -> list[str]:
    out_pattern = os.path.join(out_dir, "chunk_%03d.mp3")
    _run([
        FFMPEG, "-y", "-i", mp3_path,
        "-f", "segment", "-segment_time", str(segment_seconds),
        "-c", "copy", out_pattern,
    ], timeout=1200)
    return sorted(
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.startswith("chunk_") and f.endswith(".mp3")
    )


def _whisper_transcribe_file(path: str, model: str = "gpt-4o-mini-transcribe") -> str:
    with open(path, "rb") as f:
        result = client.audio.transcriptions.create(model=model, file=f)
    return (result.text or "").strip()


# ---------------------------------------------------------------------------
# Mongo helpers
# ---------------------------------------------------------------------------

def save_metadata_to_mongo(metadata: dict):
    if metadata_col is None:
        raise HTTPException(status_code=500, detail="Mongo not configured. Set MONGODB_URI.")
    video_id = metadata.get("video_id")
    if not video_id:
        raise HTTPException(status_code=500, detail="Missing video_id in metadata")
    metadata_col.update_one(
        {"_id": video_id},
        {"$set": {**metadata, "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )


def save_comments_to_mongo(video_id: str, comments: list):
    if comments_col is None:
        raise HTTPException(status_code=500, detail="Mongo not configured. Set MONGODB_URI.")
    now = datetime.now(timezone.utc)
    operations = []
    for c in comments:
        comment_id = c.get("id")
        if not comment_id:
            continue
        mongo_id = f"{video_id}:{comment_id}"
        doc = {
            "_id": mongo_id,
            "video_id": video_id,
            "comment_id": comment_id,
            "author": c.get("author"),
            "text": c.get("text"),
            "like_count": c.get("like_count") or 0,
            "timestamp": c.get("timestamp"),
            "parent": c.get("parent") or "root",
            "updated_at": now,
        }
        operations.append(UpdateOne({"_id": mongo_id}, {"$set": doc}, upsert=True))
    if operations:
        result = comments_col.bulk_write(operations, ordered=False)
        return {
            "matched": result.matched_count,
            "modified": result.modified_count,
            "upserted": len(result.upserted_ids),
        }
    return {"matched": 0, "modified": 0, "upserted": 0}


# ---------------------------------------------------------------------------
# Transcript helpers
# ---------------------------------------------------------------------------

def try_subtitles_first(video_id: str) -> Optional[str]:
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    cookies_path = os.getenv("YT_COOKIES_PATH")
    if not cookies_path or not os.path.exists(cookies_path):
        print(f"[SUBTITLES SKIP] {video_id} no cookies")
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "vtt",
            "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
            "quiet": True,
            "cookiefile": cookies_path,
            "ignoreconfig": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            print(f"[SUBTITLES FAIL] {video_id} err={str(e)[:400]}")
            return None

        vtt_files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".vtt")]
        if not vtt_files:
            print(f"[SUBTITLES NONE] {video_id}")
            return None

        vtt_file = max(vtt_files, key=lambda p: os.path.getsize(p))
        with open(vtt_file, "r", encoding="utf-8") as f:
            raw_vtt = f.read()

        cleaned_text = clean_vtt_text(raw_vtt)
        if not cleaned_text:
            print(f"[SUBTITLES EMPTY] {video_id}")
            return None

        print(f"[SUBTITLES OK] {video_id} chars={len(cleaned_text)}")
        return cleaned_text


def try_whisper_next(video_id: str, model: str = "gpt-4o-mini-transcribe") -> Optional[str]:
    if not client:
        print(f"[WHISPER SKIP] {video_id} (OPENAI_API_KEY missing)")
        return None

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    cookies_path = os.getenv("YT_COOKIES_PATH")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = [
                PY, "-m", "yt_dlp",
                "--no-warnings",
                "--no-playlist",
                "--sleep-requests", "0.75",
                "--sleep-interval", "10",
                "--max-sleep-interval", "20",
                "--retries", "10",
                "--extractor-retries", "10",
                "--extractor-args", "youtube:player_client=web",
                "--js-runtimes", "node",
                "-f", "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio[ext=webm]/140/251/bestaudio/best",
                "-o", os.path.join(tmpdir, "audio.%(ext)s"),
                video_url,
            ]
            cmd = _insert_cookies_flag(cmd, cookies_path)

            print(f"[WHISPER TRY] {video_id} downloading audio...")
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if proc.returncode != 0:
                print(f"[WHISPER AUDIO FAIL] {video_id} err={(proc.stderr or proc.stdout)[:400]}")
                return None

            audio_candidates = [
                os.path.join(tmpdir, f)
                for f in os.listdir(tmpdir)
                if f.startswith("audio.")
            ]
            if not audio_candidates:
                print(f"[WHISPER AUDIO MISSING] {video_id}")
                return None

            audio_path = max(audio_candidates, key=os.path.getsize)
            mp3_path = os.path.join(tmpdir, "audio_16k_mono.mp3")
            try:
                _reencode_to_mp3(audio_path, mp3_path)
            except Exception as e:
                print(f"[WHISPER FFMPEG FAIL] {video_id} err={str(e)[:400]}")
                return None

            size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
            print(f"[WHISPER AUDIO READY] {video_id} mp3={size_mb:.1f}MB")
            text_parts: list[str] = []

            if size_mb > 10:
                chunks_dir = os.path.join(tmpdir, "chunks")
                os.makedirs(chunks_dir, exist_ok=True)
                try:
                    chunks = _split_mp3(mp3_path, chunks_dir, segment_seconds=600)
                except Exception as e:
                    print(f"[WHISPER CHUNK FFMPEG FAIL] {video_id} err={str(e)[:400]}")
                    return None
                if not chunks:
                    print(f"[WHISPER CHUNK FAIL] {video_id} (no chunks)")
                    return None
                for idx, ch in enumerate(chunks, start=1):
                    try:
                        part = _whisper_transcribe_file(ch, model=model)
                        if part:
                            text_parts.append(part.strip())
                    except Exception as e:
                        print(f"[WHISPER CHUNK FAIL] {video_id} idx={idx} err={str(e)[:400]}")
                        return None
            else:
                try:
                    part = _whisper_transcribe_file(mp3_path, model=model)
                    if part:
                        text_parts.append(part.strip())
                except Exception as e:
                    print(f"[WHISPER FAIL] {video_id} err={str(e)[:400]}")
                    return None

            text = " ".join(text_parts).strip()
            if text:
                print(f"[WHISPER OK] {video_id} chars={len(text)}")
                return text
            print(f"[WHISPER EMPTY] {video_id}")
            return None

    except Exception as e:
        print(f"[WHISPER FAIL] {video_id} err={str(e)[:400]}")
        return None


def fetch_transcript_text(video_id: str, model: str = "gpt-4o-mini-transcribe") -> Optional[str]:
    text = try_subtitles_first(video_id)
    if text:
        return text
    print(f"[SUBTITLES NOT USABLE] {video_id} falling back to Whisper")
    return try_whisper_next(video_id, model=model)


def fetch_comments(video_id: str, n: int = 10, timeout_sec: int = 600):
    url = f"https://www.youtube.com/watch?v={video_id}"
    cookies = os.getenv("YT_COOKIES_PATH")
    cmd = [
        "yt-dlp",
        "--ignore-config",
        "--skip-download",
        "--get-comments",
        "--extractor-args", "youtube:comment_sort=top",
        "--dump-single-json",
        url,
    ]
    if cookies and os.path.exists(cookies):
        cmd[1:1] = ["--cookies", cookies]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail=f"Timed out fetching comments after {timeout_sec}s")

    if proc.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"yt-dlp comments error: {proc.stderr.strip() or proc.stdout.strip()}",
        )

    try:
        data = json.loads(proc.stdout)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse yt-dlp JSON for {video_id}. stderr={proc.stderr.strip()[:500]}",
        )

    comments = data.get("comments") or []
    comments.sort(key=lambda c: (c.get("like_count") or 0), reverse=True)

    return [
        {
            "id": c.get("id"),
            "author": c.get("author"),
            "text": c.get("text") or c.get("content"),
            "like_count": c.get("like_count"),
            "timestamp": c.get("timestamp"),
            "parent": c.get("parent"),
        }
        for c in comments[:n]
    ]


def fetch_video_info(video_id: str) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "ignore_no_formats_error": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "video_id": info.get("id"),
        "title": info.get("title"),
        "webpage_url": info.get("webpage_url"),
        "upload_date": to_iso_date(info.get("upload_date")),
        "view_count": safe_int(info.get("view_count")),
        "like_count": safe_int(info.get("like_count")),
        "comment_count": safe_int(info.get("comment_count")),
        "description": info.get("description") or "",
        "uploader": info.get("uploader"),
        "channel_id": info.get("channel_id"),
        "channel_url": info.get("channel_url"),
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    return {
        "status": "Online",
        "message": "Go to /docs to test the tool",
        "bucket": BUCKET_NAME,
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "cookies_path_set": bool(os.getenv("YT_COOKIES_PATH")),
        "cookies_exists": bool(os.getenv("YT_COOKIES_PATH") and os.path.exists(os.getenv("YT_COOKIES_PATH"))),
        "gcp_project": storage_client.project,
        "py": PY,
        "ffmpeg": FFMPEG,
        "mongo_connected": bool(mongo_client),
        "metadata_collection": METADATA_COLLECTION,
        "comments_collection": COMMENTS_COLLECTION,
    }


@app.get("/transcript/{video_id}")
def get_transcript(video_id: str):
    cookies_path = os.getenv("YT_COOKIES_PATH")
    if not cookies_path or not os.path.exists(cookies_path):
        raise HTTPException(status_code=500, detail="Missing YT_COOKIES_PATH or cookies file not found")

    text = fetch_transcript_text(video_id)
    if not text:
        raise HTTPException(status_code=404, detail="No subtitles found")

    gcs_path = upload_transcript_to_gcs(video_id, text)
    return {"video_id": video_id, "gcs_path": gcs_path, "text": text}


@app.get("/metadata/{video_id}")
def get_metadata(video_id: str, gcs_transcript_path: Optional[str] = None):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "ignore_no_formats_error": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"yt-dlp metadata error: {str(e)}")

    metadata = {
        "video_id": info.get("id"),
        "title": info.get("title"),
        "channel": {
            "channel_id": info.get("channel_id"),
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
        "gcs_transcript_path": gcs_transcript_path,
    }

    save_metadata_to_mongo(metadata)
    return metadata

@app.get("/comments/{video_id}")
def get_comments(video_id: str, n: int = 10, timeout_sec: int = 600):
    if n < 1 or n > 50:
        raise HTTPException(status_code=400, detail="n must be between 1 and 50")

    comments = fetch_comments(video_id, n=n, timeout_sec=timeout_sec)
    save_comments_to_mongo(video_id, comments)
    print(f"[MONGO COMMENTS OK] {video_id}")
    return {"video_id": video_id, "sort": "top", "comments": comments}



@app.get("/top_videos/buckets")
def top_20_videos_by_bucket_store(
    w_views: float = DEFAULT_WEIGHTS["views"],
    w_likes: float = DEFAULT_WEIGHTS["likes"],
    w_comments: float = DEFAULT_WEIGHTS["comments"],
):
    if (w_views + w_likes + w_comments) <= 0:
        raise HTTPException(status_code=400, detail="Weights must sum to > 0")

    results: dict[str, list[dict]] = {}

    for bucket, channels in CHANNEL_BUCKETS.items():
        results[bucket] = []

        for channel_url in channels:
            with ydl_with_cookies({"extract_flat": True, "playlistend": 100}) as ydl:
                flat = ydl.extract_info(channel_url, download=False)

            vids = []
            for e in (flat.get("entries") or []):
                e = e or {}
                vid = e.get("id")
                if not vid or vid.startswith("UC") or not e.get("url"):
                    continue
                vids.append(vid)

            scored = []
            for i, vid in enumerate(vids, start=1):
                print(f"[VIDEO {i}/{len(vids)}] Scoring {vid}")
                try:
                    info = fetch_video_info(vid)
                except Exception as e:
                    print(f"[VIDEO SKIP] {vid} err={str(e)[:200]}")
                    continue

                if bucket in NON_TRAVEL_BUCKETS and not is_travel_video(info):
                    continue

                views = safe_int(info.get("view_count"))
                likes = safe_int(info.get("like_count"))
                comments_count = safe_int(info.get("comment_count"))
                score = (w_views * views) + (w_likes * likes) + (w_comments * comments_count)

                scored.append({
                    "video_id": info.get("video_id"),
                    "title": info.get("title"),
                    "webpage_url": info.get("webpage_url"),
                    "upload_date": info.get("upload_date"),
                    "uploader": info.get("uploader"),
                    "channel_id": info.get("channel_id"),
                    "channel_url": info.get("channel_url"),
                    "stats": {
                        "view_count": views,
                        "like_count": likes,
                        "comment_count": comments_count,
                    },
                    "score": score,
                })
                time.sleep(1)

            scored.sort(key=lambda x: x["score"], reverse=True)
            top20 = scored[:25]

            stored = []
            for idx, v in enumerate(top20, start=1):
                vid = v["video_id"]
                print(f"[STORE {idx}/{len(top20)}] {vid}")

                gcs_path = None
                try:
                    transcript_result = get_transcript(vid)
                    gcs_path = transcript_result.get("gcs_path")
                    print(f"[TRANSCRIPT OK] {vid}")
                except Exception as e:
                    print(f"[TRANSCRIPT FAIL] {vid} err={str(e)[:200]}")
                    continue

                try:
                    get_metadata(vid, gcs_transcript_path=gcs_path)
                except Exception as e:
                    print(f"[METADATA FAIL] {vid} err={str(e)[:200]}")
                    continue

                try:
                    get_comments(vid)
                except Exception as e:
                    print(f"[COMMENTS FAIL] {vid} err={str(e)[:200]}")

                stored.append({**v, "gcs_transcript_path": gcs_path})
                time.sleep(2)

            results[bucket].append({
                "channel_url": channel_url,
                "weights": {"views": w_views, "likes": w_likes, "comments": w_comments},
                "top_20": stored,
            })

    return {"status": "ok", "results": results}


class YouTubeRequest(BaseModel):
    video_id: str
    model: str = "gpt-4o-mini-transcribe"


@app.post("/transcribe/youtube")
def transcribe_youtube(req: YouTubeRequest):
    if not client:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    text = fetch_transcript_text(req.video_id, model=req.model)
    if not text:
        raise HTTPException(status_code=500, detail="Could not get subtitles and Whisper returned no transcript")

    transcript_path = upload_transcript_to_gcs(req.video_id, text)
    return {"video_id": req.video_id, "gcs_transcript_path": transcript_path, "text": text}