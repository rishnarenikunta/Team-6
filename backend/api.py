# Run: uvicorn api:app --reload --port 8000

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import Any
from typing import Any, Dict, List, Optional

load_dotenv()

app = FastAPI(title="Travel App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]


def make_slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text).strip("-")
    return text

# ── /api/claims/trending ──────────────────────────────────────────────────────
# Returns top claims per destination from the top_narratives cluster results
from datetime import datetime, timedelta

# api/creators/page

@app.get("/api/creators/page")
def get_creators_page() -> list[dict[str, Any]]:
    """
    Creators list view for creators/page.tsx.

    Returns an array of Creator objects:
    {
      slug, name, region, domain, subscribers, monthlyViews,
      contentType, videos[], commentVolume30d, sentiment, spotlightComment
    }
    """

    # 1. Base creators
    creators = list(db["creators"].find({}))

    # Helper: map channel_id -> metadata docs and video_ids
    # Fetch all metadata for all these creators in one go
    channel_ids = [c["channel_id"] for c in creators if "channel_id" in c]
    metadata_docs = list(
        db["metadata"].find(
            {"channel.channel_id": {"$in": channel_ids}}
        )
    )

    metadata_by_channel: dict[str, list[dict[str, Any]]] = {}
    for doc in metadata_docs:
        ch_id = doc.get("channel", {}).get("channel_id")
        if not ch_id:
            continue
        metadata_by_channel.setdefault(ch_id, []).append(doc)

    # 2. Fetch comments for all those videos (for joins)
    all_video_ids: list[str] = []
    for docs in metadata_by_channel.values():
        for d in docs:
            vid = d.get("video_id")
            if vid:
                all_video_ids.append(vid)

    comments_by_video: dict[str, list[dict[str, Any]]] = {}
    if all_video_ids:
        comment_docs = list(
            db["comments"].find(
                {"video_id": {"$in": all_video_ids}},
                {"_id": 0, "video_id": 1, "text": 1, "like_count": 1, "timestamp": 1}
            )
        )
        for c in comment_docs:
            vid = c.get("video_id")
            if not vid:
                continue
            comments_by_video.setdefault(vid, []).append(c)

    now_ts = int(datetime.utcnow().timestamp())
    thirty_days_ago_ts = now_ts - int(timedelta(days=30).total_seconds())

    results: list[dict[str, Any]] = []

    for creator in creators:
        channel_id = creator.get("channel_id")
        if not channel_id:
            continue

        # ----- slug -----
        handle = creator.get("handle")  # e.g. "@iJustine"
        if handle and isinstance(handle, str) and handle.startswith("@"):
            slug = handle[1:].lower()
        elif handle and isinstance(handle, str):
            slug = handle.lower()
        else:
            slug = channel_id.lower()

        # ----- videos & monthly views -----
        creator_metadata = metadata_by_channel.get(channel_id, [])
        videos: list[dict[str, Any]] = []
        monthly_views_total = 0

        creator_video_ids: list[str] = []

        for doc in creator_metadata:
            video_id = doc.get("video_id")
            if video_id:
                creator_video_ids.append(video_id)

            stats = doc.get("stats", {}) or {}
            view_count = stats.get("view_count", 0) or 0
            monthly_views_total += view_count

            videos.append({
                "title": doc.get("title", ""),
                "img": "",  # no thumbnail field shown in schema; fill later if added
                "link": doc.get("webpage_url", ""),
            })

        # ----- comments: commentVolume30d & spotlightComment -----
        comment_volume_30d = 0
        spotlight_comment = ""

        # Gather all comments for this creator's videos
        creator_comments: list[dict[str, Any]] = []
        for vid in creator_video_ids:
            creator_comments.extend(comments_by_video.get(vid, []))

        # Count last 30 days and pick top-liked recent comment
        best_comment = None
        best_likes = -1

        for c in creator_comments:
            ts = c.get("timestamp")
            if isinstance(ts, (int, float)):
                if ts >= thirty_days_ago_ts:
                    comment_volume_30d += 1
                    likes = c.get("like_count", 0) or 0
                    if likes > best_likes and c.get("text"):
                        best_likes = likes
                        best_comment = c

        if best_comment and best_comment.get("text"):
            spotlight_comment = best_comment["text"]

        # ----- sentiment placeholder -----
        sentiment = {
            "positive": 0,
            "neutral": 100,
            "negative": 0,
        }

        # ----- region & domain -----
        category = creator.get("category", "")  # e.g. "Tech", "Travel & Events"
        domain = category or ""

        # Simple region heuristic placeholder (can be replaced with real mapping)
        region = "Americas"

        # contentType must match your union: "Travel" | "Food" | ...
        # Map from category to one of those; default to "Travel".
        content_type = "Travel"
        if isinstance(category, str):
            lower_cat = category.lower()
            if "tech" in lower_cat:
                content_type = "Tech"
            elif "news" in lower_cat:
                content_type = "News"
            elif "food" in lower_cat:
                content_type = "Food"
            elif "entertain" in lower_cat:
                content_type = "Entertainment"
            elif "vlog" in lower_cat or "lifestyle" in lower_cat:
                content_type = "Lifestyle/Vlog"
            elif "wellness" in lower_cat or "health" in lower_cat:
                content_type = "Wellness"
            elif "travel" in lower_cat:
                content_type = "Travel"

        results.append({
            "slug": slug,
            "name": creator.get("name", ""),
            "region": region,
            "domain": domain,
            "subscribers": creator.get("subscriber_count", 0) or 0,
            "monthlyViews": monthly_views_total,
            "contentType": content_type,
            "videos": videos,
            "commentVolume30d": comment_volume_30d,
            "sentiment": sentiment,
            "spotlightComment": spotlight_comment,
        })

    return results

