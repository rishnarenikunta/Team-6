# backend/cluster.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient
import numpy as np
import hdbscan
import umap
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from datetime import datetime, timezone
from bson import ObjectId

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]

# --- Debug: check for mismatches ---
print("\n=== DIAGNOSTIC ===")

creator_ids = db["creators"].distinct("channel_id")
narrative_channel_ids = db["narratives"].distinct("channel_id")
claim_channel_ids = db["claims"].distinct("channel_id")

print(f"Creators in 'creators' collection: {len(creator_ids)}")
print(f"Distinct channel_ids in 'narratives': {len(narrative_channel_ids)}")
print(f"Distinct channel_ids in 'claims': {len(claim_channel_ids)}")

# Which creators have NO matching narratives
missing_narratives = [c for c in creator_ids if c not in narrative_channel_ids]
print(f"\nCreators with 0 matching narratives: {missing_narratives}")

# Which creators have NO matching claims
missing_claims = [c for c in creator_ids if c not in claim_channel_ids]
print(f"\nCreators with 0 matching claims: {missing_claims}")

# Sample a creator that should have data and check
print(f"\nSample creator IDs from creators collection: {creator_ids[:3]}")
print(f"Sample channel_ids from narratives collection: {narrative_channel_ids[:3]}")
print("=== END DIAGNOSTIC ===\n")
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


def filter_valid_docs(docs, vector_field, scope_type, type_id):
    """Filter out docs with missing, null, or inhomogeneous vectors."""
    valid = [
        doc for doc in docs
        if doc.get(vector_field) and isinstance(doc[vector_field], list)
    ]

    if not valid:
        return []

    expected_len = len(valid[0][vector_field])
    valid = [doc for doc in valid if len(doc[vector_field]) == expected_len]

    skipped = len(docs) - len(valid)
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} docs with bad vectors for {scope_type}={type_id}")

    return valid


def compute_top_narrative(scope_type, scope_filter, type_id):
    """
    scope_type:   "country" | "creator" | "overall"
    scope_filter: MongoDB query dict to filter narratives collection
    type_id:      string identifier for this scope (country name, channel_id, or "overall")

    Falls back to the single available doc if fewer than 2 valid vectors exist.
    Saves None values if no docs exist at all.
    """
    col = db["narratives"]
    docs = list(col.find(scope_filter))

    # No docs at all — save a None record and exit
    if len(docs) == 0:
        print(f"⚠️  No narratives found for {scope_type}={type_id}, saving null record")
        db["top_narratives"].update_one(
            {"type": scope_type, "typeID": type_id},
            {"$set": {
                "type":        scope_type,
                "typeID":      type_id,
                "narrativeID": None,
                "narrative":   None,
                "channel_id":  None,
                "video_id":    None,
                "clusterSize": None,
                "totalDocs":   0,
                "computedAt":  datetime.now(timezone.utc)
            }},
            upsert=True
        )
        return

    valid_docs = filter_valid_docs(docs, "narrative_vector", scope_type, type_id)

    # Fewer than 2 valid vectors — fall back to single doc (first valid, or first overall)
    if len(valid_docs) < 2:
        fallback_doc = valid_docs[0] if valid_docs else docs[0]
        print(f"⚠️  Not enough valid vectors for {scope_type}={type_id}, using single fallback doc")
        db["top_narratives"].update_one(
            {"type": scope_type, "typeID": type_id},
            {"$set": {
                "type":        scope_type,
                "typeID":      type_id,
                "narrativeID": fallback_doc.get("narrative_id"),
                "narrative":   fallback_doc.get("narrative_title"),
                "channel_id":  fallback_doc.get("channel_id"),
                "video_id":    fallback_doc.get("video_id"),
                "clusterSize": 1,
                "totalDocs":   len(docs),
                "computedAt":  datetime.now(timezone.utc)
            }},
            upsert=True
        )
        return

    # Normal path — cluster and find top doc
    embeddings = np.array([doc["narrative_vector"] for doc in valid_docs])
    top_doc, cluster_size = get_top_doc_from_cluster(valid_docs, embeddings)

    # Clustering returned nothing — fall back to first valid doc
    if top_doc is None:
        print(f"⚠️  No cluster found for {scope_type}={type_id}, using single fallback doc")
        top_doc = valid_docs[0]
        cluster_size = 1

    db["top_narratives"].update_one(
        {"type": scope_type, "typeID": type_id},
        {"$set": {
            "type":        scope_type,
            "typeID":      type_id,
            "narrativeID": top_doc.get("narrative_id"),
            "narrative":   top_doc.get("narrative_title"),
            "channel_id":  top_doc.get("channel_id"),
            "video_id":    top_doc.get("video_id"),
            "clusterSize": cluster_size,
            "totalDocs":   len(docs),
            "computedAt":  datetime.now(timezone.utc)
        }},
        upsert=True
    )
    print(f"✅ narrative saved: {scope_type}={type_id}")


