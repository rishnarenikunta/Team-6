"""
backend/seed.py
Run once to populate MongoDB: python seed.py
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]

# ── Validators ────────────────────────────────────────────────────────────────

video_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "destination", "published_at"],
        "properties": {
            "title":            {"bsonType": "string"},
            "destination":      {"bsonType": "string"},
            "watch_time_hours": {"bsonType": "double"},
            "views":            {"bsonType": "int"},
            "published_at":     {"bsonType": "date"},
        },
    }
}

creator_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "channel_id"],
        "properties": {
            "name":        {"bsonType": "string"},
            "channel_id":  {"bsonType": "string"},
            "subscribers": {"bsonType": "int"},
            "risk_tier":   {"enum": ["low", "moderate", "high"]},
        },
    }
}

narrative_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["destination", "signal_type", "value", "refreshed_at"],
        "properties": {
            "destination":  {"bsonType": "string"},
            "country":      {"bsonType": "string"},
            "signal_type":  {"enum": ["narrative_momentum", "search_interest", "watch_time"]},
            "value":        {"bsonType": "double"},
            "risk":         {"bsonType": "string"},
            "highlights":   {"bsonType": "array"},
            "blurb":        {"bsonType": "string"},
            "refreshed_at": {"bsonType": "date"},
        },
    }
}

# claims now has carousel-specific fields: source, views, engagement_rate,
# growth_velocity, and trending (bool) to flag carousel-worthy claims
claims_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["destination", "claim", "source"],
        "properties": {
            "destination":     {"bsonType": "string"},
            "claim":           {"bsonType": "string"},
            "source":          {"bsonType": "string"},
            "views":           {"bsonType": "string"},   # "842K"
            "engagement_rate": {"bsonType": "string"},   # "9.8%"
            "growth_velocity": {"bsonType": "string"},   # "+37%"
            "verified":        {"bsonType": "bool"},
            "trending":        {"bsonType": "bool"},     # true → ClaimsCarousel
        },
    }
}

# ── Create / update collections ───────────────────────────────────────────────

existing = db.list_collection_names()

for name, validator in [
    ("videos",     video_validator),
    ("creators",   creator_validator),
    ("narratives", narrative_validator),
    ("claims",     claims_validator),
]:
    if name not in existing:
        db.create_collection(name, validator=validator)
        print(f"✅ Created: {name}")
    else:
        db.command("collMod", name, validator=validator)
        print(f"↩  Exists (validator refreshed): {name}")

# ── Creators ──────────────────────────────────────────────────────────────────

creators_col = db["creators"]
if creators_col.count_documents({}) == 0:
    creators_col.insert_many([
        {"name": "WonderWithMia",     "channel_id": "UC_mia_01",   "subscribers": 980000,  "risk_tier": "low"},
        {"name": "TravelTomo",        "channel_id": "UC_tomo_01",  "subscribers": 450000,  "risk_tier": "low"},
        {"name": "NomadNick",         "channel_id": "UC_nick_01",  "subscribers": 2100000, "risk_tier": "low"},
        {"name": "WanderNina",        "channel_id": "UC_nina_01",  "subscribers": 320000,  "risk_tier": "low"},
        {"name": "WanderlustHiroshi", "channel_id": "UC_kyoto_01", "subscribers": 340000,  "risk_tier": "low"},
        {"name": "LisbonDays",        "channel_id": "UC_lisbon_01","subscribers": 120000,  "risk_tier": "moderate"},
        {"name": "CDMXFoodie",        "channel_id": "UC_cdmx_01",  "subscribers": 890000,  "risk_tier": "low"},
        {"name": "SeoulNights",       "channel_id": "UC_seoul_01", "subscribers": 560000,  "risk_tier": "low"},
    ])
    print("✅ Seeded creators.")
else:
    print("↩  Creators already seeded.")

# ── Narratives ────────────────────────────────────────────────────────────────

narratives_col = db["narratives"]
if narratives_col.count_documents({}) == 0:
    narratives_col.insert_many([
        {
            "destination": "Kyoto", "country": "Japan",
            "signal_type": "narrative_momentum", "value": 12.0,
            "risk": "Low creator risk",
            "highlights": ["culture", "food", "walkable"],
            "blurb": "Autumn travel vlogs are spiking; viewers gravitate toward slow itineraries and neighborhood food crawls.",
            "refreshed_at": datetime.utcnow(),
        },
        {
            "destination": "Lisbon", "country": "Portugal",
            "signal_type": "search_interest", "value": 8.0,
            "risk": "Moderate creator risk",
            "highlights": ["budget", "coast", "nightlife"],
            "blurb": "Creators tout shoulder-season bargains and surf day-trips; mixed sentiment on short-term rental fatigue.",
            "refreshed_at": datetime.utcnow(),
        },
        {
            "destination": "México City", "country": "Mexico",
            "signal_type": "watch_time", "value": 15.0,
            "risk": "Monitor safety advisories",
            "highlights": ["food", "design", "urban"],
            "blurb": "Long-form food series are outperforming; audience questions center on neighborhoods and transit safety.",
            "refreshed_at": datetime.utcnow(),
        },
        {
            "destination": "Seoul", "country": "South Korea",
            "signal_type": "narrative_momentum", "value": 10.0,
            "risk": "Low creator risk",
            "highlights": ["pop culture", "shopping", "night market"],
            "blurb": "Short-form hauls and night market reels dominate; viewers want exact shop maps and late-night transit tips.",
            "refreshed_at": datetime.utcnow(),
        },
    ])
    print("✅ Seeded narratives.")
else:
    print("↩  Narratives already seeded.")

# ── Claims ────────────────────────────────────────────────────────────────────

claims_col = db["claims"]
claims_col.drop()
db.create_collection("claims", validator=claims_validator)
claims_col = db["claims"]

if claims_col.count_documents({}) == 0:
    claims_col.insert_many([
        # trending: True  →  these appear in the ClaimsCarousel on the homepage
        {
            "destination": "Tokyo", "claim": "You can eat in Tokyo for under $10 a meal.",
            "source": "WonderWithMia", "views": "842K",
            "engagement_rate": "9.8%", "growth_velocity": "+37%",
            "verified": True, "trending": True,
        },
        {
            "destination": "Tokyo", "claim": "Tokyo convenience stores are massively underrated.",
            "source": "TravelTomo", "views": "620K",
            "engagement_rate": "8.1%", "growth_velocity": "+21%",
            "verified": True, "trending": True,
        },
        {
            "destination": "Japan", "claim": "A rail pass saves you hundreds on long-distance travel.",
            "source": "NomadNick", "views": "1.2M",
            "engagement_rate": "11.2%", "growth_velocity": "+42%",
            "verified": True, "trending": True,
        },
        {
            "destination": "Tokyo", "claim": "Hidden ramen spots consistently beat the tourist traps.",
            "source": "WanderNina", "views": "540K",
            "engagement_rate": "7.5%", "growth_velocity": "+18%",
            "verified": True, "trending": True,
        },
        {
            "destination": "Kyoto", "claim": "Arashiyama bamboo grove is best visited before 7am.",
            "source": "WanderlustHiroshi", "views": "910K",
            "engagement_rate": "10.4%", "growth_velocity": "+29%",
            "verified": True, "trending": True,
        },
        {
            "destination": "Seoul", "claim": "T-money card works on every metro line including AREX.",
            "source": "SeoulNights", "views": "730K",
            "engagement_rate": "8.9%", "growth_velocity": "+33%",
            "verified": True, "trending": True,
        },
        # trending: False  →  destination detail pages only
        {
            "destination": "Lisbon", "claim": "Tram 28 is fine for tourists during off-peak hours.",
            "source": "LisbonDays", "views": "310K",
            "engagement_rate": "6.2%", "growth_velocity": "+11%",
            "verified": True, "trending": False,
        },
        {
            "destination": "México City", "claim": "Uber is safer than street taxis at night.",
            "source": "CDMXFoodie", "views": "480K",
            "engagement_rate": "7.0%", "growth_velocity": "+15%",
            "verified": True, "trending": False,
        },
    ])
    print("✅ Seeded claims.")
else:
    print("↩  Claims already seeded.")

print("\n🎉 Database ready.")