@app.get("/api/claims/trending")
def get_trending_claims() -> list[dict[str, Any]]:
    docs = list(db["top_claims"].find({}))

    # Build a creator lookup map
    creators = list(db["creators"].find({}, {"_id": 0}))
    creator_map = {c["channel_id"]: c for c in creators}

    result = [
        {
            "id":           str(doc["_id"]),
            "text":         doc.get("claimText", ""),
            "destination":  doc.get("country", ""),
            "cluster_size": doc.get("clusterSize", 0),
            "computed_at":  doc["computedAt"].isoformat() if doc.get("computedAt") else None,
            # Join creator info
            "source":       doc.get("creatorID", ""),
            "creator_name": creator_map.get(doc.get("creatorID", ""), {}).get("name", ""),
            "views":        creator_map.get(doc.get("creatorID", ""), {}).get("views", 0),
        }
        for doc in docs
    ]
    print("TRENDING CLAIMS RESPONSE:")
    print(result)

    return result

@app.get("/api/topics/trending")
def get_trending_topics() -> dict:
    # Pull distinct destinations or tags from your DB
    destinations = db["narratives"].distinct("destination")
    return {"topics": destinations}

@app.get("/api/narratives/trending")
def get_trending_narratives() -> list[dict[str, Any]]:
    docs = list(
        db["top_narratives"]
        .find({})
        .sort("clusterSize", -1)   # sort by largest clusters first
        .limit(7)                  # only take top 7
    )


    creators = list(db["creators"].find({}, {"_id": 0}))
    creator_map = {c["channel_id"]: c for c in creators}

    result = [
        {
            "id":           str(doc["_id"]),
            "text":         doc.get("narrative", ""),
            "destination":  doc.get("typeID", ""),
            "cluster_size": doc.get("clusterSize", 0),
            "computed_at":  doc["computedAt"].isoformat() if doc.get("computedAt") else None,
            "source":       doc.get("channel_id", ""),
            "creator_name": creator_map.get(doc.get("channel_id", ""), {}).get("name", ""),
            "views":        creator_map.get(doc.get("channel_id", ""), {}).get("views", 0),
        }
        for doc in docs
    ]

    print("TRENDING NARRATIVES RESPONSE:")
    print(result)

    return result

