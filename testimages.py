import requests
import json
import re
from pathlib import Path


def get_youtube_thumbnail(video_id: str, headers: dict) -> str | None:
    """
    Returns the best available thumbnail URL using YouTube's predictable CDN paths.
    No yt-dlp or JS runtime needed.
    """
    # Try in descending quality order
    candidates = [
        f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",   # 1280x720
        f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg",       # 640x480
        f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",       # 480x360 (always exists)
    ]
    for url in candidates:
        resp = requests.get(url, headers=headers)
        # maxresdefault returns a 404 or 1x1 placeholder for some videos
        if resp.status_code == 200 and len(resp.content) > 5000:
            return url
    return None


def get_channel_pfp(channel_id: str, headers: dict) -> str | None:
    """
    Scrapes the channel page and extracts the avatar URL from YouTube's
    embedded ytInitialData JSON blob — no yt-dlp or JS runtime required.
    """
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    resp = requests.get(channel_url, headers=headers)
    resp.raise_for_status()

    match = re.search(r"var ytInitialData\s*=\s*(\{.*?\});</script>", resp.text, re.DOTALL)
    if not match:
        print("❌ Could not find ytInitialData in channel page.")
        return None

    data = json.loads(match.group(1))

    try:
        metadata = data["header"]["pageHeaderRenderer"]["content"]["pageHeaderViewModel"]
        thumbnails = metadata["image"]["decoratedAvatarViewModel"]["avatar"]["avatarViewModel"]["image"]["sources"]
        return thumbnails[-1]["url"]
    except (KeyError, IndexError, TypeError):
        try:
            thumbnails = data["header"]["c4TabbedHeaderRenderer"]["avatar"]["thumbnails"]
            return thumbnails[-1]["url"]
        except (KeyError, IndexError, TypeError):
            print("❌ Could not navigate ytInitialData to find avatar.")
            return None


def download_specific_assets(video_id: str, channel_id: str):
    print(f"--- Processing Video: {video_id} ---")

    test_dir = Path("test_assets")
    test_dir.mkdir(exist_ok=True)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    # ── 1. Video Thumbnail ─────────────────────────────────────────────────
    print("Fetching video thumbnail...")
    thumb_url = get_youtube_thumbnail(video_id, headers)

    if thumb_url:
        res = requests.get(thumb_url, headers=headers)
        res.raise_for_status()
        thumb_path = test_dir / f"thumb_{video_id}.jpg"
        thumb_path.write_bytes(res.content)
        print(f"✅ Saved Thumbnail: {thumb_path.name}")
    else:
        print("❌ Could not retrieve video thumbnail.")

    # ── 2. Channel PFP ─────────────────────────────────────────────────────
    print(f"Fetching channel PFP for {channel_id}...")
    pfp_url = get_channel_pfp(channel_id, headers)

    if pfp_url:
        if pfp_url.startswith("//"):
            pfp_url = "https:" + pfp_url
        res = requests.get(pfp_url, headers=headers)
        res.raise_for_status()
        pfp_path = test_dir / f"pfp_{channel_id}.jpg"
        pfp_path.write_bytes(res.content)
        print(f"✅ Saved PFP: {pfp_path.name}")
    else:
        print("❌ PFP not saved.")


if __name__ == "__main__":
    MY_VIDEO_ID = "AETTGnnFY0Y"
    MY_CHANNEL_ID = "UCHza0GAxOvBOeLKkMeL8EcQ"

    download_specific_assets(MY_VIDEO_ID, MY_CHANNEL_ID)