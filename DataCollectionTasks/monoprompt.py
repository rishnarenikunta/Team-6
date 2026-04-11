# main.py

import os
import time
from dotenv import load_dotenv

from typing import List, Dict, Any, Optional
from google import genai  # pip install google-genai
from google.genai import types, errors

from pydantic import BaseModel, Field


import json
import requests
import uuid
from datetime import datetime, timezone

from google.cloud import storage
from pymongo import MongoClient
import random

load_dotenv()

# Accept a comma-separated list of keys, fallback to single key if that's what exists
GEMINI_KEYS_ENV = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")


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
        """Executes a function and retries on rate limits or server errors."""
        if max_attempts is None:
            # By default, allow enough attempts to cycle through all keys twice
            max_attempts = len(self.keys) * 3 # Give it a few more tries

        attempts = 0
        while attempts < max_attempts:
            try:
                return action_func(self.client)
            except errors.APIError as e:
                # Check for 429 (Rate Limit) or 5xx (Server Errors)
                if e.code == 429 or e.code >= 500:
                    self._rotate()
                    attempts += 1
                    # Exponential backoff with jitter: 2^attempts + random milliseconds
                    sleep_time = (2 ** attempts) + random.uniform(0, 1)
                    print(f"[WARN] API Error {e.code}: {e.message}. Sleeping for {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                else:
                    raise e
            except Exception as e:
                # Fallback for unexpected network exceptions containing the status code
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

# Initialize the rotator
gemini_rotator = GeminiRotator(GEMINI_KEYS_ENV)

GENERATION_MODEL = "gemini-3.1-flash-lite-preview"
TRANSCRIPT_BASE_URL = "http://localhost:8000"  # adjust if different host/port


def fetch_transcript_from_gcs(gcs_uri: str) -> str:
    """Fetches the transcript JSON directly from a Google Cloud Storage bucket."""
    if not gcs_uri.startswith("gs://"):
        print(f"[WARN] Invalid GCS URI: {gcs_uri}")
        return ""
    
    # Split gs://bucket_name/path/to/file.json
    parts = gcs_uri[5:].split("/", 1)
    bucket_name = parts[0]
    blob_name = parts[1] if len(parts) > 1 else ""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    try:
        content = blob.download_as_text()
        data = json.loads(content)
        return data.get("text", "") 
    except Exception as e:
        print(f"[WARN] Failed to fetch transcript from GCS ({gcs_uri}): {e}")
        return ""


def build_country_features(
    title: str,
    top_comments: List[str],
    transcript: str,
) -> str:
    """
    Builds a text block with basic video context + transcript.
    We now use this as part of a richer feature-extraction prompt.
    """
    text = f"Video title: {title}\n\n"
    text += "Top comments:\n"
    for i, c in enumerate(top_comments, start=1):
        text += f"{i}. {c}\n"
    text += "\nTranscript:\n"
    # Truncate to avoid sending huge transcripts
    text += transcript
    return text


# Pydantic schema for structured video feature extraction
class Claim(BaseModel):
    claim_title: str = Field(description="A short succint display title for the claim")
    claim_text: str
    fact_check_assessment: str
    claim_comment_sentiment: str
    claim_comment_risk: str

class Narrative(BaseModel):
    narrative_title: str = Field(
        description="A punchy, declarative statement summarizing the creator's core argument or takeaway about the location (e.g., 'British food is actually delicious' instead of 'British Food Quality')."
    )
    narrative_description: str
    narrative_comment_summary: str
    narrative_comment_risk: str
    claims: list[Claim]

class CommentAnalysis(BaseModel):
    overall_sentiment: float
    general_risk_callouts: list[str]

class VideoComponents(BaseModel):
    video_summary: str = Field(description="1-2 sentences strictly summarizing the content")
    # video_overview: str = Field(description="A detailed paragraph explaining context, tone, and purpose")
    video_topics_destinations: list[str]
    overall_comment_analysis: CommentAnalysis
    narratives: list[Narrative]

class VideoFeatures(BaseModel):
    is_travel: bool = Field(
        description="True if the video is mainly about trips, tourism, or exploring locations. False otherwise."
    )
    video_components: Optional[VideoComponents] = None
    
# Embedding model for narrative title and claim title

EMBEDDING_MODEL = "models/gemini-embedding-001"  

# def embed_text(text: str) -> Optional[List[float]]:
#     text = (text or "").strip()
#     if not text:
#         return None

#     response = client.models.embed_content(
#         model=EMBEDDING_MODEL,
#         contents=text,
#     )
#     # google-genai: embeddings[0].values
#     emb = response.embeddings[0].values
#     return emb
def embed_texts(texts: List[str], model: str = EMBEDDING_MODEL) -> List[List[float]]:
    def action(client_instance):
        return client_instance.models.embed_content(
            model=model,
            contents=texts,
        )
    
    # Execute the API call through the rotator
    response = gemini_rotator.execute_with_retry(action)
    return [e.values for e in response.embeddings]

def extract_video_features_for_video(
    video_id: str,
    title: str,
    top_comments: List[str],
    transcript: str
) -> dict:

    features_text = build_country_features(
        title=title,
        top_comments=top_comments,
        transcript=transcript,
    )

    prompt = (
        "You are an expert video intelligence analyst, content classifier, and trust & safety reviewer. "
        "Your task is to first classify the provided video, and if applicable, analyze the Transcript, Metadata, and Comments to extract specific structured insights.\n"
        "You must strictly base your analysis ONLY on the provided inputs. Do not invent information, guess, or bring in outside knowledge unless performing a basic logical fact-check on a claim made within the video.\n\n"
        "INPUT DATA:\n"
        f"{features_text}\n\n"
        "INSTRUCTIONS:\n"
        "1. Classification (Travel vs. Non-Travel): Determine if this video is a travel video and set the 'is_travel' boolean field accordingly.\n"
        "   - Definition: A 'Travel' video primarily focuses on visiting, exploring, or documenting places outside the creator’s home location.\n"
        "   - Examples include: Travel vlogs, tourism guides, city/country exploration, trip itineraries, cultural experiences while traveling, and destination reviews.\n"
        "   - Non-Travel videos include: General lifestyle vlogs filmed at home, food reviews without travel context, commentary, podcasts, or videos that only briefly mention travel but are not about the trip itself.\n"
        "   - Rules: Classify based on the MAIN topic of the video, not small mentions. Use the title and transcript as the strongest signals.\n\n"
        "2. Conditional Extraction: \n"
        "   - If 'is_travel' is FALSE, you must leave the 'video_components' field empty or null and skip the remaining steps.\n"
        "   - If 'is_travel' is TRUE, you must extract the following inside the 'video_components' object:\n\n"
        "   a. Video Summary: Provide a concise, 1-2 sentence summary of what the video is about.\n"
        "   b. Destinations: Extract the primary physical countries discussed or visited in the video. Only include those that are a central topic or destination.\n"
        "   c. Overall Comment Analysis: Analyze the comments to determine the overall sentiment as a score from 0.0 to 1.0 (0.0 = very negative, 0.5 = neutral, 1.0 = very positive). Also identify any general risk callouts (e.g., hate speech, spam, widespread misinformation, dangerous acts).\n"
        "   d. Narratives & Claims: Break down the transcript into the creator's core arguments or specific takeaways about the location (Narratives). \n"
        "      - CRITICAL INSTRUCTION A: The 'narrative_title' MUST be a declarative sentence or specific opinion, NOT a generic category. \n"
        "        * BAD: 'Safety and Risk in Volatile Regions'\n"
        "        * GOOD: 'Traveling to Cameroon during elections is extremely dangerous.'\n"
        "        * BAD: 'Australia as a Diverse Travel Destination'\n"
        "        * GOOD: 'Australia offers everything from urban cities to remote outbacks.'\n"
        "      - Under each Narrative, list the specific reasons or features the speaker highlights to prove that point (Claims).\n"
        "      - CRITICAL INSTRUCTION B: DO NOT summarize the plot or recount what the speaker did chronologically (e.g., avoid 'They went to the museum and then ate dinner').\n"
        "      - CRITICAL INSTRUCTION C: DO extract qualitative judgments and actionable insights (e.g., 'The local food scene is highly accessible for vegans,' supported by claims like 'Every restaurant had plant-based menus').\n"
        "   e. Risk Assessment Constraint: Whenever you are asked to assess 'risk' (for the overall video, per narrative, or per claim), you MUST derive this risk by combining three factors:\n"
        "      - The sentiment of the comments regarding that specific topic.\n"
        "      - A summary of what the comments are saying about it.\n"
        "      - A logical fact-check of the narrative/claim based on the provided text, search, and basic common sense.\n\n"
        "OUTPUT FORMAT:\n"
        "You must output your response EXACTLY matching the output JSON structure. Return ONLY valid JSON. Do not include markdown formatting like ```json or any introductory text."
    )

    def action(client_instance):
        return client_instance.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VideoFeatures,
                temperature=0.2 # Lower temperature for more deterministic, structured outputs
            ),
        )

    # Execute the generation API call through the rotator
    response = gemini_rotator.execute_with_retry(action)

    raw = (response.text or "").strip()

    default_result: Dict[str, Any] = {
    "video_components": {
        "video_summary": "",
        "video_topics_destinations": [],
        "overall_comment_analysis": {
            "overall_sentiment": "",
            "general_risk_callouts": [],
        },
        "narratives": [],
        }
    }

    if not raw:
        return default_result

    try:
            data = json.loads(raw)
            _ = VideoFeatures(**data)
            print(data)
            filename = f"features_{video_id}.json"
            # with open(filename, "w", encoding="utf-8") as f:
            #     json.dump(data, f, indent=2, ensure_ascii=False)

            features_with_embedding: Dict[str, Any] = data

            video_components = features_with_embedding.get("video_components", {})
            narratives = video_components.get("narratives", [])
            print("NARRATIVES BEFORE EMBEDDING:")
            for i, n in enumerate(narratives):
                print(i, n.get("narrative_title"))

            # 1) collect all titles
            narrative_titles = []
            narrative_index = []
            claim_titles = []
            claim_index = []

            if isinstance(narratives, list):
                for n_idx, narrative in enumerate(narratives):
                    nt = narrative.get("narrative_title")
                    print("Checking narrative idx", n_idx, "title:", repr(nt))
                    if isinstance(nt, str) and nt.strip():
                        narrative_index.append(n_idx)
                        narrative_titles.append(nt)

                    claims = narrative.get("claims", [])
                    if isinstance(claims, list):
                        for c_idx, claim in enumerate(claims):
                            ct = claim.get("claim_title")
                            print("  Checking claim idx", c_idx, "title:", repr(ct))
                            if isinstance(ct, str) and ct.strip():
                                claim_index.append((n_idx, c_idx))
                                claim_titles.append(ct)

            print("NARRATIVE INDEX:", narrative_index)
            print("CLAIM INDEX:", claim_index)
            print("NARRATIVE TITLES:", narrative_titles)
            print("CLAIM TITLES:", claim_titles)

            # 2) embed all narrative titles
            if narrative_titles:
                nt_embs = embed_texts(narrative_titles)
                print("NARRATIVE EMBEDDINGS LEN:", len(nt_embs))
                for (n_idx, emb) in zip(narrative_index, nt_embs):
                    print("Assigning narrative_title_embedding to idx", n_idx)
                    narratives[n_idx]["narrative_title_embedding"] = emb

            # 3) embed all claim titles
            if claim_titles:
                ct_embs = embed_texts(claim_titles)
                print("CLAIM EMBEDDINGS LEN:", len(ct_embs))
                for ((n_idx, c_idx), emb) in zip(claim_index, ct_embs):
                    print("Assigning claim_title_embedding to", (n_idx, c_idx))
                    narratives[n_idx]["claims"][c_idx]["claim_title_embedding"] = emb

            # 1) collect all titles
            narrative_titles = []
            claim_titles = []
            narrative_index = []  # (n_idx)
            claim_index = []      # (n_idx, c_idx)

            if isinstance(narratives, list):
                for n_idx, narrative in enumerate(narratives):
                    nt = narrative.get("narrative_title")
                    if isinstance(nt, str) and nt.strip():
                        narrative_index.append(n_idx)
                        narrative_titles.append(nt)

                    claims = narrative.get("claims", [])
                    if isinstance(claims, list):
                        for c_idx, claim in enumerate(claims):
                            ct = claim.get("claim_title")
                            if isinstance(ct, str) and ct.strip():
                                claim_index.append((n_idx, c_idx))
                                claim_titles.append(ct)

            # 2) embed all narrative titles at once
            if narrative_titles:
                nt_embs = embed_texts(narrative_titles)
                for (n_idx, emb) in zip(narrative_index, nt_embs):
                    narratives[n_idx]["narrative_title_embedding"] = emb

            # 3) embed all claim titles at once
            if claim_titles:
                ct_embs = embed_texts(claim_titles)
                for ((n_idx, c_idx), emb) in zip(claim_index, ct_embs):
                    narratives[n_idx]["claims"][c_idx]["claim_title_embedding"] = emb

            return features_with_embedding

    except json.JSONDecodeError:
        return default_result
    

