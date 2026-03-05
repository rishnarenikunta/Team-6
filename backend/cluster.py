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

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]


def compute_trend(scope_type, scope_value,
                  collection_name, vector_field, text_field):

    col = db[collection_name]
    docs = list(col.find({scope_type: scope_value}))

    if len(docs) < 2:
        print(f"⚠️  Not enough docs for {scope_type}={scope_value}")
        return

    embeddings = np.array([doc[vector_field] for doc in docs])

    n_samples = len(embeddings)

    # Step 1: Dimensionality reduction
    n_components = min(50, n_samples - 1)
    n_neighbors = min(15, n_samples - 1)

    if n_components < 2:
        print(f"⚠️  Too few samples ({n_samples}) to reduce for {scope_type}={scope_value}")
        return

    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        init="random",  # avoids spectral layout crash on small datasets
        random_state=42
    )
    reduced = reducer.fit_transform(embeddings)

    # Step 2: Density clustering
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,
        metric="euclidean",
        cluster_selection_method="eom"
    )
    labels = clusterer.fit_predict(reduced)

    counts = Counter(labels)
    counts.pop(-1, None)  # remove noise

    if not counts:
        print(f"⚠️  No clusters found for {scope_value}")
        return

    # Largest cluster = strongest narrative
    top_cluster = counts.most_common(1)[0][0]
    cluster_indices = [i for i, label in enumerate(labels)
                       if label == top_cluster]

    cluster_embeddings = embeddings[cluster_indices]

    # Step 3: Find centroid
    centroid = cluster_embeddings.mean(axis=0)

    # Step 4: Find most representative document
    sims = cosine_similarity([centroid], cluster_embeddings)[0]
    best_local_idx = np.argmax(sims)
    best_global_idx = cluster_indices[best_local_idx]

    top_doc = docs[best_global_idx]

    # Step 5: Save to top_narratives table
    scope_id_field = "destination_id" if scope_type == "destination" else "channel_id"

    db["top_narratives"].update_one(
        {
            scope_id_field: scope_value,
            "content_type": collection_name
        },
        {
            "$set": {
                scope_id_field: scope_value,
                "scope_type": scope_type,
                "content_type": collection_name,
                "top_narrative": top_doc[text_field],
                "cluster_size": counts[top_cluster],
                "total_docs": n_samples,
                "computed_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    print(f"✅  Trend saved for {scope_type}={scope_value}")


# ============================================================
# RUN FOR ALL DESTINATIONS AND CREATORS
# ============================================================

destinations = db["narratives"].distinct("destination")
creators = db["creators"].distinct("channel_id")

for dest in destinations:
    compute_trend("destination", dest,
                  "narratives", "narrative_vector", "blurb")
    compute_trend("destination", dest,
                  "claims", "claim_vector", "claim_text")

for creator in creators:
    compute_trend("source", creator,
                  "claims", "claim_vector", "claim_text")


# ============================================================
# PRINT TOP NARRATIVES TABLE
# ============================================================

print("\n" + "=" * 70)
print("📊  TOP NARRATIVES")
print("=" * 70)

all_narratives = list(db["top_narratives"].find({}, {"_id": 0}).sort(
    [("scope_type", 1), ("destination_id", 1), ("channel_id", 1)]
))

if not all_narratives:
    print("No narratives found.")
else:
    current_scope = None
    for row in all_narratives:
        scope = row.get("scope_type", "unknown")

        # Print section header when scope type changes
        if scope != current_scope:
            current_scope = scope
            label = "BY DESTINATION" if scope == "destination" else "BY CREATOR"
            print(f"\n--- {label} ---")

        scope_id = row.get("destination_id") or row.get("channel_id", "unknown")
        content_type = row.get("content_type", "")
        narrative = row.get("top_narrative", "")
        cluster_size = row.get("cluster_size", 0)
        total_docs = row.get("total_docs", 0)
        computed_at = row.get("computed_at", "")

        print(f"\n  🌍  {scope_id}  [{content_type}]")
        print(f"  📝  {narrative}")
        print(f"  📈  Cluster size: {cluster_size} / {total_docs} docs  |  Computed: {computed_at}")

print("\n" + "=" * 70)
print("🎉  Done.")