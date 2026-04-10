# Run: uvicorn api:app --reload --port 8000

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import Any, Optional

load_dotenv()

app = FastAPI(title="Travel App API")

live_frontend = os.getenv("FRONTEND_URL")
origins = ["http://localhost:3000"]
if live_frontend:
    origins.append(live_frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]


# ── /api/claims/trending ──────────────────────────────────────────────────────
# Returns top claims per destination from the top_narratives cluster results

@app.get("/api/claims/trending")
def get_trending_claims() -> list[dict[str, Any]]:
    docs = list(db["top_claims"].find({}))

    # Build a creator lookup map
    creators = list(db["creators"].find({}, {"_id": 0}))
    creator_map = {c["channel_id"]: c for c in creators}

    result = [
        {
            "id":           str(doc["_id"]),
            "text":         doc.get("claimText", ""),
            "destination":  doc.get("country", ""),
            "cluster_size": doc.get("clusterSize", 0),
            "computed_at":  doc["computedAt"].isoformat() if doc.get("computedAt") else None,
            # Join creator info
            "source":       doc.get("creatorID", ""),
            "creator_name": creator_map.get(doc.get("creatorID", ""), {}).get("name", ""),
            "views":        creator_map.get(doc.get("creatorID", ""), {}).get("views", 0),
        }
        for doc in docs
    ]
    print("TRENDING CLAIMS RESPONSE:")
    print(result)

    return result

@app.get("/api/topics/trending")
def get_trending_topics() -> dict:
    # Pull distinct destinations or tags from your DB
    destinations = db["narratives"].distinct("destination")
    return {"topics": destinations}
@app.get("/api/narratives/trending")
def get_trending_narratives() -> list[dict[str, Any]]:
    docs = list(
        db["top_narratives"]
        .find({})
        .sort("clusterSize", -1)   # sort by largest clusters first
        .limit(7)                  # only take top 7
    )


    creators = list(db["creators"].find({}, {"_id": 0}))
    creator_map = {c["channel_id"]: c for c in creators}

    result = [
        {
            "id":           str(doc["_id"]),
            "text":         doc.get("narrative", ""),
            "destination":  doc.get("typeID", ""),
            "cluster_size": doc.get("clusterSize", 0),
            "computed_at":  doc["computedAt"].isoformat() if doc.get("computedAt") else None,
            "source":       doc.get("channel_id", ""),
            "creator_name": creator_map.get(doc.get("channel_id", ""), {}).get("name", ""),
            "views":        creator_map.get(doc.get("channel_id", ""), {}).get("views", 0),
        }
        for doc in docs
    ]

    print("TRENDING NARRATIVES RESPONSE:")
    print(result)

    return result

@app.get("/api/destinations")
def get_destinations(region: Optional[str]= None, tag: Optional[str]= None) -> list[dict[str, Any]]:

    REGIONS: dict[str, list[str]] = {
        "asia":     ["Japan", "South Korea", "Thailand", "Vietnam"],
        "europe":   ["Portugal", "France", "Italy", "Spain", "Germany"],
        "americas": ["Mexico", "USA", "Canada", "Brazil"],
    }

    # Get all unique destinations from narratives
    match: dict = {}
    if region:
        countries = REGIONS.get(region.lower(), [])
        if countries:
            # Filter narratives by country — need to join with a lookup
            # since country is not stored in new seed; filter by known destination lists
            dest_by_region = {
                "asia":     ["Kyoto", "Tokyo", "Seoul"],
                "europe":   ["Lisbon"],
                "americas": [],
            }
            allowed = dest_by_region.get(region.lower(), [])
            if allowed:
                match["destination"] = {"$in": allowed}

    if tag:
        match["highlights"] = tag.lower()

    # Get one representative narrative per destination from top_narratives
    top_query: dict = {"scope_type": "destination", "content_type": "narratives"}
    top_docs = list(db["top_narratives"].find(top_query))
    top_by_dest = {doc["destination_id"]: doc for doc in top_docs}

    # Get all destinations that have narratives
    all_destinations = db["narratives"].distinct("destination", match)

    results = []
    for dest in all_destinations:
        top = top_by_dest.get(dest)
        # Fall back to any raw narrative if cluster hasn't run yet
        if not top:
            raw = db["narratives"].find_one({"destination": dest})
            if not raw:
                continue
            results.append({
                "id":          str(raw["_id"]),
                "name":        dest,
                "blurb":       raw.get("narrative_text", ""),
                "top_narrative": None,
                "cluster_size": None,
                "computed_at": None,
            })
        else:
            results.append({
                "id":            str(top["_id"]),
                "name":          dest,
                "blurb":         top.get("top_narrative", ""),
                "top_narrative": top.get("top_narrative", ""),
                "cluster_size":  top.get("cluster_size", 0),
                "computed_at":   top["computed_at"].isoformat() if top.get("computed_at") else None,
            })

    return results



