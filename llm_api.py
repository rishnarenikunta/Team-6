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

app = FastAPI(title="LLM Video Analysis API", version="1.4.0")

# ---------------------------------------------------------------------------
# MongoDB collections
# ---------------------------------------------------------------------------
client         = MongoClient(os.getenv("MONGODB_URI"))
db             = client["travel_app"]
metadata_col   = db["metadata"]
comments_col   = db["comments"]
videos_col     = db["videos"]
creators_col   = db["creators"]
narratives_col = db["narratives"]
claims_col     = db["claims"]
top_narratives_col = db["top_narratives"]
top_claims_col     = db["top_claims"]

TOP_COMMENTS_LIMIT = 20  # how many top comments to pull for LLM context


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class VideoRequest(BaseModel):
    """Callers only need to supply video_id. Everything else is resolved from DB."""
    video_id: str = Field(..., description="YouTube video ID")


class TravelClassificationResponse(BaseModel):
    video_id:  str
    is_travel: bool


class VideoFeaturesResponse(BaseModel):
    video_id:      str
    is_travel:     bool
    narrative_ids: List[str] = []
    claim_ids:     List[str] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _present(d: dict) -> dict:
    """Strip None values so we never overwrite existing fields with nulls."""
    return {k: v for k, v in d.items() if v is not None}


def _resolve_video_context(video_id: str) -> dict:
    """
    Builds a unified context dict for the LLM by joining:
      - metadata   → title, tags, language, duration, channel info
      - comments   → top N comments sorted by like_count
    Raises 404 if the video_id is not in metadata.
    """
    # 1. Base info from metadata
    meta = metadata_col.find_one({"video_id": video_id}, {"_id": 0})
    if meta is None:
        raise HTTPException(
            status_code=404,
            detail=f"video_id '{video_id}' not found in metadata collection",
        )

    channel = meta.get("channel") or {}
    stats   = meta.get("stats")   or {}

    # 2. Top comments from comments collection, ranked by like_count
    raw_comments = list(
        comments_col.find(
            {"video_id": video_id},
            {"_id": 0, "text": 1, "like_count": 1},
        )
        .sort("like_count", -1)
        .limit(TOP_COMMENTS_LIMIT)
    )
    top_comments = [c["text"] for c in raw_comments if c.get("text")]

    return {
        # identity
        "video_id":      video_id,
        # LLM inputs
        "title":         meta.get("title", ""),
        "description":   meta.get("description", ""),
        "tags":          meta.get("tags") or [],
        "language":      meta.get("language", ""),
        "duration":      meta.get("duration_seconds"),
        "upload_date":   meta.get("upload_date"),
        "top_comments":  top_comments,
        # channel / creator
        "channel_id":    channel.get("channel_id") or meta.get("channel_id"),
        "channel_title": channel.get("channel_title") or meta.get("channel_title", ""),
        # stats
        "view_count":    stats.get("view_count"),
        "like_count":    stats.get("like_count") or meta.get("likes"),
        "comment_count": stats.get("comment_count") or meta.get("comment_count"),
    }


