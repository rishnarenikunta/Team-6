# classifyVideos.py

import os
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.cluster import KMeans
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Video Travel Classification API")


class Comment(BaseModel):
    text: str


class VideoInput(BaseModel):
    video_id: str
    channel_title: str
    tags: List[str]
    top_comments: List[Comment]


class TravelClassificationResponse(BaseModel):
    video_id: str
    label: Literal["Travel", "Non-Travel"]
    cluster_id: int
    cluster_travel_probability: float


class BatchTravelRequest(BaseModel):
    videos: List[VideoInput]
    k: int = 2  # number of clusters, default 2 (travel vs non-travel)
    embedding_model: str = "text-embedding-3-small"


def build_video_text_repr(video: VideoInput) -> str:
    """Concatenate channel title, tags, comments into a single text blob."""
    tags_text = " ".join(video.tags)
    comments_text = " ".join(c.text for c in video.top_comments)
    merged = f"Channel: {video.channel_title}\nTags: {tags_text}\nComments: {comments_text}"
    return merged.strip()


def embed_texts(texts: List[str], model: str) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI embedding API.
    """
    if not client.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    # OpenAI Python SDK v1 style
    resp = client.embeddings.create(
        model=model,
        input=texts,
    )
    return [d.embedding for d in resp.data]


@app.post("/classify/videos/travel", response_model=List[TravelClassificationResponse])
def classify_videos_travel(req: BatchTravelRequest):
    if len(req.videos) < req.k:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least k={req.k} videos to cluster.",
        )

    # 1. Build text representation
    corpus = [build_video_text_repr(v) for v in req.videos]

    # 2. Embed
    try:
        embeddings = embed_texts(corpus, req.embedding_model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    X = np.array(embeddings)

    # 3. K-Means clustering
    try:
        kmeans = KMeans(n_clusters=req.k, random_state=42, n_init=10)
        cluster_ids = kmeans.fit_predict(X)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KMeans failed: {str(e)}")

    # 4. Identify which cluster(s) are "Travel"
    #    We do this heuristically by checking how "travel-y" the centroid texts are
    #    using a classification prompt on cluster-level summaries.
    #    (Simpler alternative: search for travel keywords in cluster texts.)
    cluster_texts = {cid: [] for cid in range(req.k)}
    for video, cid in zip(req.videos, cluster_ids):
        cluster_texts[cid].append(build_video_text_repr(video))

    cluster_labels = {}
    cluster_probs = {}

    for cid in range(req.k):
        # Concatenate up to N examples to describe the cluster
        examples = cluster_texts[cid][:10]
        cluster_description = "\n\n---\n\n".join(examples)

        prompt = f"""
You are a classifier. I will give you text snippets related to YouTube videos.
These videos may or may not be about travel, tourism, vlogs, trips, or destinations.

Decide if this CLUSTER of videos is mainly about travel.

Respond ONLY as JSON with keys:
- "label": "Travel" or "Non-Travel"
- "probability": a float between 0 and 1 indicating confidence that this cluster is Travel.

Cluster snippets:
{cluster_description}
"""

        try:
            chat_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a strict JSON-only classifier."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            content = chat_resp.choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cluster classification failed for cluster {cid}: {str(e)}",
            )

        # Very simple / naive JSON parsing
        import json

        try:
            parsed = json.loads(content)
            label = parsed.get("label", "Non-Travel")
            prob = float(parsed.get("probability", 0.5))
        except Exception:
            # fallback heuristic
            label = "Travel" if "travel" in cluster_description.lower() else "Non-Travel"
            prob = 0.5

        cluster_labels[cid] = label
        cluster_probs[cid] = prob

    # 5. Map each video to Travel / Non-Travel using its cluster label
    responses: List[TravelClassificationResponse] = []
    for video, cid in zip(req.videos, cluster_ids):
        responses.append(
            TravelClassificationResponse(
                video_id=video.video_id,
                label=cluster_labels[cid],
                cluster_id=int(cid),
                cluster_travel_probability=float(cluster_probs[cid]),
            )
        )

    return responses
