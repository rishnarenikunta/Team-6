# backend/cluster.py

import os
import time
import random
import json
from dotenv import load_dotenv
from pymongo import MongoClient
import numpy as np
import hdbscan
import umap
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from datetime import datetime, timezone
from google import genai
from google.genai import types, errors
from pydantic import BaseModel, Field

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]

# --- Debug: check for mismatches ---
print("\n=== DIAGNOSTIC ===")

creator_ids = db["creators"].distinct("channel_id")
narrative_channel_ids = db["narratives"].distinct("channel_id")
claim_channel_ids = claim_channel_ids = db["claims"].distinct("source")

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

# ==========================================
# GEMINI ROTATOR FRAMEWORK
# ==========================================
GEMINI_KEYS_ENV = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY")

class GeminiRotator:
    """Manages a pool of Gemini API keys and automatically rotates them on 429 or 5xx errors."""
    def __init__(self, keys_string: str):
        if not keys_string:
            raise ValueError("No Gemini keys provided in environment.")
        self.keys = [k.strip() for k in keys_string.split(",") if k.strip()]
        self.current_index = 0
        self.client = genai.Client(api_key=self.keys[self.current_index])
        print(f"[INFO] Initialized GeminiRotator with {len(self.keys)} key(s).")

    def _rotate(self):
        self.current_index = (self.current_index + 1) % len(self.keys)
        print(f"[INFO] Rotating to Gemini API key index {self.current_index}...")
        self.client = genai.Client(api_key=self.keys[self.current_index])

    def execute_with_retry(self, action_func, max_attempts=None):
        if max_attempts is None:
            max_attempts = len(self.keys) * 3 

        attempts = 0
        while attempts < max_attempts:
            try:
                return action_func(self.client)
            except errors.APIError as e:
                if e.code == 429 or e.code >= 500:
                    self._rotate()
                    attempts += 1
                    sleep_time = (2 ** attempts) + random.uniform(0, 1)
                    print(f"[WARN] API Error {e.code}: {e.message}. Sleeping for {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                else:
                    raise e
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "500" in error_str or "503" in error_str:
                    self._rotate()
                    attempts += 1
                    sleep_time = (2 ** attempts) + random.uniform(0, 1)
                    print(f"[WARN] Caught rate limit exception. Sleeping for {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                else:
                    raise e
                    
        raise RuntimeError("Max retries exhausted across all available Gemini API keys.")

gemini_rotator = GeminiRotator(GEMINI_KEYS_ENV)
GENERATION_MODEL = "gemini-3.1-flash-lite-preview" # Ideal for fast, structured text summarization

# ==========================================
# SUMMARIZATION LOGIC
# ==========================================

class ClusterSummary(BaseModel):
    master_narrative: str = Field(
        description="A single, clean, overarching narrative sentence (max 15 words) that captures the core theme of the cluster."
    )

def summarize_cluster_with_gemini(cluster_texts):
    """Uses the GeminiRotator to generate a master narrative from a cluster of texts."""
    prompt = f"""
    You are an expert travel analyst. Below are similar statements made by travel creators.
    Synthesize these into a single, clean, overarching narrative sentence.
    
    Statements:
    {json.dumps(cluster_texts, indent=2)}
    """
    
    def action(client_instance):
        return client_instance.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ClusterSummary,
                temperature=0.2 # Low temp for deterministic summaries
            ),
        )
        
    try:
        response = gemini_rotator.execute_with_retry(action)
        data = json.loads(response.text)
        return data.get("master_narrative", cluster_texts[0])
    except Exception as e:
        print(f"[WARN] Gemini Summarization Error: {e}")
        return cluster_texts[0] # Fallback to the first text if generation fails



