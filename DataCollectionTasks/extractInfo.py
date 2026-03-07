# extractInfo.py

import os
from typing import List, Dict, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Country Extraction & Sentiment API")


class Comment(BaseModel):
    text: str


class VideoCountryInput(BaseModel):
    video_id: str
    title: str
    description: str
    top_comments: List[Comment]


class CountrySentiment(BaseModel):
    country: str
    sentiment: Literal["positive", "neutral", "negative"]
    sentiment_score: float  # -1 to 1
    example_comments: List[str]
    reasoning: str


class VideoCountryAnalysis(BaseModel):
    video_id: str
    countries: List[CountrySentiment]


class BatchCountryRequest(BaseModel):
    videos: List[VideoCountryInput]
    model: str = "gpt-4o-mini"


def build_country_context(video: VideoCountryInput) -> str:
    comments_text = "\n".join(f"- {c.text}" for c in video.top_comments)
    return f"""
TITLE: {video.title}

DESCRIPTION:
{video.description}

TOP COMMENTS:
{comments_text}
""".strip()


@app.post("/analyze/videos/country", response_model=List[VideoCountryAnalysis])
def analyze_country_sentiment(req: BatchCountryRequest):
    if not client.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    analyses: List[VideoCountryAnalysis] = []

    for video in req.videos:
        context = build_country_context(video)

        prompt = f"""
You are an analyst for YouTube video performance and sentiment.

Given the video metadata and comments below, do the following:

1. Extract all COUNTRIES mentioned or clearly implied as locations (e.g., "U.S.", "America", "NYC" -> United States).
2. For each country, estimate:
   - overall sentiment from viewers toward that country in this context
   - sentiment_score in [-1, 1] (negative to positive)
   - up to 3 representative example comments
   - a short reasoning summary

Return ONLY valid JSON as a list under key "countries".
Each item must have:
  - "country": string (e.g., "United States", "Japan")
  - "sentiment": "positive" | "neutral" | "negative"
  - "sentiment_score": number between -1 and 1
  - "example_comments": list of strings
  - "reasoning": string

If no country is mentioned, return {{"countries": []}}.

VIDEO CONTEXT:
{context}
"""

        try:
            resp = client.chat.completions.create(
                model=req.model,
                messages=[
                    {"role": "system", "content": "You are a strict JSON-only extractor."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            content = resp.choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Country analysis failed for video {video.video_id}: {str(e)}",
            )

        import json

        try:
            parsed = json.loads(content)
            countries_raw = parsed.get("countries", [])
        except Exception:
            # Fallback: no countries parsed
            countries_raw = []

        countries_structured: List[CountrySentiment] = []
        for c in countries_raw:
            try:
                countries_structured.append(
                    CountrySentiment(
                        country=c.get("country", "Unknown"),
                        sentiment=c.get("sentiment", "neutral"),
                        sentiment_score=float(c.get("sentiment_score", 0.0)),
                        example_comments=list(c.get("example_comments", [])),
                        reasoning=c.get("reasoning", ""),
                    )
                )
            except Exception:
                # Skip malformed entry
                continue

        analyses.append(
            VideoCountryAnalysis(
                video_id=video.video_id,
                countries=countries_structured,
            )
        )

    return analyses
