import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URI")

client = MongoClient(uri)
db = client["travel_app"]

# Only create if not exists
if "videos" not in db.list_collection_names():
    db.create_collection("videos", validator=video_validator)

if "creators" not in db.list_collection_names():
    db.create_collection("creators", validator=creator_validator)

if "narratives" not in db.list_collection_names():
    db.create_collection("narratives", validator=narrative_validator)

if "claims" not in db.list_collection_names():
    db.create_collection("claims", validator=claims_validator)

print("Collections created successfully.")