def get_risk_score(doc):
    """Extracts risk string from a doc and converts it to a 0-3 scale."""
    risk_str = None
    
    # Extract from narrative doc format
    if "risk" in doc and isinstance(doc["risk"], dict):
        risk_str = doc["risk"].get("risk_text")
    # Extract from claim doc format
    elif "claim_risk" in doc:
        risk_str = doc.get("claim_risk")
    elif "risks" in doc and isinstance(doc["risks"], dict):
        risk_str = doc["risks"].get("risk_text")
        
    if not risk_str:
        return 0.0
        
    risk_str = risk_str.lower()
    if "high" in risk_str or "extreme" in risk_str: return 3.0
    if "medium" in risk_str: return 2.0
    if "low" in risk_str: return 1.0
    return 0.0

def get_risk_label(score):
    """Converts a numeric risk average back to a descriptive label."""
    if score >= 2.5: return "High - Physical Danger"
    if score >= 1.5: return "Medium - Scam/Misinfo"
    if score >= 0.5: return "Low - Subjective"
    return "None"

# ==========================================
# CLUSTERING LOGIC
# ==========================================

def get_top_clusters(docs, embeddings, max_clusters=3, min_cluster_size=2):
    """Run UMAP + HDBSCAN, and return gemini summaries for up to 'max_clusters'."""
    n_samples = len(embeddings)
    n_components = min(50, n_samples - 1)
    n_neighbors = min(15, n_samples - 1)

    if n_components < 2:
        return []

    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        init="random",
        random_state=42
    )
    reduced = reducer.fit_transform(embeddings)

    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric="euclidean", cluster_selection_method="eom")
    labels = clusterer.fit_predict(reduced)

    counts = Counter(labels)
    counts.pop(-1, None) # Remove noise

    if not counts:
        return []

    results = []
    # Get up to 'max_clusters' (e.g., Top 3)
    top_clusters = counts.most_common(max_clusters)

    for rank, (cluster_id, size) in enumerate(top_clusters, start=1):
        if size < min_cluster_size:
            continue

        cluster_indices = [i for i, label in enumerate(labels) if label == cluster_id]
        cluster_embeddings = embeddings[cluster_indices]

        # --- Compute Average Risk ---
        cluster_docs = [docs[i] for i in cluster_indices]
        risk_scores = [get_risk_score(d) for d in cluster_docs]
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        avg_risk_label = get_risk_label(avg_risk_score)

        # Extract all unique channel and video IDs in this cluster
        cluster_channels = list(set(d.get("channel_id") for d in cluster_docs if d.get("channel_id")))
        cluster_videos = list(set(d.get("video_id") for d in cluster_docs if d.get("video_id")))
        # --- Centroid & Gemini Summary ---
        centroid = cluster_embeddings.mean(axis=0)
        sims = cosine_similarity([centroid], cluster_embeddings)[0]
        
        # Sort indices by proximity to centroid
        sorted_local_indices = np.argsort(sims)[::-1] 
        
        # Grab the top 5 closest texts to feed to Gemini
        top_texts = []
        for local_idx in sorted_local_indices[:5]:
            global_idx = cluster_indices[local_idx]
            # Handle both narratives and claims collections
            text = docs[global_idx].get("narrative_title") or docs[global_idx].get("claim_title")
            if text:
                top_texts.append(text)

        # Generate the synthesized narrative!
        generated_text = summarize_cluster_with_gemini(top_texts)

        # Return the closest physical doc, the cluster size, and the generated text
        best_global_idx = cluster_indices[sorted_local_indices[0]]
        closest_doc = docs[best_global_idx]

        results.append({
            "rank": rank,
            "doc": closest_doc,
            "size": size,
            "text": generated_text,
            "avg_risk_score": avg_risk_score,
            "avg_risk_label": avg_risk_label,
            "cluster_channels": cluster_channels,
            "cluster_videos": cluster_videos
        })

    return results

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