def compute_top_claim(scope_type, scope_filter, creator_id, country):

    type_id = _make_type_id(scope_type, creator_id, country)

    col = db["claims"]
    docs = list(col.find(scope_filter))

    # No docs at all — save a None record and exit
    if len(docs) == 0:
        print(f"⚠️  No claims found for {scope_type}={type_id}, saving null record")
        db["top_claims"].update_one(
            {"type": scope_type, "typeID": type_id},
            {"$set": {
                "type":        scope_type,
                "typeID":      type_id,
                "creatorID":   None,
                "country":     country,
                "claimID":     None,
                "claimText":   None,
                "narrativeID": None,
                "clusterSize": None,
                "totalDocs":   0,
                "computedAt":  datetime.now(timezone.utc)
            }},
            upsert=True
        )
        return

    valid_docs = filter_valid_docs(docs, "claim_vector", scope_type, type_id)

    # Fewer than 2 valid vectors — fall back to single doc
    if len(valid_docs) < 2:
        fallback_doc = valid_docs[0] if valid_docs else docs[0]
        print(f"⚠️  Not enough valid vectors for {scope_type}={type_id}, using single fallback doc")
        db["top_claims"].update_one(
            {"type": scope_type, "typeID": type_id},
            {"$set": {
                "type":        scope_type,
                "typeID":      type_id,
                "creatorID":   fallback_doc.get("source"),
                "country":     country,
                "claimID":     fallback_doc.get("_id"),
                "claimText":   fallback_doc.get("claim_title"),
                "narrativeID": fallback_doc.get("narrative_id"),
                "clusterSize": 1,
                "totalDocs":   len(docs),
                "computedAt":  datetime.now(timezone.utc)
            }},
            upsert=True
        )
        return

    # Normal path — cluster and find top doc
    embeddings = np.array([doc["claim_vector"] for doc in valid_docs])
    top_doc, cluster_size = get_top_doc_from_cluster(valid_docs, embeddings)

    # Clustering returned nothing — fall back to first valid doc
    if top_doc is None:
        print(f"⚠️  No cluster found for {scope_type}={type_id}, using single fallback doc")
        top_doc = valid_docs[0]
        cluster_size = 1

    db["top_claims"].update_one(
        {"type": scope_type, "typeID": type_id},
        {"$set": {
            "type":        scope_type,
            "typeID":      type_id,
            "creatorID":   top_doc.get("source"),
            "country":     country,
            "claimID":     top_doc["_id"],
            "claimText":   top_doc["claim_title"],
            "narrativeID": top_doc.get("narrative_id"),
            "clusterSize": cluster_size,
            "totalDocs":   len(docs),
            "computedAt":  datetime.now(timezone.utc)
        }},
        upsert=True
    )
    print(f"✅ claim saved: {scope_type}={type_id}")


def _make_type_id(scope_type, creator_id, country):
    if scope_type == "creator":
        return creator_id
    if scope_type == "country":
        return country
    return "overall"


# --- Run ---

countries = db["narratives"].distinct("destination")
creators  = db["creators"].distinct("channel_id")

# Top narratives per country
for country in countries:
    compute_top_narrative(
        scope_type="country",
        scope_filter={"destination": country},
        type_id=country
    )

# Top narratives per creator
for creator in creators:
    compute_top_narrative(
        scope_type="creator",
        scope_filter={"channel_id": creator},
        type_id=creator
    )

# Overall top narrative
compute_top_narrative(
    scope_type="overall",
    scope_filter={},
    type_id="overall"
)

# Top claims per country
for country in countries:
    compute_top_claim(
        scope_type="country",
        scope_filter={"destination": country},
        creator_id=None,
        country=country
    )

# Top claims per creator
for creator in creators:
    compute_top_claim(
        scope_type="creator",
        scope_filter={"source": creator},
        creator_id=creator,
        country=None
    )

# Overall top claim
compute_top_claim(
    scope_type="overall",
    scope_filter={},
    creator_id=None,
    country=None
)


# --- Print results ---

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
            print(f"\n{current_type.upper()}")

        print(f"\n  {row.get('typeID')}")

        if collection_name == "top_narratives":
            print(f"  {row.get('narrative')}")
            print(f"  narrativeID: {row.get('narrativeID')}")
        else:
            print(f"  {row.get('claimText')}")
            print(f"  claimID: {row.get('claimID')}  |  narrativeID: {row.get('narrativeID')}")
            print(f"  creatorID: {row.get('creatorID')}  |  destination: {row.get('country')}")

        print(f"  Cluster: {row.get('clusterSize')} / {row.get('totalDocs')}  |  {row.get('computedAt')}")


print_table("top_narratives", "TOP NARRATIVES")
print_table("top_claims",     "TOP CLAIMS")

print(f"\n{'=' * 70}")
print("  Done.")