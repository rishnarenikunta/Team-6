
#3. Run:  uvicorn api:app --reload --port 8000
#look at how to store information into the mongo tablle -> store the claims and narattives table by using cloud run 
#create just one api endpoint to get the data from the mongo db and display it on the frontend and that api endpoint can have frontend/backend 
#hdb scan on narratives, top_narratives_percreator,country,and overall 

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
    allow_origins=["http://localhost:3000"],  # add your production URL here later
    allow_methods=["*"],
    allow_headers=["*"],
)


client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]

SIGNAL_LABELS = {
    "narrative_momentum": "Narrative momentum",
    "search_interest":    "Search interest",
    "watch_time":         "Watch time",
}

# for claimsCarosol
@app.get("/api/claims/trending")
def get_trending_claims() -> list[dict[str, Any]]:
    """
    Returns all claims where trending=True.
    Shaped to match exactly what ClaimsCarousel expects.
    """
    docs = list(db["claims"].find({"trending": True}))
    return [
        {
            "id":             str(doc["_id"]),
            "text":           doc["claim"],
            "source":         doc.get("source", ""),
            "views":          doc.get("views", ""),
            "engagement":     doc.get("engagement_rate", ""),
            "growth":         doc.get("growth_velocity", ""),
            "destination":    doc.get("destination", ""),
            "verified":       doc.get("verified", False),
        }
        for doc in docs
    ]

# ── /api/destinations  (powers DiscoverPage) ─────────────────────────────────

@app.get("/api/destinations")
def get_destinations(region: str | None = None, tag: str | None = None) -> list[dict[str, Any]]:
    query: dict = {}

    REGIONS: dict[str, list[str]] = {
        "asia":     ["Japan", "South Korea", "Thailand", "Vietnam"],
        "europe":   ["Portugal", "France", "Italy", "Spain", "Germany"],
        "americas": ["Mexico", "USA", "Canada", "Brazil"],
    }

    if region:
        countries = REGIONS.get(region.lower(), [])
        if countries:
            query["country"] = {"$in": countries}

    if tag:
        query["highlights"] = tag.lower()

    docs = list(db["narratives"].find(query))

    results = []
    for doc in docs:
        signal_type  = doc.get("signal_type", "")
        signal_value = doc.get("value", 0)
        label        = SIGNAL_LABELS.get(signal_type, signal_type.replace("_", " ").title())
        results.append({
            "id":          str(doc["_id"]),
            "name":        doc["destination"],
            "country":     doc.get("country", ""),
            "signal":      f"{label} +{signal_value:.0f}%",
            "risk":        doc.get("risk", ""),
            "highlights":  doc.get("highlights", []),
            "blurb":       doc.get("blurb", ""),
            "refreshedAt": doc["refreshed_at"].isoformat() if doc.get("refreshed_at") else None,
        })
    return results

# ── /api/destinations/{name}  (destination detail) ───────────────────────────

@app.get("/api/destinations/{destination_name}")
def get_destination(destination_name: str) -> dict[str, Any]:
    doc = db["narratives"].find_one({"destination": {"$regex": destination_name, "$options": "i"}})
    if not doc:
        raise HTTPException(status_code=404, detail="Destination not found")

    claims = list(
        db["claims"].find(
            {"destination": doc["destination"]},
            {"_id": 0, "claim": 1, "verified": 1, "source": 1}
        )
    )

    signal_type  = doc.get("signal_type", "")
    signal_value = doc.get("value", 0)
    label        = SIGNAL_LABELS.get(signal_type, signal_type.replace("_", " ").title())

    return {
        "id":          str(doc["_id"]),
        "name":        doc["destination"],
        "country":     doc.get("country", ""),
        "signal":      f"{label} +{signal_value:.0f}%",
        "risk":        doc.get("risk", ""),
        "highlights":  doc.get("highlights", []),
        "blurb":       doc.get("blurb", ""),
        "claims":      claims,
        "refreshedAt": doc["refreshed_at"].isoformat() if doc.get("refreshed_at") else None,
    }

print("Total claims:", db["claims"].count_documents({}))
print("Trending claims:", db["claims"].count_documents({"trending": True}))