def compute_top_narrative(scope_type, scope_filter, type_id, max_clusters=3):
    """
    scope_type:   "country" | "creator" | "overall"
    scope_filter: MongoDB query dict to filter narratives collection
    type_id:      string identifier for this scope (country name, channel_id, or "overall")

    Falls back to the single available doc if fewer than 2 valid vectors exist.
    Saves None values if no docs exist at all.
    """
    col = db["narratives"]
    docs = list(col.find(scope_filter))

    # Clean the slate: Remove old clusters for this specific scope/ID
    db["top_narratives"].delete_many({"type": scope_type, "typeID": type_id})

    # No docs at all — save a None record and exit
    if len(docs) == 0:
        db["top_narratives"].insert_one({
            "type":        scope_type,
            "typeID":      type_id,
            "clusterRank": 1,
            "narrativeID": None,
            "includedChannels":  [],
            "includedVideos":    [],
            "clusterSize": 0,
            "totalDocs":   0,
            "averageRiskScore": None,
            "averageRiskLabel": None,
            "computedAt":  datetime.now(timezone.utc)
        })
        return

    valid_docs = filter_valid_docs(docs, "narrative_vector", scope_type, type_id)

    # Fewer than 2 valid vectors — fall back to single doc
    if len(valid_docs) < 2:
        fallback_doc = valid_docs[0] if valid_docs else docs[0]
        print(f"⚠️  Not enough valid vectors for {scope_type}={type_id}, using single fallback doc")
        avg_risk_score = get_risk_score(fallback_doc)
        db["top_narratives"].insert_one({
            "type": scope_type,
            "typeID": type_id,
            "clusterRank": 1,
            "narrativeID": fallback_doc.get("narrative_id"),
            "narrative": fallback_doc.get("narrative_title"),
            "includedChannels": [fallback_doc.get("channel_id")] if fallback_doc.get("channel_id") else [],
            "includedVideos": [fallback_doc.get("video_id")] if fallback_doc.get("video_id") else [],
            "clusterSize": 1, "totalDocs": len(docs),
            "averageRiskScore": avg_risk_score,
            "averageRiskLabel": get_risk_label(avg_risk_score),
            "computedAt": datetime.now(timezone.utc)
        })
        return

    # Normal path — get multiple clusters
    embeddings = np.array([doc["narrative_vector"] for doc in valid_docs])
    clusters_data = get_top_clusters(valid_docs, embeddings, max_clusters=max_clusters, min_cluster_size=2)

    # If clustering returned nothing, fall back and wrap the single doc's IDs in a list
    if not clusters_data:
        fallback_doc = valid_docs[0]
        avg_risk_score = get_risk_score(fallback_doc)
        clusters_data = [{
            "rank": 1,
            "doc": fallback_doc,
            "size": 1, 
            "text": fallback_doc.get("narrative_title"),
            "avg_risk_score": avg_risk_score,
            "avg_risk_label": get_risk_label(avg_risk_score),
            "cluster_channels": [fallback_doc.get("channel_id")] if fallback_doc.get("channel_id") else [],
            "cluster_videos": [fallback_doc.get("video_id")] if fallback_doc.get("video_id") else []
        }]

    # Save all found clusters
    for cluster in clusters_data:
        db["top_narratives"].insert_one({
            "type": scope_type,
            "typeID": type_id,
            "clusterRank": cluster["rank"], # Track 1st, 2nd, 3rd
            "narrativeID": cluster["doc"].get("narrative_id"),
            "narrative": cluster["text"],
            "clusterSize": cluster["size"],
            "totalDocs": len(docs),
            "averageRiskScore": cluster["avg_risk_score"],
            "averageRiskLabel": cluster["avg_risk_label"],
            "includedChannels": cluster["cluster_channels"],
            "includedVideos": cluster["cluster_videos"],
            "computedAt": datetime.now(timezone.utc)
        })
    
    print(f"✅ Saved {len(clusters_data)} narratives for {scope_type}={type_id}")


