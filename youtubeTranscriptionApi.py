from fastapi import FastAPI, HTTPException
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)

app = FastAPI()

@app.get("/transcript/{video_id}")
def get_transcript(video_id: str):
    ytt = YouTubeTranscriptApi()

    try:
        fetched = ytt.fetch(video_id)
    except (NoTranscriptFound, TranscriptsDisabled):
        raise HTTPException(status_code=404, detail="Transcript not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    text = "\n".join(s.text for s in fetched)

    return {
        "video_id": video_id,
        "text": text
    }