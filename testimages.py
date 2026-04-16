import requests
import json
import re
import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]


# ── Helpers ────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def get_best_thumbnail_url(video_id: str) -> str | None:
    """Returns the highest-quality available thumbnail URL for a YouTube video."""
    candidates = [
        f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",   # 1280x720
        f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg",       # 640x480
        f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",       # 480x360 (always exists)
    ]
    for url in candidates:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            # maxresdefault returns a tiny placeholder (not a real 404) for some videos
            if resp.status_code == 200 and len(resp.content) > 5000:
                return url
        except requests.RequestException:
            continue
    return None


def get_channel_pfp_url(channel_id: str) -> str | None:
    """
    Scrapes ytInitialData from the channel page to find the avatar URL.
    No yt-dlp or JS runtime needed.
    """
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    try:
        resp = requests.get(channel_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ⚠️  Could not fetch channel page for {channel_id}: {e}")
        return None

    match = re.search(r"var ytInitialData\s*=\s*(\{.*?\});</script>", resp.text, re.DOTALL)
    if not match:
        print(f"  ⚠️  ytInitialData not found for channel {channel_id}")
        return None

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        print(f"  ⚠️  Failed to parse ytInitialData for channel {channel_id}")
        return None

    # Primary path (newer channel layout)
    try:
        metadata  = data["header"]["pageHeaderRenderer"]["content"]["pageHeaderViewModel"]
        sources   = metadata["image"]["decoratedAvatarViewModel"]["avatar"]["avatarViewModel"]["image"]["sources"]
        url = sources[-1]["url"]
    except (KeyError, IndexError, TypeError):
        # Fallback path (older c4TabbedHeaderRenderer layout)
        try:
            thumbnails = data["header"]["c4TabbedHeaderRenderer"]["avatar"]["thumbnails"]
            url = thumbnails[-1]["url"]
        except (KeyError, IndexError, TypeError):
            print(f"  ⚠️  Could not find avatar in ytInitialData for {channel_id}")
            return None

    # Some URLs are protocol-relative: //yt3.ggpht.com/...
    if url.startswith("//"):
        url = "https:" + url
    return url


def fetch_image_bytes(url: str) -> bytes | None:
    """Downloads an image and returns its raw bytes, or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException as e:
        print(f"  ⚠️  Failed to download image from {url}: {e}")
        return None


# ── Main enrichment logic ──────────────────────────────────────────────────────

def enrich_thumbnails_and_pfps():
    """
    1. Iterates every document in `metadata`.
    2. For each video_id  → fetches thumbnail → writes URL back to metadata.thumbnail_url
    3. Collects unique channel_ids → fetches PFP once per channel → writes URL to creators.pfp_url
    """

    # ── 1. Pull all metadata docs (only the two fields we need) ───────────────
    meta_docs = list(
        db["metadata"].find(
            {},
            {"_id": 1, "video_id": 1, "channel": 1},
        )
    )
    print(f"Found {len(meta_docs)} metadata documents to process.\n")

    seen_channels: dict[str, str] = {}   # channel_id → pfp_url (cache so we only scrape once)

    for doc in meta_docs:
        # video_id lives in the `video_id` field (or fall back to _id string)
        video_id   = doc.get("video_id") or str(doc["_id"])
        channel_id = doc.get("channel", {}).get("channel_id", "")

        # ── Thumbnail ──────────────────────────────────────────────────────────
        print(f"[{video_id}] Fetching thumbnail...")
        thumb_url = get_best_thumbnail_url(video_id)

        if thumb_url:
            db["metadata"].update_one(
                {"_id": doc["_id"]},
                {"$set": {"thumbnail_url": thumb_url}},
            )
            print(f"  ✅ thumbnail_url saved → {thumb_url}")
        else:
            print(f"  ❌ No thumbnail found for {video_id}")

        # ── PFP (deduplicated per channel) ─────────────────────────────────────
        if not channel_id:
            print(f"  ⚠️  No channel_id on doc {doc['_id']}, skipping PFP.")
            continue

        if channel_id not in seen_channels:
            print(f"  [{channel_id}] Fetching channel PFP...")
            pfp_url = get_channel_pfp_url(channel_id)
            seen_channels[channel_id] = pfp_url   # cache (even if None, to avoid retrying)

            if pfp_url:
                db["creators"].update_one(
                    {"channel_id": channel_id},
                    {"$set": {"pfp_url": pfp_url}},
                )
                print(f"  ✅ pfp_url saved to creators → {pfp_url}")
            else:
                print(f"  ❌ Could not get PFP for channel {channel_id}")
        else:
            print(f"  ↩️  PFP for {channel_id} already processed, skipping.")

    print("\n✅ Done enriching thumbnails and profile pictures.")


if __name__ == "__main__":
    enrich_thumbnails_and_pfps()