def compute_top_claim(scope_type, scope_filter, creator_id, country, max_clusters=3):
    type_id = _make_type_id(scope_type, creator_id, country)

    col = db["claims"]
    docs = list(col.find(scope_filter))

    # Clean the slate: Remove old clusters for this specific scope/ID
    db["top_claims"].delete_many({"type": scope_type, "typeID": type_id})

    # No docs at all — save a None record and exit
    if len(docs) == 0:
        print(f"⚠️  No claims found for {scope_type}={type_id}, saving null record")
        db["top_claims"].insert_one({
            "type":        scope_type,
            "typeID":      type_id,
            "clusterRank": 1,
            "creatorID":   creator_id,
            "country":     country,
            "claimID":     None,
            "claimText":   None,
            "narrativeID": None,
            "includedChannels": [],
            "includedVideos": [],
            "clusterSize": 0,
            "totalDocs":   0,
            "averageRiskScore": None,
            "averageRiskLabel": None,
            "computedAt":  datetime.now(timezone.utc)
        })
        return

    valid_docs = filter_valid_docs(docs, "claim_vector", scope_type, type_id)

    # Fewer than 2 valid vectors — fall back to single doc
    if len(valid_docs) < 2:
        fallback_doc = valid_docs[0] if valid_docs else docs[0]
        print(f"⚠️  Not enough valid vectors for {scope_type}={type_id}, using single fallback doc")
        avg_risk_score = get_risk_score(fallback_doc)
        
        db["top_claims"].insert_one({
            "type":        scope_type,
            "typeID":      type_id,
            "clusterRank": 1,
            "creatorID":   fallback_doc.get("source"),
            "country":     country,
            "claimID":     fallback_doc.get("_id"),
            "claimText":   fallback_doc.get("claim_title"),
            "narrativeID": fallback_doc.get("narrative_id"),
            "includedChannels": [fallback_doc.get("channel_id")] if fallback_doc.get("channel_id") else [],
            "includedVideos": [fallback_doc.get("video_id")] if fallback_doc.get("video_id") else [],
            "clusterSize": 1,
            "totalDocs":   len(docs),
            "averageRiskScore": avg_risk_score,
            "averageRiskLabel": get_risk_label(avg_risk_score),
            "computedAt":  datetime.now(timezone.utc)
        })
        return

    # Normal path — get multiple clusters
    embeddings = np.array([doc["claim_vector"] for doc in valid_docs])
    clusters_data = get_top_clusters(valid_docs, embeddings, max_clusters=max_clusters, min_cluster_size=2)

    # Clustering returned nothing — fall back to first valid doc
    if not clusters_data:
        print(f"⚠️  No cluster found for {scope_type}={type_id}, using single fallback doc")
        fallback_doc = valid_docs[0]
        avg_risk_score = get_risk_score(fallback_doc)
        clusters_data = [{
            "rank": 1,
            "doc": fallback_doc,
            "size": 1,
            "text": fallback_doc.get("claim_title"),
            "avg_risk_score": avg_risk_score,
            "avg_risk_label": get_risk_label(avg_risk_score),
            "cluster_channels": [fallback_doc.get("channel_id")] if fallback_doc.get("channel_id") else [],
            "cluster_videos": [fallback_doc.get("video_id")] if fallback_doc.get("video_id") else []
        }]

    # Save all found clusters
    for cluster in clusters_data:
        db["top_claims"].insert_one({
            "type":        scope_type,
            "typeID":      type_id,
            "clusterRank": cluster["rank"],
            "creatorID":   cluster["doc"].get("source"),
            "country":     country,
            "claimID":     cluster["doc"].get("_id"),
            "claimText":   cluster["text"],
            "narrativeID": cluster["doc"].get("narrative_id"),
            "clusterSize": cluster["size"],
            "totalDocs":   len(docs),
            "averageRiskScore": cluster["avg_risk_score"],
            "averageRiskLabel": cluster["avg_risk_label"],
            "includedChannels": cluster["cluster_channels"],
            "includedVideos": cluster["cluster_videos"],
            "computedAt":  datetime.now(timezone.utc)
        })
        
    print(f"✅ Saved {len(clusters_data)} claims for {scope_type}={type_id}")


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