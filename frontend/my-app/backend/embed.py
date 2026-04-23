# backend/embed.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_collection(collection_name, text_field, vector_field):
    col = db[collection_name]

    docs = list(col.find({vector_field: {"$exists": False}}))

    if not docs:
        print(f"✅ No new documents in {collection_name}")
        return

    texts = [doc[text_field] for doc in docs]
    embeddings = model.encode(texts, show_progress_bar=True)

    for doc, emb in zip(docs, embeddings):
        col.update_one(
            {"_id": doc["_id"]},
            {"$set": {vector_field: emb.tolist()}}
        )

    print(f"✅ Embedded {len(docs)} documents in {collection_name}")


# Embed narratives (using blurb)
embed_collection("narratives", "blurb", "narrative_vector")

# Embed claims
embed_collection("claims", "claim_text", "claim_vector")

print("🎉 Embedding complete.")