from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
import os
import uuid

from DataCollectionTasks.monoprompt import (
    classify_is_travel_video,
    extract_video_features_for_video,
)

load_dotenv()

app = FastAPI(
    title="LLM Video Analysis API",
    version="1.3.0",
)

# ---------------------------------------------------------------------------
# MongoDB — six collections
# ---------------------------------------------------------------------------
mongo_client       = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db                 = mongo_client[os.getenv("MONGO_DB_NAME", "video_analysis")]
videos_col         = db["videos"]
creators_col       = db["creators"]
narratives_col     = db["narratives"]
claims_col         = db["claims"]
top_narratives_col = db["top_narratives"]
top_claims_col     = db["top_claims"]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class VideoMetadata(BaseModel):
    # Required
    video_id:      str       = Field(..., description="YouTube video ID")
    title:         str       = Field(..., description="Video title")
    # Optional — send what you have
    creator_id:    Optional[str]       = None
    channel_title: Optional[str]       = None
    tags:          Optional[List[str]] = None
    description:   Optional[str]       = None
    duration:      Optional[int]       = None
    upload_date:   Optional[str]       = None
    view_count:    Optional[int]       = None
    like_count:    Optional[int]       = None
    language:      Optional[str]       = None
    comment_count: Optional[int]       = None
    top_comments:  Optional[List[str]] = None


class TravelClassificationResponse(BaseModel):
    video_id:  str
    is_travel: bool


class VideoFeaturesResponse(BaseModel):
    video_id:      str
    is_travel:     bool
    narrative_ids: List[str] = []
    claim_ids:     List[str] = []


# ---------------------------------------------------------------------------
# Helper: only include a key in a $set dict if the value is not None
# ---------------------------------------------------------------------------
def _present(d: dict) -> dict:
    """Strip None values so we never overwrite existing fields with nulls."""
    return {k: v for k, v in d.items() if v is not None}


