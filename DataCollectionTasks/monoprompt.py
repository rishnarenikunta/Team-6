# main.py

import os
from dotenv import load_dotenv

from typing import List, Dict, Any, Optional
from google import genai  # pip install google-genai
from google.genai import types

from pydantic import BaseModel, Field


import json
import requests
import uuid
from datetime import datetime, timezone

from google.cloud import storage
from pymongo import MongoClient

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

client = genai.Client(
    api_key=GEMINI_API_KEY,
  #  http_options={"api_version": "v1beta"},
)

# PRINT AVAILABLE MODELS
# for m in client.models.list():
#     print(m.name)

GENERATION_MODEL = "gemini-2.5-flash-lite"
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
    description: str,
    top_comments: List[str],
    transcript: str,
) -> str:
    """
    Builds a text block with basic video context + transcript.
    We now use this as part of a richer feature-extraction prompt.
    """
    text = f"Video title: {title}\n\n"
    text += f"Description:\n{description}\n\n"
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
    narrative_title: str = Field(description="A short succint display title for the narrative")
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
    video_components: VideoComponents

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
    # filter or keep blank; here we keep order and embed as-is
    response = client.models.embed_content(
        model=model,
        contents=texts,
    )
    return [e.values for e in response.embeddings]

def extract_video_features_for_video(
    video_id: str,
    title: str,
    description: str,
    top_comments: List[str],
    transcript: str
) -> dict:

    features_text = build_country_features(
        title=title,
        description=description,
        top_comments=top_comments,
        transcript=transcript,
    )

    prompt = (
        "You are an expert video intelligence analyst and trust & safety reviewer. Your task is to analyze the provided Video Transcript, Video Metadata, and Video Comments to extract specific structured insights."
        "You must strictly base your analysis ONLY on the provided inputs. Do not invent information, guess, or bring in outside knowledge unless performing a basic logical fact-check on a claim made within the video."
        "\nINPUT DATA:"
        f"{features_text}"
        "\nINSTRUCTIONS:\n"
        "1. Video Summary: Provide a concise, 1-2 sentence summary of what the video is about."
        # "2. Video Overview: Provide a broader contextual paragraph detailing the video's purpose, tone, and main message based on the metadata and transcript."
        "2. Destinations: Extract the primary physical countries discussed or visited in the video. Only include those that are a central topic or destination in the video."
        "3. Overall Comment Analysis: Analyze the comments to determine the overall sentiment "
        "as a score from 0.0 to 1.0 (0.0 = very negative, 0.5 = neutral, 1.0 = very positive). "
        "Also identify any general risk callouts (e.g., hate speech, spam, widespread misinformation, dangerous acts)."
        "4. Narratives & Claims: Break down the transcript into its overarching themes or opinions about the location (Narratives). Under each Narrative, list the specific reasons or features the speaker highlights to prove that point (Claims)."
        "\n(a) CRITICAL INSTRUCTIONS: DO NOT summarize the plot or recount what the speaker did chronologically (e.g., avoid 'They went to the museum and then ate dinner')."
        "\n(b) DO extract qualitative judgments and actionable insights (e.g., 'The local food scene is highly accessible for vegans,' supported by claims like 'Every restaurant had plant-based menus')."
        "5. Risk Assessment Constraint: Whenever you are asked to assess 'risk' (for the overall video, per narrative, or per claim), you MUST derive this risk by combining three factors:"
        "\na. The sentiment of the comments regarding that specific topic."
        "\nb. A summary of what the comments are saying about it."
        "\nc. A logical fact-check of the narrative/claim based on the provided text, search, and basic common sense."
        "\nOUTPUT FORMAT:\n"
        "You must output your response EXACTLY matching the output JSON structure. Return ONLY valid JSON. Do not include markdown formatting like ```json or any introductory text."
    )

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=VideoFeatures,
            temperature=0.2 # Lower temperature for more deterministic, structured outputs
        ),
    )

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
    
def build_travel_prompt(
    channel_title: str,
    tags: List[str],
    title: str,
    description: str,
    top_comments: List[str],
    transcript: str,
) -> str:
    prompt = (
        "You are labeling a YouTube video as Travel or Non-Travel.\n"
        "A 'Travel' video is mainly about trips, tourism, vlogs of journeys, "
        "exploring cities or countries, etc.\n\n"
        "Return only one word: Travel or Non-Travel.\n\n"
        f"Channel title: {channel_title}\n"
        f"Tags: {', '.join(tags)}\n\n"
        f"Video title: {title}\n"
        f"Description: {description}\n\n"
        "Top comments:\n"
    )
    for i, c in enumerate(top_comments, start=1):
        prompt += f"{i}. {c}\n"
    prompt += "\nTranscript:\n"
    prompt += transcript[0:5000]
    return prompt


