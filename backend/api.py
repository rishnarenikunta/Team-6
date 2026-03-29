# Run: uvicorn api:app --reload --port 8000

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import Any
from typing import Any, Dict, List, Optional

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
def get_destinations(
    region: Optional[str] = None,
    tag: Optional[str] = None,
) -> List[Dict[str, Any]]:

    REGIONS: Dict[str, List[str]] = {
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


# ── /api/creators/{channel_id}  ───────────────────────────────────────────────

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