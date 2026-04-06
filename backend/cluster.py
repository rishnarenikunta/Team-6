# backend/cluster.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient
import numpy as np
import hdbscan
import umap
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from datetime import datetime
from bson import ObjectId

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]


def get_top_doc_from_cluster(docs, embeddings):
    """Run UMAP + HDBSCAN and return the most representative doc in the largest cluster."""
    n_samples = len(embeddings)

    n_components = min(50, n_samples - 1)
    n_neighbors = min(15, n_samples - 1)

    if n_components < 2:
        return None, None

    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        init="random",
        random_state=42
    )
    reduced = reducer.fit_transform(embeddings)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,
        metric="euclidean",
        cluster_selection_method="eom"
    )
    labels = clusterer.fit_predict(reduced)

    counts = Counter(labels)
    counts.pop(-1, None)

    if not counts:
        return None, None

    top_cluster = counts.most_common(1)[0][0]
    cluster_indices = [i for i, label in enumerate(labels) if label == top_cluster]
    cluster_embeddings = embeddings[cluster_indices]

    centroid = cluster_embeddings.mean(axis=0)
    sims = cosine_similarity([centroid], cluster_embeddings)[0]
    best_local_idx = np.argmax(sims)
    best_global_idx = cluster_indices[best_local_idx]

    return docs[best_global_idx], counts[top_cluster]

#get top narratives 

def compute_top_narrative(scope_type, scope_filter, type_id):
    """
    scope_type:   "country" | "creator" | "overall"
    scope_filter: MongoDB query dict to filter narratives collection
    type_id:      string identifier for this scope (country name, channel_id, or "country::channel_id")
    """
    col = db["narratives"]
    docs = list(col.find(scope_filter))

    if len(docs) < 2:
        print(f"⚠️  Not enough narratives for {scope_type}={type_id}")
        return

    embeddings = np.array([doc["narrative_vector"] for doc in docs])
    top_doc, cluster_size = get_top_doc_from_cluster(docs, embeddings)

    if top_doc is None:
        print(f"⚠️  No cluster found for narrative {scope_type}={type_id}")
        return

    db["top_narratives"].update_one(
        {
            "type":   scope_type,
            "typeID": type_id
        },
        {
            "$set": {
                "type":        scope_type,
                "typeID":      type_id,
                "narrativeID": top_doc.get("narrative_id"), 
                "narrative":   top_doc["narrative_text"],
                "channel_id":  top_doc.get("channel_id"),   # ← add
                "video_id":    top_doc.get("video_id"),     # ← add
                "clusterSize": cluster_size,
                "totalDocs":   len(docs),
                "computedAt":  datetime.utcnow()
            }
        },
        upsert=True
    )
    print(f"narrative saved: {scope_type}={type_id}")




def compute_top_claim(scope_type, scope_filter, creator_id, country):
   
    type_id = _make_type_id(scope_type, creator_id, country)

    col = db["claims"]
    docs = list(col.find(scope_filter))

    if len(docs) < 2:
        print(f"⚠️  Not enough claims for {scope_type}={type_id}")
        return

    embeddings = np.array([doc["claim_vector"] for doc in docs])
    top_doc, cluster_size = get_top_doc_from_cluster(docs, embeddings)

    if top_doc is None:
        print(f"⚠️  No cluster found for claim {scope_type}={type_id}")
        return

    db["top_claims"].update_one(
        {
            "type":   scope_type,
            "typeID": type_id
        },
        {
            "$set": {
                "type":        scope_type,
                "typeID":      type_id,
                "creatorID":   top_doc.get("source"),
                "country":     country,
                "claimID":     top_doc["_id"],
                "claimText":   top_doc["claim_text"],
                "narrativeID": top_doc.get("narrative_id"),  # the narrative that generated this claim
                "clusterSize": cluster_size,
                "totalDocs":   len(docs),
                "computedAt":  datetime.utcnow()
            }
        },
        upsert=True
    )
    print(f"claim saved: {scope_type}={type_id}")


def _make_type_id(scope_type, creator_id, country):
    if scope_type == "creator":
        return creator_id
    if scope_type == "country":
        return country
    return "overall"


#overall bascially 

# distinct vlaues 
countries = db["narratives"].distinct("destination")   # rename field if needed
creators  = db["creators"].distinct("channel_id")

# top narratives per country
for country in countries:
    compute_top_narrative(
        scope_type="country",
        scope_filter={"destination": country},
        type_id=country
    )

#creator 
for creator in creators:
    compute_top_narrative(
        scope_type="creator",
        scope_filter={"channel_id": creator},
        type_id=creator
    )

# overall 
compute_top_narrative(
    scope_type="overall",
    scope_filter={},          # all narratives
    type_id="overall"
)

# claims
for country in countries:
    compute_top_claim(
        scope_type="country",
        scope_filter={"destination": country},
        creator_id=None,
        country=country
    )

for creator in creators:
    compute_top_claim(
        scope_type="creator",
        scope_filter={"channel_id": creator},
        creator_id=creator,
        country=None
    )


compute_top_claim(
    scope_type="overall",
    scope_filter={},          # all claims
    creator_id=None,
    country=None
)


#results to check if table is working 

def print_table(collection_name, label):
    print(f"\n{'=' * 70}")
    print(f" {label}")
    print("=" * 70)

    rows = list(db[collection_name].find({}, {"_id": 0}).sort("type", 1))
    if not rows:
        print("No records found.")
        return

    current_type = None
    for row in rows:
        if row["type"] != current_type:
            current_type = row["type"]
            print(f"\n{current_type.upper()} ")

        print(f"\n  {row.get('typeID')}")

        if collection_name == "top_narratives":
            print(f"  {row.get('narrative')}")
            print(f"  narrativeID: {row.get('narrativeID')}")
        else:
            print(f"  {row.get('claimText')}")
            print(f"  claimID: {row.get('claimID')}  |  narrativeID: {row.get('narrativeID')}")
            print(f"  creatorID: {row.get('creatorID')}  |  🌍 destination: {row.get('country')}")

        print(f"  Cluster: {row.get('clusterSize')} / {row.get('totalDocs')}  |  {row.get('computedAt')}")


print_table("top_narratives", "TOP NARRATIVES")
print_table("top_claims",     "TOP CLAIMS")

print(f"\n{'=' * 70}")
print("  Done.")