def classify_is_travel_video(
    video_id: str,
    channel_title: str,
    tags: List[str],
    title: str,
    description: str,
    top_comments: List[str],
    transcript: str
) -> bool:
    """
    Uses Gemini to classify whether a video is a travel video or not.
    Returns True if Travel, False otherwise.
    """

    prompt = build_travel_prompt(
        channel_title=channel_title,
        tags=tags,
        title=title,
        description=description,
        top_comments=top_comments,
        transcript=transcript,
    )

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )

    raw = (response.text or "").strip().lower()
    # print("RAW TRAVEL OUTPUT:", raw)  # uncomment for debugging

    # Very simple heuristic based on the expected "Travel" / "Non-Travel" answer
    if "travel" in raw and "non" not in raw:
        return True
    if "non" in raw and "travel" in raw:
        return False
    # Fallback: treat unclear answers as Non-Travel
    return False

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
    videos_col = db["videos"]
    creators_col = db["creators"]
    narratives_col = db["narratives"]
    claims_col = db["claims"]

    now = datetime.now(timezone.utc)
    now_str = now.isoformat()
    vc = features.get("video_components") or {}

    video_id = ctx.get("video_id")
    channel_id = ctx.get("channel_id")

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
            }))

    return narrative_ids, claim_ids


if __name__ == "__main__":
    # 1. get injected MongoDB doc from Switch
    mongo_data_str = os.environ.get("MONGO_DOCUMENT")
    if not mongo_data_str:
        print("[ERROR] No MONGO_DOCUMENT found in environment variables. Exiting.")
        exit(1)
    try:
        mongo_doc = json.loads(mongo_data_str)
    except json.JSONDecodeError:
        print("[ERROR] MONGO_DOCUMENT is not valid JSON. Exiting.")
        exit(1)
    # 2. Extract some metadata
    video_id = mongo_doc.get("_id", "Unknown")
    gcs_transcript_path = mongo_doc.get("gcs_transcript_path")
    channel_title = "Example Travel Channel"
    channel_id = mongo_doc.get("channel_id")
    tags = ["travel", "vlog", "europe", "vacation"]
    title = mongo_doc.get("title")
    description = "In this video I travel through France, Germany, and Italy." # TODO: fade
    top_comments = [
        "Loved the scenes from Paris!",
        "Germany looked incredible.",
        "Please visit Spain next time!",
    ]

    # 3. Fetch transcript from GCS
    if not gcs_transcript_path:
        print("[ERROR] No gcs_transcript_path found in the MongoDB document. Exiting.")
        print(mongo_doc)
        exit(1)
        
    transcript = fetch_transcript_from_gcs(gcs_transcript_path)
    if not transcript:
        print(f"[WARN] Transcript is empty for {video_id}. Pipeline may degrade.")

    print(f"Starting pipeline for Video ID: {video_id}")
    # 4. First: classify if it's a travel video
    is_travel = classify_is_travel_video(
        video_id=video_id,
        channel_title=channel_title,
        tags=tags,
        title=title,
        description=description,
        top_comments=top_comments,
        transcript=transcript
    )

    print(f"Is travel video? {is_travel}")

    # 4. If it IS a travel video, extract structured features
    if is_travel:

        #this is the features
        features = extract_video_features_for_video(
            video_id=video_id,
            title=title,
            description=description,
            top_comments=top_comments,
            transcript=transcript
        )
        print("Extracted video features successfully")
        # --- DATABASE INSERTION ---
        
        if MONGODB_URI:
            try:
                # Initialize MongoDB Client
                db_client = MongoClient(MONGODB_URI)
                db = db_client["travel_app"]
                
                # Build context mapping for the save function
                ctx = {
                    "video_id": video_id,
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "top_comments": top_comments,
                    "channel_id": channel_id,
                    "channel_title": channel_title,
                }
                
                # Save into the collections
                n_ids, c_ids = save_features_to_collections(db, ctx, features)
                print(f"[SUCCESS] Saved to MongoDB. Inserted {len(n_ids)} narratives and {len(c_ids)} claims.")
            except Exception as e:
                print(f"[ERROR] Failed to save to MongoDB: {e}")
        else:
            print("[WARN] MONGODB_URI not found. Skipping database insertion.")
        #sanity check for embedding vector shape : PASS
        # vec = np.array(features["video_components"]["narratives"][0]["claims"][0]["claim_title_embedding"], dtype=float)
        # print("Dim:", vec.shape[0])
        # print("Min:", vec.min(), "Max:", vec.max())
        # print("Norm:", np.linalg.norm(vec))
        # You can still access just countries with: features["countries"]
    else:
        print("Not a travel video; skipping feature extraction.")


# TO DO
# LATER
    # - Add more robust error handling and logging
    # - Consider adding a feedback loop where you can correct the model's output and have it learn from those corrections over time (e.g., using few-shot examples or fine-tuning on a labeled
    #   dataset of travel videos with known features)

# CONNECT TO EMBEDDING MODEL ... gemini 
# use the ttext-embedding-004 model to create embeddings for the extracted features and store those embeddings in a vector database for later retrieval and similarity search.
# features to emed: 
# CREATE A THE EMBEDDINGS AND ADD IT TO THE FEATURES THING AS A JSON ENTRY..
# sene a post request with video id and the features to a new endpoint in the fastapi server that will store the features in a database for later retrieval and use in a search index or something