@app.get("/api/destinations")
def get_destinations(
    region: Optional[str] = None,
    tag: Optional[str] = None,
) -> List[Dict[str, Any]]:

    REGIONS: Dict[str, List[str]] = {
    "asia":     ["Japan", "South Korea", "Thailand", "Vietnam"],
    "europe":   ["Portugal", "France", "Italy", "Spain", "Germany"],
    "americas": ["Mexico", "USA", "Canada", "Brazil"],
}

    # Get all unique destinations from narratives
    match: dict = {}
    if region:
        countries = REGIONS.get(region.lower(), [])
        if countries:
            # Filter narratives by country — need to join with a lookup
            # since country is not stored in new seed; filter by known destination lists
            dest_by_region = {
                "asia":     ["Kyoto", "Tokyo", "Seoul"],
                "europe":   ["Lisbon"],
                "americas": [],
            }
            allowed = dest_by_region.get(region.lower(), [])
            if allowed:
                match["destination"] = {"$in": allowed}

    if tag:
        match["highlights"] = tag.lower()

    # Get one representative narrative per destination from top_narratives
    top_query: dict = {"scope_type": "destination", "content_type": "narratives"}
    top_docs = list(db["top_narratives"].find(top_query))
    top_by_dest = {doc["destination_id"]: doc for doc in top_docs}

    # Get all destinations that have narratives
    all_destinations = db["narratives"].distinct("destination", match)

    results = []
    for dest in all_destinations:
        top = top_by_dest.get(dest)
        # Fall back to any raw narrative if cluster hasn't run yet
        if not top:
            raw = db["narratives"].find_one({"destination": dest})
            if not raw:
                continue
            results.append({
                "id":          str(raw["_id"]),
                "name":        dest,
                "blurb":       raw.get("narrative_text", ""),
                "top_narrative": None,
                "cluster_size": None,
                "computed_at": None,
            })
        else:
            results.append({
                "id":            str(top["_id"]),
                "name":          dest,
                "blurb":         top.get("top_narrative", ""),
                "top_narrative": top.get("top_narrative", ""),
                "cluster_size":  top.get("cluster_size", 0),
                "computed_at":   top["computed_at"].isoformat() if top.get("computed_at") else None,
            })

    return results


# ── /api/destinations/{name}  ─────────────────────────────────────────────────
# Destination detail page — top narrative + all raw claims for that destination

@app.get("/api/destinations/{destination_name}")
def get_destination(destination_name: str) -> dict[str, Any]:

    # Find top narrative for this destination
    top = db["top_narratives"].find_one({
        "destination_id": {"$regex": destination_name, "$options": "i"},
        "scope_type": "destination",
        "content_type": "narratives"
    })

    # Fall back to raw narrative if cluster hasn't run
    if not top:
        raw = db["narratives"].find_one(
            {"destination": {"$regex": destination_name, "$options": "i"}}
        )
        if not raw:
            raise HTTPException(status_code=404, detail="Destination not found")
        dest_name = raw["destination"]
        blurb = raw.get("narrative_text", "")
        cluster_size = None
        computed_at = None
        doc_id = str(raw["_id"])
    else:
        dest_name = top["destination_id"]
        blurb = top.get("top_narrative", "")
        cluster_size = top.get("cluster_size")
        computed_at = top["computed_at"].isoformat() if top.get("computed_at") else None
        doc_id = str(top["_id"])

    # Get all claims for this destination
    claims = list(
        db["claims"].find(
            {"destination": dest_name},
            {"_id": 0, "claim_text": 1, "source": 1, "claim_risk": 1, "date": 1}
        )
    )

    # Get top claim from cluster results
    top_claim = db["top_narratives"].find_one({
        "destination_id": dest_name,
        "scope_type": "destination",
        "content_type": "claims"
    })

    return {
        "id":            doc_id,
        "name":          dest_name,
        "blurb":         blurb,
        "cluster_size":  cluster_size,
        "computed_at":   computed_at,
        "top_claim":     top_claim.get("top_narrative") if top_claim else None,
        "claims":        claims,
    }


# ── /api/creators  ────────────────────────────────────────────────────────────
# Returns all creators with their top claim narrative from cluster results

@app.get("/api/creators")
def get_creators() -> list[dict[str, Any]]:
    creators = list(db["creators"].find({}, {"_id": 0}))

    top_docs = list(db["top_narratives"].find({
        "scope_type": "source",
        "content_type": "claims"
    }))
    top_by_creator = {doc["channel_id"]: doc for doc in top_docs}

    results = []
    for creator in creators:
        cid = creator["channel_id"]
        top = top_by_creator.get(cid)
        results.append({
            "channel_id":      cid,
            "name":            creator.get("name", ""),
            "subscriber_count": creator.get("subscriber_count", 0),
            "views":           creator.get("views", 0),
            "top_claim":       top.get("top_narrative") if top else None,
            "cluster_size":    top.get("cluster_size") if top else None,
            "computed_at":     top["computed_at"].isoformat() if top and top.get("computed_at") else None,
        })

    return results