# ── /api/creators  ────────────────────────────────────────────────────────────
# Returns all creators with their top claim narrative from cluster results

@app.get("/api/creators")
def get_creators() -> list[dict[str, Any]]:
    creators = list(db["creators"].find({}, {"_id": 0}))

    # ── 2. Fetch all metadata and group videos by channel.channel_id ──────────
    all_meta = list(
        db["metadata"].find(
            {},
            {
                "_id": 0, 
                "video_id": 1,
                "title": 1,
                "webpage_url": 1,
                "channel": 1,
                "stats": 1,
                "upload_date": 1,
                },
        )
    )

    videos_by_channel: dict[str, list] = {}
    for m in all_meta:
        channel_id = m.get("channel", {}).get("channel_id", "")
        if not channel_id:
            continue
        videos_by_channel.setdefault(channel_id, []).append(m)

    # ── 3. Assemble results ───────────────────────────────────────────────────
    results = []
    for creator in creators:
        cid    = creator.get("channel_id", "")
        videos = videos_by_channel.get(cid, [])

        video_list = [
            {
                "video_id":      v.get("video_id", ""),
                "title":         v.get("title", ""),
                "view_count":    v.get("stats", {}).get("view_count"),
                "like_count":    v.get("stats", {}).get("like_count"),
                "comment_count": v.get("stats", {}).get("comment_count"),
                "webpage_url":   v.get("webpage_url", ""),
                "upload_date":   v.get("upload_date", ""),
            }
            for v in videos
        ]

        comment_volume = sum(
            v.get("stats", {}).get("comment_count", 0) or 0
            for v in videos
        )

        results.append({
            "channel_id":       cid,
            "creator_name":     creator.get("name", ""),
            "subscriber_count": creator.get("subscriber_count", 0),
            "views":            creator.get("views", 0),
            "comment_volume":   comment_volume,
            "videos":           video_list,
        })

    return results


# ── /api/creators/{channel_id}  ───────────────────────────────────────────────

@app.get("/api/creators/{channel_id}")
def get_creator(channel_id: str) -> dict[str, Any]:

    # ── 1. Fetch the creator ──────────────────────────────────────────────────
    creator = db["creators"].find_one({"channel_id": channel_id}, {"_id": 0})
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    # ── 2. Fetch all metadata for this creator (join on channel.channel_id) ───
    meta_docs = list(
        db["metadata"].find(
            {"channel.channel_id": channel_id},
            {
                "_id": 0,
                "video_id": 1,
                "title": 1,
                "webpage_url": 1,
                "stats": 1,
                "upload_date": 1,
            },
        )
    )

    video_list = [
        {
            "video_id":      v.get("video_id", ""),
            "title":         v.get("title", ""),
            "view_count":    v.get("stats", {}).get("view_count"),
            "like_count":    v.get("stats", {}).get("like_count"),
            "comment_count": v.get("stats", {}).get("comment_count"),
            "webpage_url":   v.get("webpage_url", ""),
            "upload_date":   v.get("upload_date", ""),
        }
        for v in meta_docs
    ]

    comment_volume = sum(
        v.get("stats", {}).get("comment_count", 0) or 0
        for v in meta_docs
    )

    # ── 3. Fetch trending narratives from top_narratives ──────────────────────
    # join on typeID = channel_id and type = "creator"
    narrative_docs = list(
        db["top_narratives"].find(
            {"typeID": channel_id, "type": "creator"},
            {"_id": 0},
        )
    )

    trending_narratives = [
        {
            "narrative_id":  doc.get("narrativeID"),
            "narrative":     doc.get("narrative"),
            "cluster_size":  doc.get("clusterSize"),
            "video_id":      doc.get("video_id"),
            "computed_at":   doc["computedAt"].isoformat() if doc.get("computedAt") else None,
            "total_docs":    doc.get("totalDocs", 0),
        }
        for doc in narrative_docs
    ]

    # ── 4. Fetch trending claims from top_claims ───────────────────────────────
    # join on typeID = channel_id and type = "creator"
    claim_docs = list(
        db["top_claims"].find(
            {"typeID": channel_id, "type": "creator"},
            {"_id": 0},
        )
    )

    trending_claims = [
        {
        "claim_id":    str(doc["claimID"]) if doc.get("claimID") else None,  # ✅
        "claim_text":  doc.get("claimText"),
        "cluster_size": doc.get("clusterSize"),
        "computed_at": doc["computedAt"].isoformat() if doc.get("computedAt") else None,
        "total_docs":  doc.get("totalDocs", 0),
    }
    for doc in claim_docs
    ]

    # ── 5. Assemble response ──────────────────────────────────────────────────
    return {
        "channel_id":        channel_id,
        "creator_name":      creator.get("name", ""),
        "subscriber_count":  creator.get("subscriber_count", 0),
        "views":             creator.get("views", 0),
        "comment_volume":    comment_volume,
        "videos":            video_list,
        "trending_narratives": trending_narratives,
        "trending_claims":     trending_claims,
    }


