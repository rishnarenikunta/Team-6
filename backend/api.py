# Run: uvicorn api:app --reload --port 8000

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import Any

load_dotenv()

app = FastAPI(title="Travel App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
def get_destinations(region: str | None = None, tag: str | None = None) -> list[dict[str, Any]]:

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

    top_docs = list(db["top_narratives"].find({
        "scope_type": "source",
        "content_type": "claims"
    }))
    top_by_creator = {doc["channel_id"]: doc for doc in top_docs}

    results = []
    for creator in creators:
        cid = creator["channel_id"]
        top = top_by_creator.get(cid)
        results.append({
            "channel_id":      cid,
            "name":            creator.get("name", ""),
            "subscriber_count": creator.get("subscriber_count", 0),
            "views":           creator.get("views", 0),
            "top_claim":       top.get("top_narrative") if top else None,
            "cluster_size":    top.get("cluster_size") if top else None,
            "computed_at":     top["computed_at"].isoformat() if top and top.get("computed_at") else None,
        })

    return results


# ── /api/creators/{channel_id}  ──────-─────────────────────────────────────────

@app.get("/api/creators/{channel_id}")
def get_creator(channel_id: str) -> dict[str, Any]:
    creator = db["creators"].find_one({"channel_id": channel_id}, {"_id": 0})
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    top = db["top_narratives"].find_one({
        "channel_id": channel_id,
        "scope_type": "source",
        "content_type": "claims"
    })

    claims = list(
        db["claims"].find(
            {"source": channel_id},
            {"_id": 0, "claim_text": 1, "destination": 1, "claim_risk": 1, "date": 1}
        )
    )

    return {
        "channel_id":       channel_id,
        "name":             creator.get("name", ""),
        "subscriber_count": creator.get("subscriber_count", 0),
        "views":            creator.get("views", 0),
        "join_date":        creator["join_date"].isoformat() if creator.get("join_date") else None,
        "top_claim":        top.get("top_narrative") if top else None,
        "cluster_size":     top.get("cluster_size") if top else None,
        "computed_at":      top["computed_at"].isoformat() if top and top.get("computed_at") else None,
        "claims":           claims,
    }


print("Total narratives:", db["narratives"].count_documents({}))
print("Total claims:",     db["claims"].count_documents({}))
print("Top narratives computed:", db["top_narratives"].count_documents({}))
print("Top claims computed:", db["top_claims"].count_documents({}))

# ─────────────────────────────────────────────────────────────────────────────
# NEW ENDPOINTS — paste these into api.py
# ─────────────────────────────────────────────────────────────────────────────

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


# ── /api/narratives/{slug} ───────────────────────────────────────────────────
# Powers /narratives/[slug]/page.tsx — single narrative detail

@app.get("/api/narratives/{slug}")
def get_narrative_detail(slug: str) -> dict[str, Any]:

    # slug = narrative_id value (e.g. "narr_kyoto_01")
    doc = db["narratives"].find_one(
        {"narrative_id": slug},
        {"narrative_vector": 0},
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Narrative not found")

    destination = doc.get("destination", "")
    channel_id  = doc.get("channel_id", "")

    creator = db["creators"].find_one({"channel_id": channel_id}, {"_id": 0}) or {}

    # Related claims for the same destination
    related_claims = list(
        db["claims"].find(
            {"destination": destination},
            {"_id": 0, "claim_text": 1, "source": 1, "claim_risk": 1, "date": 1},
        ).limit(10)
    )

    # Top cluster result for this destination (if available)
    cluster = db["top_narratives"].find_one({
        "destination_id": destination,
        "scope_type": "destination",
        "content_type": "narratives",
    })

    # Other narratives for same destination (siblings)
    siblings = list(
        db["narratives"].find(
            {"destination": destination, "narrative_id": {"$ne": slug}},
            {"narrative_vector": 0, "_id": 0, "narrative_id": 1, "narrative_text": 1},
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