# ── /api/creators/{channel_id}  ───────────────────────────────────────────────

@app.get("/api/creators/{channel_id}")
def get_creator(channel_id: str) -> dict[str, Any]:
    creator = db["creators"].find_one({"channel_id": channel_id}, {"_id": 0})
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    top = db["top_narratives"].find_one({
        "channel_id": channel_id,
        "scope_type": "source",
        "content_type": "claims"
    })

    claims = list(
        db["claims"].find(
            {"source": channel_id},
            {"_id": 0, "claim_text": 1, "destination": 1, "claim_risk": 1, "date": 1}
        )
    )

    return {
        "channel_id":       channel_id,
        "name":             creator.get("name", ""),
        "subscriber_count": creator.get("subscriber_count", 0),
        "views":            creator.get("views", 0),
        "join_date":        creator["join_date"].isoformat() if creator.get("join_date") else None,
        "top_claim":        top.get("top_narrative") if top else None,
        "cluster_size":     top.get("cluster_size") if top else None,
        "computed_at":      top["computed_at"].isoformat() if top and top.get("computed_at") else None,
        "claims":           claims,
    }


print("Total narratives:", db["narratives"].count_documents({}))
print("Total claims:",     db["claims"].count_documents({}))
print("Top narratives computed:", db["top_narratives"].count_documents({}))
print("Top claims computed:", db["top_claims"].count_documents({}))

from collections import Counter

# api cretors slug
@app.get("/api/creators/{slug}/page")
def get_creator_page(slug: str) -> dict[str, Any]:
    """
    Detailed creator view used by creators/[slug]/page.tsx.
    `slug` is treated as the YouTube handle (e.g. '@iJustine') or channel_id.
    """

    # 1. Find creator by handle (preferred) or channel_id fallback
    creator = db["creators"].find_one({"handle": slug}, {"_id": 0})
    if not creator:
        creator = db["creators"].find_one({"channel_id": slug}, {"_id": 0})

    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    channel_id = creator["channel_id"]

    # 2. Fetch all metadata for this creator's videos
    metadata_docs = list(
        db["metadata"].find(
            {"channel.channel_id": channel_id}
        )
    )

    # Build videos array for frontend
    videos = []
    video_ids = []
    for doc in metadata_docs:
        video_id = doc.get("video_id", "")
        video_ids.append(video_id)

        stats = doc.get("stats", {}) or {}
        view_count = stats.get("view_count", 0)

        videos.append({
            "title": doc.get("title", ""),
            "views": str(view_count),  # frontend expects string
            "img": "",                 # thumbnail URL not in schema sample; fill in later if added
            "link": doc.get("webpage_url", ""),
        })

    # 3. Aggregate tags across videos -> simple topThemes
    tag_counter: Counter[str] = Counter()
    for doc in metadata_docs:
        tags = doc.get("tags", []) or []
        for tag in tags:
            if isinstance(tag, str):
                tag_counter[tag] += 1

    # Top 10 tags as themes
    topThemes = [tag for tag, _ in tag_counter.most_common(10)]

    # 4. Highlighted comments: top-liked comments across these videos
    highlightedComments: list[str] = []
    if video_ids:
        comment_docs = list(
            db["comments"]
            .find(
                {"video_id": {"$in": video_ids}},
                {"_id": 0, "text": 1, "like_count": 1}
            )
            .sort("like_count", -1)
            .limit(10)
        )
        highlightedComments = [
            c.get("text", "") for c in comment_docs if c.get("text")
        ]

    # 5. Basic derived fields for ContentCreator type
    # You can refine these mappings once you have more business logic:
    # - domain: from creator["category"] or a separate field
    # - region: from your own channel-region mapping table
    domain = creator.get("category", "")  # e.g. "Tech", "Travel", etc.

    # Simple default region; replace with real mapping logic if you have one
    region = "Americas"

    # Monthly views: naive placeholder using total views; you can compute
    # 30-day rolling views later if you store per-video time-series.
    monthlyViews = creator.get("views", 0)

    # Sentiment: placeholder neutral distribution until you have model outputs.
    sentiment = {
        "positive": 0,
        "neutral": 100,
        "negative": 0,
    }

    return {
        "slug": slug,
        "name": creator.get("name", ""),
        "region": region,
        "domain": domain,
        "subscribers": creator.get("subscriber_count", 0),
        "monthlyViews": monthlyViews,
        "contentType": domain if domain else "Travel",  # fits your union type
        "videos": videos,
        "profilePhoto": None,  # fill once you add this to the creators schema
        "sentiment": sentiment,
        "topThemes": topThemes,
        "highlightedComments": highlightedComments,
    }