print("Total narratives:", db["narratives"].count_documents({}))
print("Total claims:",     db["claims"].count_documents({}))
print("Top narratives computed:", db["top_narratives"].count_documents({}))
print("Top claims computed:", db["top_claims"].count_documents({}))


from math import floor


# ── /api/stats/main ──────────────────────────────────────────────────────────
# Powers StatsMain.tsx
# Returns: topDestination, active narratives count, total claims, trending
#          creator count, and creator tier breakdown.

@app.get("/api/stats/main")
def get_main_stats() -> dict[str, Any]:

    # ── Destination popularity: count narratives per destination ──────────────
    dest_pipeline = [
        {"$group": {"_id": "$destination", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    dest_counts = list(db["narratives"].aggregate(dest_pipeline))

    top_dest_name   = dest_counts[0]["_id"]   if dest_counts else "Unknown"
    top_dest_count  = dest_counts[0]["count"] if dest_counts else 0
    second_count    = dest_counts[1]["count"] if len(dest_counts) > 1 else 0

    # Growth = how many more narratives top dest has vs #2, expressed as %
    if second_count > 0:
        growth_pct = round((top_dest_count - second_count) / second_count * 100, 1)
    else:
        growth_pct = 100.0

    top_destination = {
        "name":   top_dest_name,
        "growth": growth_pct,        # e.g. 25.0  → "25% more narratives than #2"
    }

    # ── Narrative & claim counts ──────────────────────────────────────────────
    active_narratives = db["narratives"].count_documents({})
    total_claims      = db["claims"].count_documents({})

    # ── Creator tiers ─────────────────────────────────────────────────────────
    # Micro: 0–50K  |  Mid: 50K–500K  |  Large: 500K–1M  |  Enterprise: 1M+
    all_creators = list(db["creators"].find({}, {"_id": 0, "subscriber_count": 1}))
    total_creators = len(all_creators)

    tiers = {"micro": 0, "mid_tier": 0, "large": 0, "enterprise": 0}
    for c in all_creators:
        subs = c.get("subscriber_count", 0)
        if subs < 50_000:
            tiers["micro"] += 1
        elif subs < 500_000:
            tiers["mid_tier"] += 1
        elif subs < 1_000_000:
            tiers["large"] += 1
        else:
            tiers["enterprise"] += 1

    def pct(n):
        return round(n / total_creators * 100, 1) if total_creators else 0

    creator_insights = {
        "total": total_creators,
        "tiers": {
            "micro":      {"count": tiers["micro"],      "pct": pct(tiers["micro"])},
            "mid_tier":   {"count": tiers["mid_tier"],   "pct": pct(tiers["mid_tier"])},
            "large":      {"count": tiers["large"],      "pct": pct(tiers["large"])},
            "enterprise": {"count": tiers["enterprise"], "pct": pct(tiers["enterprise"])},
        },
    }

    # ── Trending creators = creators who have a top_narrative entry ───────────
    trending_creator_count = db["top_narratives"].distinct("channel_id")
    trending_creators_n    = len(trending_creator_count)

    return {
        "top_destination":      top_destination,
        "active_narratives":    active_narratives,
        "total_claims":         total_claims,
        "trending_creators":    trending_creators_n,
        "creator_insights":     creator_insights,
    }


# ── /api/narratives ──────────────────────────────────────────────────────────
# Powers /narratives/page.tsx  — paginated list of all narratives
# Query params: destination (optional filter), limit, offset

@app.get("/api/narratives")
def list_narratives(
    destination: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:

    match: dict = {}
    if destination:
        match["destination"] = {"$regex": destination, "$options": "i"}

    total = db["narratives"].count_documents(match)
    docs  = list(
        db["narratives"]
        .find(match, {"narrative_vector": 0})   # omit heavy vector field
        .sort("date", -1)
        .skip(offset)
        .limit(limit)
    )

    # Enrich with creator name
    creators     = list(db["creators"].find({}, {"_id": 0}))
    creator_map  = {c["channel_id"]: c for c in creators}

    items = [
        {
            "id":           str(doc["_id"]),
            "narrative_id": doc.get("narrative_id", ""),
            "text":         doc.get("narrative_text", ""),
            "destination":  doc.get("destination", ""),
            "date":         doc["date"].isoformat() if doc.get("date") else None,
            "channel_id":   doc.get("channel_id", ""),
            "creator_name": creator_map.get(doc.get("channel_id", ""), {}).get("name", ""),
            # slug = narrative_id (e.g. "narr_kyoto_01") used for detail URL
            "slug":         doc.get("narrative_id", str(doc["_id"])),
        }
        for doc in docs
    ]

    return {"total": total, "offset": offset, "limit": limit, "items": items}

# ── /api/narratives/enriched ─────────────────────────────────────────────────
# Returns all narratives enriched with:
#   - claims joined on narrative_id
#   - metadata tags + sentiment label
#   - slug field (= narrative_id)

@app.get("/api/narratives/enriched")
def get_narratives_enriched() -> list[dict[str, Any]]:

    # ── 1. Fetch all narratives ───────────────────────────────────────────────
    narratives = list(db["narratives"].find({}, {"narrative_vector": 0}))

    # ── 2. Build claims lookup keyed by narrative_id ──────────────────────────
    all_claims = list(
        db["claims"].find(
            {},
            {"_id": 0, "narrative_id": 1, "claim_text": 1, "claim_risk": 1, "source": 1, "date": 1},
        )
    )
    claims_by_narrative: dict[str, list] = {}
    for claim in all_claims:
        nid = claim.get("narrative_id", "")
        claims_by_narrative.setdefault(nid, []).append({
            "claim_text": claim.get("claim_text", ""),
            "claim_risk": claim.get("claim_risk", ""),
            "source":     claim.get("source", ""),
            "date":       claim.get("date", ""),
        })

    # ── 3. Build metadata lookup keyed by video_id ────────────────────────────
    all_meta = list(
        db["metadata"].find(
            {},
            {"_id": 0, "video_id": 1, "tags": 1, "sentiment": 1, "title": 1, "upload_date": 1, "webpage_url": 1},
        )
    )
    meta_by_video: dict[str, dict] = {m["video_id"]: m for m in all_meta if m.get("video_id")}

    # ── 4. Assemble enriched records ──────────────────────────────────────────
    results = []
    for doc in narratives:
        narrative_id = doc.get("narrative_id", "")
        video_id     = doc.get("video_id", "")
        meta         = meta_by_video.get(video_id, {})

        raw_sentiment = meta.get("sentiment")
        if raw_sentiment is None:
            sentiment_label = None
        elif raw_sentiment >= 0.66:
            sentiment_label = "positive"
        elif raw_sentiment <= 0.33:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        results.append({
            "slug":           narrative_id,          # <── slug as a field
            "narrative_id":   narrative_id,
            "video_id":       video_id,
            "destination":    doc.get("destination", ""),
            "channel_id":     doc.get("channel_id", ""),
            "narrative_text": doc.get("narrative_text", ""),
            "date":           doc["date"].isoformat() if doc.get("date") else None,
            "claims":         claims_by_narrative.get(narrative_id, []),
            "metadata": {
                "tags":            meta.get("tags", []),
                "sentiment_score": raw_sentiment,
                "sentiment":       sentiment_label,
                "title":           meta.get("title", ""),
                "upload_date":     meta.get("upload_date", ""),
                "webpage_url":     meta.get("webpage_url", ""),
            },
        })

    return results


# ── /api/narratives/enriched/full ────────────────────────────────────────────
# All narratives enriched with claims, metadata, and video stats

@app.get("/api/narratives/enriched/video_details")
def get_narratives_enriched_videoDetails() -> list[dict[str, Any]]:

    # ── 1. Fetch all narratives ───────────────────────────────────────────────
    narratives = list(db["narratives"].find({}, {"narrative_vector": 0}))

    # ── 2. Build claims lookup keyed by narrative_id ──────────────────────────
    all_claims = list(
        db["claims"].find(
            {},
            {"_id": 0, "narrative_id": 1, "claim_text": 1, "claim_risk": 1, "source": 1, "date": 1},
        )
    )
    claims_by_narrative: dict[str, list] = {}
    for claim in all_claims:
        nid = claim.get("narrative_id", "")
        claims_by_narrative.setdefault(nid, []).append({
            "claim_text": claim.get("claim_text", ""),
            "claim_risk": claim.get("claim_risk", ""),
            "source":     claim.get("source", ""),
            "date":       claim.get("date", ""),
        })

    # ── 3. Build metadata lookup keyed by video_id ────────────────────────────
    all_meta = list(
        db["metadata"].find(
            {},
            {
                "_id": 0,
                "video_id": 1,
                "tags": 1,
                "sentiment": 1,
                "title": 1,
                "upload_date": 1,
                "webpage_url": 1,
                "risk_callouts": 1,
                "stats": 1,
            },
        )
    )
    meta_by_video: dict[str, dict] = {m["video_id"]: m for m in all_meta if m.get("video_id")}

    # ── 4. Shared helper: sentiment label ─────────────────────────────────────
    def sentiment_label(score) -> str | None:
        if score is None:
            return None
        if score >= 0.66:
            return "positive"
        if score <= 0.33:
            return "negative"
        return "neutral"

    # ── 5. Shared helper: risk_callouts — filter out "None" placeholders ──────
    def parse_risk_callouts(raw: list) -> list[str]:
        return [r for r in (raw or []) if r and r.strip().lower() != "none"]

    # ── 6. Assemble enriched records ──────────────────────────────────────────
    results = []
    for doc in narratives:
        narrative_id  = doc.get("narrative_id", "")
        video_id      = doc.get("video_id", "")
        meta          = meta_by_video.get(video_id, {})
        stats         = meta.get("stats", {})
        raw_sentiment = meta.get("sentiment")

        results.append({
            "slug":           narrative_id,
            "narrative_id":   narrative_id,
            "video_id":       video_id,
            "destination":    doc.get("destination", ""),
            "channel_id":     doc.get("channel_id", ""),
            "narrative_text": doc.get("narrative_text", ""),
            "date":           doc["date"].isoformat() if doc.get("date") else None,
            "claims":         claims_by_narrative.get(narrative_id, []),
            "metadata": {
                "tags":            meta.get("tags", []),
                "sentiment_score": raw_sentiment,
                "sentiment":       sentiment_label(raw_sentiment),
                "title":           meta.get("title", ""),
                "upload_date":     meta.get("upload_date", ""),
                "webpage_url":     meta.get("webpage_url", ""),
                "risk_callouts":   parse_risk_callouts(meta.get("risk_callouts", [])),
            },
            "video_stats": {
                "view_count":    stats.get("view_count"),
                "like_count":    stats.get("like_count"),
                "comment_count": stats.get("comment_count"),
            },
        })

    return results


# ── /api/narratives/enriched/full/{narrative_id} ─────────────────────────────
# Same shape as above but for a single narrative

@app.get("/api/narratives/enriched/video_details/{narrative_id}")
def get_narrative_enriched_videoDetails(narrative_id: str) -> dict[str, Any]:

    # ── 1. Fetch the narrative ────────────────────────────────────────────────
    doc = db["narratives"].find_one(
        {"narrative_id": narrative_id},
        {"narrative_vector": 0},
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Narrative not found")

    video_id = doc.get("video_id", "")

    # ── 2. Fetch claims joined on narrative_id ────────────────────────────────
    claims = [
        {
            "claim_text": c.get("claim_text", ""),
            "claim_risk": c.get("claim_risk", ""),
            "source":     c.get("source", ""),
            "date":       c.get("date", ""),
        }
        for c in db["claims"].find(
            {"narrative_id": narrative_id},
            {"_id": 0, "claim_text": 1, "claim_risk": 1, "source": 1, "date": 1},
        )
    ]

    # ── 3. Fetch metadata by video_id ─────────────────────────────────────────
    meta = db["metadata"].find_one(
        {"video_id": video_id},
        {
            "_id": 0,
            "tags": 1,
            "sentiment": 1,
            "title": 1,
            "upload_date": 1,
            "webpage_url": 1,
            "risk_callouts": 1,
            "stats": 1,
        },
    ) or {}

    stats = meta.get("stats", {})

    # ── 4. Sentiment label ────────────────────────────────────────────────────
    raw_sentiment = meta.get("sentiment")
    if raw_sentiment is None:
        sentiment = None
    elif raw_sentiment >= 0.66:
        sentiment = "positive"
    elif raw_sentiment <= 0.33:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # ── 5. Risk callouts — strip "None" placeholders ──────────────────────────
    risk_callouts = [
        r for r in meta.get("risk_callouts", [])
        if r and r.strip().lower() != "none"
    ]

    return {
        "slug":           narrative_id,
        "narrative_id":   narrative_id,
        "video_id":       video_id,
        "destination":    doc.get("destination", ""),
        "channel_id":     doc.get("channel_id", ""),
        "narrative_text": doc.get("narrative_text", ""),
        "date":           doc["date"].isoformat() if doc.get("date") else None,
        "claims":         claims,
        "metadata": {
            "tags":            meta.get("tags", []),
            "sentiment_score": raw_sentiment,
            "sentiment":       sentiment,
            "title":           meta.get("title", ""),
            "upload_date":     meta.get("upload_date", ""),
            "webpage_url":     meta.get("webpage_url", ""),
            "risk_callouts":   risk_callouts,
        },
        "video_stats": {
            "view_count":    stats.get("view_count"),
            "like_count":    stats.get("like_count"),
            "comment_count": stats.get("comment_count"),
        },
    }




# ── /api/narratives/{slug} ───────────────────────────────────────────────────
# Powers /narratives/[slug]/page.tsx — single narrative detail

@app.get("/api/narratives/{slug}")
def get_narrative_detail(slug: str) -> dict[str, Any]:

    doc = db["narratives"].find_one(
        {"narrative_id": slug},
        {"narrative_vector": 0},
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Narrative not found")

    destination = doc.get("destination", "")
    channel_id  = doc.get("channel_id", "")

    creator = db["creators"].find_one({"channel_id": channel_id}, {"_id": 0}) or {}

    # ── Fetch video metadata using video_id from the narrative ────────────────
    video_id = doc.get("video_id", "")
    meta = db["metadata"].find_one(
        {"video_id": video_id},
        {"_id": 0, "webpage_url": 1, "views": 1, "upload_date": 1, "channel_url": 1}
    ) or {}

    related_claims = list(
        db["claims"].find(
            {"destination": destination},
            {"_id": 0, "claim_text": 1, "source": 1, "claim_risk": 1, "date": 1},
        ).limit(10)
    )

    cluster = db["top_narratives"].find_one({
        "destination_id": destination,
        "scope_type": "destination",
        "content_type": "narratives",
    })

    siblings = list(
        db["narratives"].find(
            {"destination": destination, "narrative_id": {"$ne": slug}},
            {"narrative_id": 1, "narrative_text": 1},
        ).limit(5)
    )

    return {
        "id":             str(doc["_id"]),
        "narrative_id":   doc.get("narrative_id", ""),
        "slug":           slug,
        "text":           doc.get("narrative_text", ""),
        "destination":    destination,
        "date":           doc["date"].isoformat() if doc.get("date") else None,
        "channel_id":     channel_id,
        "creator_name":   creator.get("name", ""),
        "creator_subs":   creator.get("subscriber_count", 0),
        "creator_views":  creator.get("views", 0),
        "cluster_size":   cluster.get("clusterSize") if cluster else None,
        "top_narrative":  cluster.get("narrative") if cluster else None,
        "related_claims": related_claims,
        "related_narratives": [
            {"slug": s["narrative_id"], "text": s["narrative_text"]}
            for s in siblings
        ],
        # ── video fields from metadata collection ─────────────────────────────
        "video_id":        video_id,
        "video_url":       meta.get("webpage_url", ""),
        "video_views":     meta.get("views", 0),
        "video_published": meta.get("upload_date", ""),   # keep as-is (likely already a string like "20240101")
        "video_channel":   meta.get("channel_url", ""),
    }


# ── /api/destinations/top ────────────────────────────────────────────────────
# Powers TopCountries.tsx
# Returns destinations ranked by narrative count with claim count included

@app.get("/api/destinations/top")
def get_top_destinations(limit: int = 10) -> list[dict[str, Any]]:

    pipeline = [
        {"$group": {"_id": "$destination", "narrative_count": {"$sum": 1}}},
        {"$sort": {"narrative_count": -1}},
        {"$limit": limit},
    ]
    dest_groups = list(db["narratives"].aggregate(pipeline))

    # Claim counts per destination
    claim_pipeline = [
        {"$group": {"_id": "$destination", "claim_count": {"$sum": 1}}},
    ]
    claim_groups = list(db["claims"].aggregate(claim_pipeline))
    claim_map = {g["_id"]: g["claim_count"] for g in claim_groups}

    results = []
    for g in dest_groups:
        dest = g["_id"]
        results.append({
            "name":            dest,
            "narrative_count": g["narrative_count"],
            "claim_count":     claim_map.get(dest, 0),
            # Simple growth proxy: share of total narratives (%)
            "share_pct": None,   # filled below
        })

    total_narratives = sum(r["narrative_count"] for r in results)
    for r in results:
        r["share_pct"] = round(r["narrative_count"] / total_narratives * 100, 1) if total_narratives else 0

    return results


# ── /api/destinations/trending-locations ─────────────────────────────────────
# Powers TrendingLocations.tsx
# Top 3 destinations + simulated monthly mention timeline
# (Since we don't store time-series data, we bucket existing docs by month)

@app.get("/api/destinations/trending-locations")
def get_trending_locations() -> list[dict[str, Any]]:

    # Top 3 destinations by narrative count
    pipeline = [
        {"$group": {"_id": "$destination", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 3},
    ]
    top3 = list(db["narratives"].aggregate(pipeline))

    results = []
    for item in top3:
        dest = item["_id"]

        # Mentions over time: group narratives by year-month
        time_pipeline = [
            {"$match": {"destination": dest}},
            {
                "$group": {
                    "_id": {
                        "year":  {"$year": "$date"},
                        "month": {"$month": "$date"},
                    },
                    "mentions": {"$sum": 1},
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]
        time_docs = list(db["narratives"].aggregate(time_pipeline))

        timeline = [
            {
                "period": f"{t['_id']['year']}-{t['_id']['month']:02d}",
                "mentions": t["mentions"],
            }
            for t in time_docs
        ]

        results.append({
            "name":     dest,
            "total":    item["count"],
            "timeline": timeline,
        })

    return results

# ── /api/destinations/{name}  ─────────────────────────────────────────────────
# Destination detail page — top narrative + all raw claims for that destination

@app.get("/api/destinations/{destination_name}")
def get_destination(destination_name: str) -> dict[str, Any]:

    # Find top narrative for this destination
    top = db["top_narratives"].find_one({
        "destination_id": {"$regex": destination_name, "$options": "i"},
        "scope_type": "destination",
        "content_type": "narratives"
    })

    # Fall back to raw narrative if cluster hasn't run
    if not top:
        raw = db["narratives"].find_one(
            {"destination": {"$regex": destination_name, "$options": "i"}}
        )
        if not raw:
            raise HTTPException(status_code=404, detail="Destination not found")
        dest_name = raw["destination"]
        blurb = raw.get("narrative_text", "")
        cluster_size = None
        computed_at = None
        doc_id = str(raw["_id"])
    else:
        dest_name = top["destination_id"]
        blurb = top.get("top_narrative", "")
        cluster_size = top.get("cluster_size")
        computed_at = top["computed_at"].isoformat() if top.get("computed_at") else None
        doc_id = str(top["_id"])

    # Get all claims for this destination
    claims = list(
        db["claims"].find(
            {"destination": dest_name},
            {"_id": 0, "claim_text": 1, "source": 1, "claim_risk": 1, "date": 1}
        )
    )

    # Get top claim from cluster results
    top_claim = db["top_narratives"].find_one({
        "destination_id": dest_name,
        "scope_type": "destination",
        "content_type": "claims"
    })

    return {
        "id":            doc_id,
        "name":          dest_name,
        "blurb":         blurb,
        "cluster_size":  cluster_size,
        "computed_at":   computed_at,
        "top_claim":     top_claim.get("top_narrative") if top_claim else None,
        "claims":        claims,
    }