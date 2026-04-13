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
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

app = FastAPI(title="YouTube Transcription API", version="1.0.0")

PY = sys.executable

COOKIES_PATH = os.getenv("YT_COOKIES_PATH")

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

COMMON_YTDLP_OPTS = {
    "quiet": True,
    "skip_download": True,
    "retries": 10,
    "extractor_retries": 10,
    "sleep_requests": 0.75,
    "sleep_interval": 10,
    "max_sleep_interval": 20,
    "extractor_args": {
        "youtube": {
            "player_client": ["web"]
        }
    },
}

def ydl_with_cookies(extra: Optional[dict] = None) -> yt_dlp.YoutubeDL:
    opts = {**COMMON_YTDLP_OPTS}
    if extra:
        opts.update(extra)
    cookies_path = os.getenv("YT_COOKIES_PATH")
    if cookies_path and os.path.exists(cookies_path):
        opts["cookiefile"] = cookies_path
    return yt_dlp.YoutubeDL(opts)

CHANNEL_BUCKETS: dict[str, list[str]] = {
    "Travel": [
        "https://www.youtube.com/@fearlessandfar/videos",
        "https://www.youtube.com/@drewbinsky/videos",
        "https://www.youtube.com/@KenAbroad/videos",
        "https://www.youtube.com/@SabbaticalTommy/videos",
        "https://www.youtube.com/@MaxRoving/videos",
        "https://www.youtube.com/@TheEndlessAdventure/videos",
        "https://www.youtube.com/@EvaZuBe/videos",
        "https://www.youtube.com/@harryjaggardtravel/videos",
        "https://www.youtube.com/@lostleblanc/videos",
        "https://www.youtube.com/@baldandbankrupt/videos",
        "https://www.youtube.com/@chrisburkard/videos",
        "https://www.youtube.com/@funforlouis/videos",
        "https://www.youtube.com/@sealontour/videos",
        "https://www.youtube.com/@mikeokayama/videos",
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

def extract_handle_from_url(channel_url: str) -> str:
    """
    Strips /videos (or any trailing path) from a channel URL.
    'https://www.youtube.com/@drewbinsky/videos' -> 'https://www.youtube.com/@drewbinsky'
    """
    # Remove trailing /videos, /shorts, /community, etc.
    return re.sub(r"/(videos|shorts|community|playlists|about)/?$", "", channel_url)


def fetch_creator_info(channel_url: str, category: str) -> Optional[dict]:
    """
    Fetches channel-level metadata from YouTube via yt-dlp.
    Uses playlist_items=0 so it only pulls channel metadata, not individual videos.
    """
    clean_url = extract_handle_from_url(channel_url)

    opts = {
        "extract_flat": True,
        "playlist_items": "0",
        "skip_download": True,
    }

    try:
        with ydl_with_cookies(opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)

        if not info:
            print(f"[CREATOR EMPTY] {clean_url}")
            return None

        return {
            "channel_id": info.get("channel_id") or info.get("id"),
            "name": info.get("channel") or info.get("uploader"),
            "handle": info.get("uploader_id"),          # e.g. @drewbinsky
            "subscriber_count": info.get("channel_follower_count"),
            #"views": info.get("view_count") or 0,             # total channel views
            "join_date": datetime(1970, 1, 1, tzinfo=timezone.utc),                           # not exposed by yt-dlp, needs YT Data API
            "category": category,                        # from CHANNEL_BUCKETS key
            "channel_url": clean_url,
            "scraped_at": datetime.now(timezone.utc),
        }

    except Exception as e:
        print(f"[CREATOR FETCH FAIL] {clean_url} err={str(e)[:300]}")
        return None
    

def scrape_and_upsert_creators() -> list[dict]:
    """
    Iterates CHANNEL_BUCKETS, scrapes each channel, upserts into creators collection.
    Uses channel_id as the stable upsert key.
    """
    if db is None:  # add this
        raise HTTPException(status_code=500, detail="Mongo not configured. Set MONGODB_URI.")
    creators_col = db["creators"]
    results = []

    for category, urls in CHANNEL_BUCKETS.items():
        print(f"\n[CREATORS] Category: {category} ({len(urls)} channels)")

        for channel_url in urls:
            print(f"  Fetching: {channel_url}")
            data = fetch_creator_info(channel_url, category)

            if not data:
                results.append({"url": channel_url, "status": "failed"})
                continue

            channel_id = data.get("channel_id")
            if not channel_id:
                print(f"  [SKIP] No channel_id returned for {channel_url}")
                results.append({"url": channel_url, "status": "no_channel_id"})
                continue

            creators_col.update_one(
                {"channel_id": channel_id},    # stable upsert key
                {"$set": data},
                upsert=True,
            )

            print(f"  ✓ {data.get('name')} | subs={data.get('subscriber_count')} | views={data.get('views')}")
            results.append({
                "url": channel_url,
                "status": "ok",
                "name": data.get("name"),
                "channel_id": channel_id,
                "subscriber_count": data.get("subscriber_count"),
                #"views": data.get("views") or 0,
                "category": category,
            })

            time.sleep(2)   # avoid rate limiting between channels

    return results


@app.post("/scrape/creators")
def scrape_creators():
    """
    Scrapes all channels in CHANNEL_BUCKETS and upserts into the creators collection.
    Each doc will have: channel_id, name, handle, subscriber_count, views,
    join_date (null), category, channel_url, scraped_at.
    """
    if db is None:
        raise HTTPException(status_code=500, detail="Mongo not configured. Set MONGODB_URI.")

    results = scrape_and_upsert_creators()

    ok = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] != "ok"]

    return {
        "status": "ok",
        "total": len(results),
        "succeeded": len(ok),
        "failed": len(failed),
        "creators": ok,
        "errors": failed,
    }