from datetime import datetime, timezone
from typing import Any, Dict, List
from collections import Counter

# Helper to build a URL-safe slug from narrative text
def make_slug(text: str) -> str:
    import re
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug


@app.get("/api/narratives/{slug}")
def get_narrative_detail(slug: str) -> Dict[str, Any]:
    """
    Narrative detail view for narratives/[slug]/page.tsx.
    Joins:
      - top_narratives (cluster)
      - narratives (raw narrative docs)
      - claims (per narrative)
      - metadata (video info)
      - creators (channel -> creator slug)
    """

    # 1. Find the top narrative document by matching slug against its narrative text
    top_doc = db["top_narratives"].find_one({
        "content_type": "narratives"
    })

    # If you store slugs in DB later, you can replace this with a direct field lookup:
    # top_doc = db["top_narratives"].find_one({"slug": slug})

    if not top_doc:
        raise HTTPException(status_code=404, detail="Narrative not found")

    # If you have multiple top_narratives, select the one whose narrative text matches this slug best
    # For now, we naïvely scan and match by slugified narrative text.
    all_top_docs = list(
        db["top_narratives"].find(
            {"content_type": "narratives"}
        )
    )

    selected_top = None
    for doc in all_top_docs:
        narrative_text = doc.get("narrative", "")
        if not narrative_text:
            continue
        if make_slug(narrative_text) == slug:
            selected_top = doc
            break

    if not selected_top:
        # fallback: use the first doc as a placeholder
        selected_top = all_top_docs[0]

    top_doc = selected_top

    narrative_text = top_doc.get("narrative", "")
    narrative_id = top_doc.get("narrativeID")
    destination_id = top_doc.get("typeID")  # e.g. "Lisbon", "Slow travel in Japan countryside" etc.
    channel_id = top_doc.get("channel_id")

    # 2. Collect all raw narratives in this cluster (for counts & linking)
    # If you store clustered narrative IDs, you’d use those; with the sample, we approximate by destination_id.
    raw_narratives = list(
        db["narratives"].find(
            {"destination": destination_id}
        )
    )

    videos_analyzed = len(raw_narratives)

    # 3. Claims for this narrative cluster
    # If you have a field tying claims directly to narrativeID, use it; here we use destination + narrative_id when present.
    claims_query: Dict[str, Any] = {}
    if destination_id:
        claims_query["destination"] = destination_id
    if narrative_id:
        claims_query["narrative_id"] = narrative_id

    claims_docs = list(db["claims"].find(claims_query))

    # Map each claim to your Claim type
    claims: List[Dict[str, Any]] = []
    for c in claims_docs:
        text = c.get("claim_text", "")
        source = c.get("source", "")
        risk = c.get("claim_risk", "Low")  # Low/Medium/High in DB
        # Engagement / growth: placeholders until you store real metrics
        engagement = "0%"
        growth = "0%"

        claims.append({
            "text": text,
            "source": source,
            "risk": risk.lower(),  # match TS union: "low" | "medium" | "high"
            "engagement": engagement,
            "growth": growth,
        })

    claims_count = len(claims)

    # 4. Videos + top creators
    # Use the narratives' video_ids to fetch metadata and map to VideoDetail
    video_ids: List[str] = []
    channel_ids: List[str] = []

    for n in raw_narratives:
        vid = n.get("video_id")
        if vid:
            video_ids.append(vid)
        ch = n.get("channel_id")
        if ch:
            channel_ids.append(ch)

    # Include the top_narrative's video_id/channel_id as well if not present
    if top_doc.get("video_id"):
        video_ids.append(top_doc["video_id"])
    if channel_id:
        channel_ids.append(channel_id)

    # De-duplicate
    video_ids = list({v for v in video_ids if v})
    channel_ids = list({c for c in channel_ids if c})

    metadata_docs = []
    if video_ids:
        metadata_docs = list(
            db["metadata"].find(
                {"video_id": {"$in": video_ids}}
            )
        )

    # Map channel_id -> creator document for topCreators
    creators_map: Dict[str, Dict[str, Any]] = {}
    if channel_ids:
        creators_docs = list(
            db["creators"].find(
                {"channel_id": {"$in": channel_ids}}
            )
        )
        for cr in creators_docs:
            cid = cr.get("channel_id")
            if cid:
                creators_map[cid] = cr

    # Count distinct creators
    creators_count = len(creators_map)

    # Build topCreators array (use subscriber_count as a simple ranking)
    sorted_creators = sorted(
        creators_map.values(),
        key=lambda c: c.get("subscriber_count", 0),
        reverse=True
    )

    top_creators: List[Dict[str, Any]] = []
    for cr in sorted_creators[:10]:
        handle = cr.get("handle", "")
        if handle and isinstance(handle, str) and handle.startswith("@"):
            creator_slug = handle[1:].lower()
        elif handle and isinstance(handle, str):
            creator_slug = handle.lower()
        else:
            creator_slug = cr.get("channel_id", "")

        top_creators.append({
            "name": cr.get("name", ""),
            "slug": creator_slug,
        })

    # 5. Build VideoDetail list with nested VideoClaim
    videos: List[Dict[str, Any]] = []

    # Pre-group claims by video if you store video_id on claims (you do)
    claims_by_video: Dict[str, List[Dict[str, Any]]] = {}
    for c in claims_docs:
        vid = c.get("video_id")
        if not vid:
            continue
        claims_by_video.setdefault(vid, []).append(c)

    for md in metadata_docs:
        vid = md.get("video_id")
        stats = md.get("stats", {}) or {}
        title = md.get("title", "")
        channel_info = md.get("channel", {}) or {}
        channel_name = channel_info.get("channel_id", "")  # You might replace with creator name if available

        # Views as string
        view_count = stats.get("view_count", 0) or 0
        views_str = str(view_count)

        # Published: convert upload_date (YYYY-MM-DD) to "X months ago" style placeholder
        upload_date_str = md.get("upload_date")
        published = ""
        if upload_date_str:
            try:
                dt = datetime.strptime(upload_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                # Simple relative placeholder; your frontend can do better
                published = dt.date().isoformat()
            except Exception:
                published = upload_date_str

        # Summary: use narrative_text or a short phrase if you have a summary field later
        summary = f"Narrative around {destination_id}" if destination_id else ""

        # Sentiment & riskCallouts: placeholders until you store real values
        sentiment_value = "positive"
        risk_callouts = ""

        # Build VideoClaim array from claims_by_video
        video_claims_raw = claims_by_video.get(vid, [])
        video_claims: List[Dict[str, Any]] = []
        for vc in video_claims_raw:
            video_claims.append({
                "title": title,
                "text": vc.get("claim_text", ""),
                "risk": (vc.get("claim_risk", "Low") or "Low").lower(),
            })

        videos.append({
            "title": title,
            "channel": channel_name,
            "views": views_str,
            "published": published,
            "thumb": "",  # add thumbnail field if present in metadata, e.g. md["thumbnail_url"]
            "summary": summary,
            "sentiment": sentiment_value,
            "riskCallouts": risk_callouts,
            "claims": video_claims,
        })

    # 6. Narrative-level sentiment & velocity
    # Placeholder until you store these metrics
    sentiment_label = "positive"
    sentiment_score = "0.85"    # e.g. stringified score
    velocity = "steady"         # could be "spiking", "declining", etc.

    narrative_detail: Dict[str, Any] = {
        "slug": slug,
        "title": narrative_text or destination_id or slug.replace("-", " ").title(),
        "summary": narrative_text,  # or a shorter summary if you store one
        "videosAnalyzed": videos_analyzed,
        "claimsCount": claims_count,
        "creatorsCount": creators_count,
        "sentimentScore": sentiment_score,
        "velocity": velocity,
        "sentiment": sentiment_label,
        "topCreators": top_creators,
        "claims": claims,
        "videos": videos,
    }

    return narrative_detail


@app.get("/api/narratives")
def get_narratives_index() -> List[Dict[str, Any]]:
    """
    List view for narratives/page.tsx.

    Returns an array of Narrative objects:
    {
      slug, title, region, sentiment, velocity,
      creators, watchtime, claim, risk, tags
    }
    """

    # Base: all top_narratives that represent narrative clusters
    top_docs = list(
        db["top_narratives"].find(
            {"content_type": "narratives"}
        )
    )
    if not top_docs:
        return []

    # Collect IDs for joins
    destination_ids: List[str] = []
    channel_ids: List[str] = []
    video_ids: List[str] = []

    for doc in top_docs:
        dest = doc.get("typeID")
        if dest:
            destination_ids.append(dest)

        ch = doc.get("channel_id")
        if ch:
            channel_ids.append(ch)

        vid = doc.get("video_id")
        if vid:
            video_ids.append(vid)

    destination_ids = list({d for d in destination_ids if d})
    channel_ids = list({c for c in channel_ids if c})
    video_ids = list({v for v in video_ids if v})

    # Creators lookup
    creators_by_channel: Dict[str, Dict[str, Any]] = {}
    if channel_ids:
        creators_docs = list(
            db["creators"].find(
                {"channel_id": {"$in": channel_ids}}
            )
        )
        for cr in creators_docs:
            cid = cr.get("channel_id")
            if cid:
                creators_by_channel[cid] = cr

    # Claims grouped by destination
    claims_by_destination: Dict[str, List[Dict[str, Any]]] = {}
    if destination_ids:
        claims_docs = list(
            db["claims"].find(
                {"destination": {"$in": destination_ids}}
            )
        )
        for c in claims_docs:
            dest = c.get("destination")
            if dest:
                claims_by_destination.setdefault(dest, []).append(c)

    # Metadata grouped by video_id
    metadata_by_video: Dict[str, Dict[str, Any]] = {}
    if video_ids:
        metadata_docs = list(
            db["metadata"].find(
                {"video_id": {"$in": video_ids}}
            )
        )
        for md in metadata_docs:
            vid = md.get("video_id")
            if vid:
                metadata_by_video[vid] = md

    results: List[Dict[str, Any]] = []

    for top_doc in top_docs:
        narrative_text = top_doc.get("narrative", "")
        dest = top_doc.get("typeID")
        ch_id = top_doc.get("channel_id")
        vid = top_doc.get("video_id")

        # slug + title from narrative text (or fallback to destination)
        base_text = narrative_text or (dest or "")
        slug = make_slug(base_text)
        title = base_text

        # region from destination using same buckets as /api/destinations
        region = "Global"
        if isinstance(dest, str):
            d_lower = dest.lower()
            if d_lower in ["japan", "south korea", "thailand", "vietnam"]:
                region = "APAC"
            elif d_lower in ["portugal", "france", "italy", "spain", "germany"]:
                region = "EMEA"
            elif d_lower in ["mexico", "usa", "canada", "brazil"]:
                region = "Americas"

        # sentiment & velocity – placeholders to satisfy type
        sentiment = "positive"
        velocity = "steady"

        # creators: primary label from the cluster's channel_id
        creators_str = ""
        creator = creators_by_channel.get(ch_id)
        if creator:
            creators_str = (
                creator.get("name")
                or creator.get("handle")
                or ch_id
                or ""
            )
        else:
            creators_str = ch_id or ""

        # watchtime: approximate from view_count on that video (if any)
        watchtime_str = ""
        md = metadata_by_video.get(vid) if vid else None
        if md:
            stats = md.get("stats", {}) or {}
            view_count = stats.get("view_count", 0) or 0
            watchtime_str = f"{view_count:,} views"

        # representative claim + risk from this destination
        claim_text = ""
        risk_text = ""
        dest_claims = claims_by_destination.get(dest, [])
        if dest_claims:
            c0 = dest_claims[0]
            claim_text = c0.get("claim_text", "")
            risk_raw = (c0.get("claim_risk", "") or "").capitalize()
            risk_text = f"{risk_raw} brand safety risk" if risk_raw else ""

        # tags from metadata.tags
        tags: List[str] = []
        if md:
            md_tags = md.get("tags", []) or []
            tags = [t for t in md_tags if isinstance(t, str)]

        results.append({
            "slug": slug,
            "title": title,
            "region": region,
            "sentiment": sentiment,
            "velocity": velocity,
            "creators": creators_str,
            "watchtime": watchtime_str,
            "claim": claim_text,
            "risk": risk_text,
            "tags": tags,
        })

    return results
