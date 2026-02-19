# main.py

import os
from typing import List

from google import genai  # pip install google-genai

from sklearn.cluster import KMeans  # currently unused, but imported for later work
import numpy as np  # currently unused, but imported for later work

import json
import requests


# WARNING: do NOT commit your real key to GitHub.
# For local testing this is okay, but you should move this to an env var later.
GEMINI_API_KEY = "GEMINIKeyHere"  # replace with your actual Gemini API key
client = genai.Client(api_key=GEMINI_API_KEY)

GENERATION_MODEL = "gemini-2.0-flash"
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
    text = f"Video title: {title}\n\n"
    text += f"Description:\n{description}\n\n"
    text += "Top comments:\n"
    for i, c in enumerate(top_comments, start=1):
        text += f"{i}. {c}\n"
    text += "\nTranscript:\n"
    text += transcript
    return text


def extract_countries_for_video(
    video_id: str,
    title: str,
    description: str,
    top_comments: List[str],
) -> List[str]:
    transcript = fetch_transcript_from_api(video_id)

    features_text = build_country_features(
        title=title,
        description=description,
        top_comments=top_comments,
        transcript=transcript,
    )

    prompt = (
        "You are an assistant that identifies countries mentioned or implied "
        "in YouTube videos.\n"
        "Return ONLY a valid JSON array of country names, e.g. "
        "[\"France\", \"United States\"].\n"
        "Only include real countries (no cities or regions).\n"
        "If no country is clear, return [].\n\n"
        f"{features_text}\n\n"
        "Return ONLY the JSON array."
    )

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )
    

    raw = response.text.strip()
    # print("RAW COUNTRY OUTPUT:", raw)  # uncomment for debugging

    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(c).strip() for c in data if c]
    except json.JSONDecodeError:
        return []
    return []


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
    prompt += transcript
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

    raw = response.text.strip().lower()
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

    # 4. If it IS a travel video, extract countries
    if is_travel:
        countries = extract_countries_for_video(
            video_id=test_video_id,
            title=title,
            description=description,
            top_comments=top_comments,
        )
        print("Extracted countries:", countries)
    else:
        print("Not a travel video; skipping country extraction.")