# ---------------------------------------------------------------------------
# Save monoprompt.py output → correct collections
# ---------------------------------------------------------------------------
def save_features_to_collections(ctx: dict, features: Dict[str, Any]) -> tuple[list, list]:
    """
    Routes every piece of the monoprompt JSON response to its correct collection.

    videos      ← top-level video fields + summary + sentiment
    creators    ← stub upsert (preserves existing data)
    narratives  ← one doc per narrative (with embedding)
    claims      ← one doc per claim    (with embedding)
    """
    now = datetime.now(timezone.utc)
    now_str = now.isoformat() #put it into format to match the database format
    vc  = features.get("video_components") or {}

    video_id   = ctx["video_id"]
    channel_id = ctx.get("channel_id")

    # ── videos ───────────────────────────────────────────────────────────────
    comment_analysis = vc.get("overall_comment_analysis") or {}

    videos_col.update_one(
        {"video_id": video_id},
        {"$set": _present({
            "video_id":      video_id,
            "title":         ctx.get("title"),
            "description":   ctx.get("description"),
            "duration":      ctx.get("duration"),
            #"upload_date":   ctx.get("upload_date"),
            "view_count":    ctx.get("view_count"),
            "like_count":    ctx.get("like_count"),
            "comment_count": ctx.get("comment_count"),
            "tags":          ctx.get("tags"),
            "language":      ctx.get("language"),
            "comments":      ctx.get("top_comments"),
            # LLM-generated fields
            "summary":       vc.get("video_summary"),
            "destinations":  vc.get("video_topics_destinations"),
            "sentiment":     comment_analysis.get("overall_sentiment"),
            "risk_callouts": comment_analysis.get("general_risk_callouts"),
            "is_travel":     True,
            "updated_at":    now,
        })},
        upsert=True,
    )

    # ── creators (stub — preserve existing subscriber/view counts) ────────────
    if channel_id:
        creators_col.update_one(
            {"channel_id": channel_id},
            {"$setOnInsert": _present({
                "channel_id":    channel_id,
                "name":          ctx.get("channel_title"),
                "created_at":    now,
            })},
            upsert=True,
        )

    # ── narratives + claims ───────────────────────────────────────────────────
    narrative_ids: List[str] = []
    claim_ids:     List[str] = []

    # Destinations from the LLM — used to tag each narrative/claim
    destinations = vc.get("video_topics_destinations") or []
    primary_destination = destinations[0] if destinations else None

    for narrative in (vc.get("narratives") or []):
        if not narrative:
            continue

        narrative_id = str(uuid.uuid4())
        narrative_ids.append(narrative_id)

        narratives_col.insert_one(_present({
            "narrative_id":     narrative_id,
            "video_id":         video_id,
            "channel_id":       channel_id,
            # text fields from monoprompt
            "narrative_title":  narrative.get("narrative_title"),
            "narrative_text":   narrative.get("narrative_description"),
            # embedding produced by monoprompt.embed_texts()
            "narrative_vector": narrative.get("narrative_title_embedding"),
            # comment-derived fields
            "comment_summary":  narrative.get("narrative_comment_summary"),
            "risk": _present({
                "sentiment": narrative.get("narrative_comment_risk"),
                "risk_text":  narrative.get("narrative_comment_risk"),
            }) or None,
            # destination tag (matches top_narratives.typeID pattern)
            "destination":      primary_destination,
            "date":             now,
        }))

        for claim in (narrative.get("claims") or []):
            if not claim:
                continue

            claim_id = str(uuid.uuid4())
            claim_ids.append(claim_id)

            claims_col.insert_one(_present({
                "claim_id":     claim_id,
                "narrative_id": narrative_id,
                "video_id":     video_id,
                # text fields from monoprompt
                "claim_title":  claim.get("claim_title"),
                "claim_text":   claim.get("claim_text"),
                # embedding produced by monoprompt.embed_texts()
                "claim_vector": claim.get("claim_title_embedding"),
                # risk / fact-check fields
                "claim_risk":   claim.get("claim_comment_risk"),
                "fact_check":   claim.get("fact_check_assessment"),
                "risks": _present({
                    "sentiment": claim.get("claim_comment_sentiment"),
                    "risk_text": claim.get("claim_comment_risk"),
                }) or None,
                # source = channel, destination tag matches top_claims.country pattern
                "source":       channel_id,
                "destination":  primary_destination,
                "date":         now_str,
            }))

    return narrative_ids, claim_ids


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/classify_travel", response_model=TravelClassificationResponse)
def classify_travel(payload: VideoRequest):
    ctx = _resolve_video_context(payload.video_id)

    try:
        is_travel = classify_is_travel_video(
            video_id=ctx["video_id"],
            channel_title=ctx["channel_title"],
            tags=ctx["tags"],
            title=ctx["title"],
            description=ctx["description"],
            top_comments=ctx["top_comments"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {e}")

    videos_col.update_one(
        {"video_id": ctx["video_id"]},
        {
            "$set":         {"is_travel": is_travel, "updated_at": datetime.now(timezone.utc)},
            "$setOnInsert": {"video_id": ctx["video_id"]},
        },
        upsert=True,
    )

    return TravelClassificationResponse(video_id=ctx["video_id"], is_travel=is_travel)


@app.post("/video_features", response_model=VideoFeaturesResponse)
def video_features(payload: VideoRequest):
    ctx = _resolve_video_context(payload.video_id)

    # 1. Classify
    try:
        is_travel = classify_is_travel_video(
            video_id=ctx["video_id"],
            channel_title=ctx["channel_title"],
            tags=ctx["tags"],
            title=ctx["title"],
            description=ctx["description"],
            top_comments=ctx["top_comments"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {e}")

    if not is_travel:
        videos_col.update_one(
            {"video_id": ctx["video_id"]},
            {"$set": {"video_id": ctx["video_id"], "is_travel": False,
                      "updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )
        return VideoFeaturesResponse(video_id=ctx["video_id"], is_travel=False)

    # 2. Extract features (monoprompt fetches transcript internally)
    try:
        features = extract_video_features_for_video(
            video_id=ctx["video_id"],
            title=ctx["title"],
            description=ctx["description"],
            top_comments=ctx["top_comments"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature extraction error: {e}")

    # 3. Route JSON response to correct collections
    narrative_ids, claim_ids = save_features_to_collections(ctx, features)

    return VideoFeaturesResponse(
        video_id=ctx["video_id"],
        is_travel=True,
        narrative_ids=narrative_ids,
        claim_ids=claim_ids,
    )


@app.get("/video/{video_id}")
def get_video(video_id: str):
    """
    Returns a unified view: metadata + LLM analysis + narratives + claims.
    """
    meta = metadata_col.find_one({"video_id": video_id}, {"_id": 0})
    if meta is None:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")

    # Merge in LLM-generated fields from videos collection
    analysis = videos_col.find_one({"video_id": video_id}, {"_id": 0}) or {}

    # Attach nested narratives + their claims
    narratives = list(narratives_col.find({"video_id": video_id}, {"_id": 0}))
    for n in narratives:
        n["claims"] = list(claims_col.find({"narrative_id": n["narrative_id"]}, {"_id": 0}))

    return {**meta, **analysis, "narratives": narratives}