# ---------------------------------------------------------------------------
# Save to collections — skips any block where data is missing
# ---------------------------------------------------------------------------
def save_features_to_collections(
    payload: VideoMetadata,
    features: Dict[str, Any],
) -> tuple[list, list]:
    now = datetime.now(timezone.utc)
    vc  = features.get("video_components") or {}

    # ── Videos ──────────────────────────────────────────────────────────────
    comment_analysis = vc.get("overall_comment_analysis") or {}

    video_fields = _present({
        "video_id":      payload.video_id,
        "creator_id":    payload.creator_id,
        "title":         payload.title,
        "description":   payload.description,
        "duration":      payload.duration,
        "upload_date":   payload.upload_date,
        "view_count":    payload.view_count,
        "like_count":    payload.like_count,
        "tags":          payload.tags,
        "language":      payload.language,
        "comment_count": payload.comment_count,
        "comments":      payload.top_comments,
        "summary":       vc.get("video_summary") or None,
        "destinations":  vc.get("video_topics_destinations") or None,
        "sentiment":     comment_analysis.get("overall_sentiment") or None,
        "risk_callouts": comment_analysis.get("general_risk_callouts") or None,
        "is_travel":     True,
        "updated_at":    now,
    })

    if video_fields:
        videos_col.update_one(
            {"video_id": payload.video_id},
            {"$set": video_fields},
            upsert=True,
        )

    # ── Creators (stub — only if we have a creator_id) ──────────────────────
    if payload.creator_id:
        creators_col.update_one(
            {"creator_id": payload.creator_id},
            {"$setOnInsert": _present({
                "creator_id":    payload.creator_id,
                "channel_title": payload.channel_title,
                "created_at":    now,
            })},
            upsert=True,
        )

    # ── Narratives + Claims ──────────────────────────────────────────────────
    narrative_ids = []
    claim_ids     = []

    narratives = vc.get("narratives") or []
    for narrative in narratives:
        if not narrative:
            continue

        narrative_id = str(uuid.uuid4())
        narrative_ids.append(narrative_id)

        narrative_doc = _present({
            "narrative_id":     narrative_id,
            "video_id":         payload.video_id,
            "narrative_title":  narrative.get("narrative_title"),
            "narrative_text":   narrative.get("narrative_description"),
            "narrative_vector": narrative.get("narrative_title_embedding"),
            "comment_summary":  narrative.get("narrative_comment_summary"),
            "risk": _present({
                "sentiment": narrative.get("narrative_comment_risk"),
                "risk_text":  narrative.get("narrative_comment_risk"),
            }) or None,
            "date": now,
        })

        if narrative_doc:
            narratives_col.insert_one(narrative_doc)

        for claim in (narrative.get("claims") or []):
            if not claim:
                continue

            claim_id = str(uuid.uuid4())
            claim_ids.append(claim_id)

            claim_doc = _present({
                "claim_id":     claim_id,
                "narrative_id": narrative_id,
                "video_id":     payload.video_id,
                "claim_title":  claim.get("claim_title"),
                "claim_text":   claim.get("claim_text"),
                "claim_vector": claim.get("claim_title_embedding"),
                "risks": _present({
                    "sentiment": claim.get("claim_comment_sentiment"),
                    "risk_text": claim.get("claim_comment_risk"),
                }) or None,
                "fact_check":   claim.get("fact_check_assessment"),
                "date":         now,
            })

            if claim_doc:
                claims_col.insert_one(claim_doc)

    return narrative_ids, claim_ids


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/classify_travel", response_model=TravelClassificationResponse)
def classify_travel(payload: VideoMetadata):
    try:
        is_travel = classify_is_travel_video(
            video_id=payload.video_id,
            channel_title=payload.channel_title or "",
            tags=payload.tags or [],
            title=payload.title,
            description=payload.description or "",
            top_comments=payload.top_comments or [],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {e}")

    videos_col.update_one(
        {"video_id": payload.video_id},
        {
            "$set":         {"is_travel": is_travel, "updated_at": datetime.now(timezone.utc)},
            "$setOnInsert": {"video_id": payload.video_id},
        },
        upsert=True,
    )

    return TravelClassificationResponse(video_id=payload.video_id, is_travel=is_travel)


@app.post("/video_features", response_model=VideoFeaturesResponse)
def video_features(payload: VideoMetadata):
    # 1. Classify
    try:
        is_travel = classify_is_travel_video(
            video_id=payload.video_id,
            channel_title=payload.channel_title or "",
            tags=payload.tags or [],
            title=payload.title,
            description=payload.description or "",
            top_comments=payload.top_comments or [],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {e}")

    if not is_travel:
        videos_col.update_one(
            {"video_id": payload.video_id},
            {"$set": {"video_id": payload.video_id, "is_travel": False,
                      "updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )
        return VideoFeaturesResponse(video_id=payload.video_id, is_travel=False)

    # 2. Extract features
    try:
        features = extract_video_features_for_video(
            video_id=payload.video_id,
            title=payload.title,
            description=payload.description or "",
            top_comments=payload.top_comments or [],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature extraction error: {e}")

    # 3. Route each piece to its collection — skips missing fields automatically
    narrative_ids, claim_ids = save_features_to_collections(payload, features)

    return VideoFeaturesResponse(
        video_id=payload.video_id,
        is_travel=True,
        narrative_ids=narrative_ids,
        claim_ids=claim_ids,
    )


@app.get("/video/{video_id}")
def get_video(video_id: str):
    doc = videos_col.find_one({"video_id": video_id}, {"_id": 0})
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")

    narratives = list(narratives_col.find({"video_id": video_id}, {"_id": 0}))
    for n in narratives:
        n["claims"] = list(claims_col.find({"narrative_id": n["narrative_id"]}, {"_id": 0}))

    return {**doc, "narratives": narratives}