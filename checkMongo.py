import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URI")

client = MongoClient(uri)
db = client["travel_app"]
collection = db["videos"]

collection.insert_one({"test": "hello"})
print(collection.find_one())