def _present(d: dict) -> dict:
    """Strip None values so we never overwrite existing fields with nulls."""
    return {k: v for k, v in d.items() if v is not None}

def save_features_to_collections(db, ctx: dict, features: Dict[str, Any]) -> tuple[list, list]:
    """
    Routes the extracted Gemini features to the correct MongoDB collections.
    videos      ← top-level video fields + summary + sentiment
    creators    ← stub upsert (preserves existing data)
    narratives  ← one doc per narrative (with embedding)
    claims      ← one doc per claim    (with embedding)
    """
    videos_col = db["metadata"]
    creators_col = db["creators"]
    narratives_col = db["narratives"]
    claims_col = db["claims"]

    now = datetime.now(timezone.utc)
    now_str = now.isoformat()
    is_travel = features.get("is_travel")

    if is_travel:
        vc = features.get("video_components") or {}

        video_id = ctx.get("video_id")
        channel_id = ctx.get("channel_id")
        upload_date = ctx.get("upload_date")

        # 1. Update Videos Collection
        comment_analysis = vc.get("overall_comment_analysis") or {}
        videos_col.update_one(
            {"video_id": video_id},
            {"$set": _present({
                "video_id":      video_id,
                "title":         ctx.get("title"),
                "description":   ctx.get("description"),
                "tags":          ctx.get("tags"),
                "comments":      ctx.get("top_comments"),
                "summary":       vc.get("video_summary"),
                "destinations":  vc.get("video_topics_destinations"),
                "sentiment":     comment_analysis.get("overall_sentiment"),
                "risk_callouts": comment_analysis.get("general_risk_callouts"),
                "is_travel":     True,
                "updated_at":    now,
            })},
            upsert=True,
        )

        # 2. Update Creators Collection (stub)
        if channel_id:
            creators_col.update_one(
                {"channel_id": channel_id},
                {"$setOnInsert": _present({
                    "channel_id":    channel_id,
                    "name":          ctx.get("channel_title"),
                    "created_at":    now,
                })},
                upsert=True,
            )

        narrative_ids: List[str] = []
        claim_ids: List[str] = []

        destinations = vc.get("video_topics_destinations") or []
        primary_destination = destinations[0] if destinations else None

        # 3. Insert Narratives and Claims
        for narrative in (vc.get("narratives") or []):
            if not narrative:
                continue

            narrative_id = str(uuid.uuid4())
            narrative_ids.append(narrative_id)

            narratives_col.insert_one(_present({
                "narrative_id":     narrative_id,
                "video_id":         video_id,
                "channel_id":       channel_id,
                "narrative_title":  narrative.get("narrative_title"),
                "narrative_text":   narrative.get("narrative_description"),
                "narrative_vector": narrative.get("narrative_title_embedding"),
                "comment_summary":  narrative.get("narrative_comment_summary"),
                "risk": _present({
                    "sentiment": narrative.get("narrative_comment_risk"),
                    "risk_text":  narrative.get("narrative_comment_risk"),
                }) or None,
                "destination":      primary_destination,
                "date":             now,
                "upload_date":      upload_date,
            }))

            for claim in (narrative.get("claims") or []):
                if not claim:
                    continue

                claim_id = str(uuid.uuid4())
                claim_ids.append(claim_id)

                claims_col.insert_one(_present({
                    "claim_id":     claim_id,
                    "narrative_id": narrative_id,
                    "video_id":     video_id,
                    "claim_title":  claim.get("claim_title"),
                    "claim_text":   claim.get("claim_text"),
                    "claim_vector": claim.get("claim_title_embedding"),
                    "claim_risk":   claim.get("claim_comment_risk"),
                    "fact_check":   claim.get("fact_check_assessment"),
                    "risks": _present({
                        "sentiment": claim.get("claim_comment_sentiment"),
                        "risk_text": claim.get("claim_comment_risk"),
                    }) or None,
                    "source":       channel_id,
                    "destination":  primary_destination,
                    "date":         now_str,
                    "upload_date":  upload_date,
                }))

        return narrative_ids, claim_ids
    else:
        video_id = ctx.get("video_id")
        channel_id = ctx.get("channel_id")
        upload_date = ctx.get("upload_date")

        # 1. Update Videos Collection
        videos_col.update_one(
            {"video_id": video_id},
            {"$set": _present({
                "video_id":      video_id,
                "title":         ctx.get("title"),
                "description":   ctx.get("description"),
                "tags":          ctx.get("tags"),
                "comments":      ctx.get("top_comments"),
                "is_travel":     False,
                "updated_at":    now,
            })},
            upsert=True,
        )
        return [], []


