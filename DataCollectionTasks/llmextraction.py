# main.py

import os
from typing import List, Dict, Any

from google import genai  # pip install google-genai

from sklearn.cluster import KMeans  # currently unused, but imported for later work
import numpy as np  # currently unused, but imported for later work

import json
import requests


# WARNING: do NOT commit your real key to GitHub.
# For local testing this is okay, but you should move this to an env var later.
GEMINI_API_KEY = "AIzaSyBvsv5PLBlwVxyGvB6uMaqjv92aTSpfpMw"  # replace with your actual Gemini API key
#GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"api_version": "v1beta"},
)

for m in client.models.list():
    print(m.name)

GENERATION_MODEL = "gemini-2.5-flash"
TRANSCRIPT_BASE_URL = "http://localhost:8000"  # adjust if different host/port


def fetch_transcript_from_api(video_id: str) -> str:
    """
    Calls your FastAPI service:
      GET /transcript/{video_id}
    and returns the 'text' field.
    """
    url = f"{TRANSCRIPT_BASE_URL}/transcript/{video_id}"
    resp = requests.get(url)
    if resp.status_code == 404:
        # Transcript not available
        return ""
    resp.raise_for_status()
    data = resp.json()
    return data.get("text", "")


def build_country_features(
    title: str,
    description: str,
    top_comments: List[str],
    transcript: str,
) -> str:
    """
    Builds a text block with basic video context + transcript.
    We now use this as part of a richer feature-extraction prompt.
    """
    text = f"Video title: {title}\n\n"
    text += f"Description:\n{description}\n\n"
    text += "Top comments:\n"
    for i, c in enumerate(top_comments, start=1):
        text += f"{i}. {c}\n"
    text += "\nTranscript:\n"
    # Truncate to avoid sending huge transcripts
    text += transcript[0:5000]
    return text


# JSON schema for structured video feature extraction
VIDEO_FEATURES_SCHEMA: Dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "countries": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Countries mentioned or clearly implied in the transcript or metadata.",
        },
        "places": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Cities, regions, landmarks, or specific locations mentioned.",
        },
        "traits": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Other inferred traits, such as topic, tone, target audience, etc.",
        },
    },
    "required": ["countries", "places", "traits"],
}


def extract_video_features_for_video(
    video_id: str,
    title: str,
    description: str,
    top_comments: List[str],
) -> Dict[str, List[str]]:
    transcript = fetch_transcript_from_api(video_id)
    print(transcript[0:5000])

    features_text = build_country_features(
        title=title,
        description=description,
        top_comments=top_comments,
        transcript=transcript,
    )

    prompt = (
        "You are extracting structured metadata from a YouTube video.\n\n"
        "From the following information (title, description, comments, transcript), "
        "identify the following fields:\n"
        "- countries: list all countries explicitly mentioned or clearly implied.\n"
        "- places: list cities, regions, landmarks, or other specific locations mentioned.\n"
        "- traits: other relevant traits you can infer, such as topic/domain "
        "(e.g., finance, gaming, education), tone (e.g., casual, formal, salesy), "
        "target audience (e.g., beginners, advanced), etc.\n\n"
        "If a field has no good candidates, return an empty array for that field.\n"
        "Do not include explanations; just follow the schema.\n\n"
        f"{features_text}\n"
    )

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": VIDEO_FEATURES_SCHEMA,
        },
    )

    raw = (response.text or "").strip()

    default_result: Dict[str, List[str]] = {
        "countries": [],
        "places": [],
        "traits": [],
    }
    if not raw:
        return default_result

    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return default_result

        countries = data.get("countries") or []
        places = data.get("places") or []
        traits = data.get("traits") or []

        return {
            "countries": [str(c).strip() for c in countries if c],
            "places": [str(p).strip() for p in places if p],
            "traits": [str(t).strip() for t in traits if t],
        }
    except json.JSONDecodeError:
        return default_result


def build_travel_prompt(
    channel_title: str,
    tags: List[str],
    title: str,
    description: str,
    top_comments: List[str],
    transcript: str,
) -> str:
    prompt = (
        "You are labeling a YouTube video as Travel or Non-Travel.\n"
        "A 'Travel' video is mainly about trips, tourism, vlogs of journeys, "
        "exploring cities or countries, etc.\n\n"
        "Return only one word: Travel or Non-Travel.\n\n"
        f"Channel title: {channel_title}\n"
        f"Tags: {', '.join(tags)}\n\n"
        f"Video title: {title}\n"
        f"Description: {description}\n\n"
        "Top comments:\n"
    )
    for i, c in enumerate(top_comments, start=1):
        prompt += f"{i}. {c}\n"
    prompt += "\nTranscript:\n"
    prompt += transcript[0:5000]
    return prompt


def classify_is_travel_video(
    video_id: str,
    channel_title: str,
    tags: List[str],
    title: str,
    description: str,
    top_comments: List[str],
) -> bool:
    """
    Uses Gemini to classify whether a video is a travel video or not.
    Returns True if Travel, False otherwise.
    """
    transcript = fetch_transcript_from_api(video_id)

    prompt = build_travel_prompt(
        channel_title=channel_title,
        tags=tags,
        title=title,
        description=description,
        top_comments=top_comments,
        transcript=transcript,
    )

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )

    raw = (response.text or "").strip().lower()
    # print("RAW TRAVEL OUTPUT:", raw)  # uncomment for debugging

    # Very simple heuristic based on the expected "Travel" / "Non-Travel" answer
    if "travel" in raw and "non" not in raw:
        return True
    if "non" in raw and "travel" in raw:
        return False
    # Fallback: treat unclear answers as Non-Travel
    return False


if __name__ == "__main__":
    # 1. Choose a video ID that your FastAPI transcript API supports
    test_video_id = "FPX6zAA3tJI"  # replace with your real test video
    # 2. Provide some metadata (you can pull this from the YouTube Data API later)
    channel_title = "Example Travel Channel"
    tags = ["travel", "vlog", "europe", "vacation"]
    title = "Travel vlog across Europe"
    description = "In this video I travel through France, Germany, and Italy."
    top_comments = [
        "Loved the scenes from Paris!",
        "Germany looked incredible.",
        "Please visit Spain next time!",
    ]

    # 3. First: classify if it's a travel video
    is_travel = classify_is_travel_video(
        video_id=test_video_id,
        channel_title=channel_title,
        tags=tags,
        title=title,
        description=description,
        top_comments=top_comments,
    )

    print(f"Is travel video? {is_travel}")

    # 4. If it IS a travel video, extract structured features
    if is_travel:
        features = extract_video_features_for_video(
            video_id=test_video_id,
            title=title,
            description=description,
            top_comments=top_comments,
        )
        print("Extracted video features:", features)
        # You can still access just countries with: features["countries"]
    else:
        print("Not a travel video; skipping feature extraction.")