if __name__ == "__main__":
    # 1. get injected MongoDB doc from Switch
    mongo_data_str = os.environ.get("MONGO_DOCUMENT")
    print("data", mongo_data_str)
    if not mongo_data_str:
        print("[ERROR] No MONGO_DOCUMENT found in environment variables. Exiting.")
        exit(1)
    try:
        mongo_doc = json.loads(mongo_data_str)
    except json.JSONDecodeError:
        print("[ERROR] MONGO_DOCUMENT is not valid JSON. Exiting.")
        exit(1)
    # --- Initialize MongoDB ---
    db = None
    if MONGODB_URI:
        try:
            db_client = MongoClient(MONGODB_URI)
            db = db_client["travel_app"]
        except Exception as e:
            print(f"[ERROR] Failed to connect to MongoDB: {e}")

    # 2. Extract some metadata
    video_id = mongo_doc.get("_id", "Unknown")
    gcs_transcript_path = mongo_doc.get("gcs_transcript_path")
    channel_id = mongo_doc.get("channel_id", mongo_doc.get("channel").get("channel_id"))
    # --- Fetch Channel Title from Creators Collection ---
    channel_title = "Unknown Channel"
    if db is not None and channel_id:
        creator = db["creators"].find_one({"channel_id": channel_id})
        if creator and "name" in creator:
            channel_title = creator["name"]
    tags = mongo_doc.get("tags", [])
    title = mongo_doc.get("title")
    # --- Fetch Comments from Comments Collection ---
    top_comments = []
    if db is not None and video_id != "Unknown":
        # Query comments matching this video_id, limit to 50 to save context window space
        comments_cursor = db["comments"].find({"video_id": video_id}).limit(50)
        for comment_doc in comments_cursor:
            comment_text = comment_doc.get("text")
            if comment_text:
                top_comments.append(comment_text)
    # Fallback if no comments were found in the DB
    if not top_comments:
        top_comments = ["No comments available."]
    upload_date = mongo_doc.get("upload_date")

    # 3. Fetch transcript from GCS
    if not gcs_transcript_path:
        print("[ERROR] No gcs_transcript_path found in the MongoDB document. Exiting.")
        print(mongo_doc)
        exit(1)
        
    transcript = fetch_transcript_from_gcs(gcs_transcript_path)
    if not transcript:
        print(f"[WARN] Transcript is empty for {video_id}. Pipeline may degrade.")

    print(f"Starting pipeline for Video ID: {video_id} (Channel: {channel_title})")

    # Extract the features
    features = extract_video_features_for_video(
        video_id=video_id,
        title=title,
        top_comments=top_comments,
        transcript=transcript
    )
    print("Extracted video features successfully")
    
    # --- DATABASE INSERTION ---
    if db is not None:
        try:
            # Build context mapping for the save function
            ctx = {
                "video_id": video_id,
                "title": title,
                "tags": tags,
                "top_comments": top_comments,
                "channel_id": channel_id,
                "channel_title": channel_title,
                "upload_date": upload_date,
            }
            
            # Save into the collections
            n_ids, c_ids = save_features_to_collections(db, ctx, features)
            print(f"[SUCCESS] Saved to MongoDB. Inserted {len(n_ids)} narratives and {len(c_ids)} claims.")
        except Exception as e:
            print(f"[ERROR] Failed to save features to MongoDB: {e}")
        finally:
            db_client.close()
            print("[INFO] MongoDB connection closed.")
    else:
        print("[WARN] MongoDB connection not established. Skipping database insertion.")