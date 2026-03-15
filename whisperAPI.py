import os
import tempfile
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Speech-to-Text API")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class YouTubeRequest(BaseModel):
    video_id: str
    model: str = "gpt-4o-mini-transcribe"


@app.post("/transcribe/youtube")
def transcribe_youtube(req: YouTubeRequest):
    if not client.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    video_url = f"https://www.youtube.com/watch?v={req.video_id}"

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            outtmpl = os.path.join(tmpdir, "audio.%(ext)s")

            # 1) Download audio stream only (NO conversion, NO ffmpeg)
            cmd = [
                "python", "-m", "yt_dlp",
                "-f", "bestaudio[ext=m4a]/bestaudio",
                "-o", outtmpl,
                video_url,
            ]

            proc = subprocess.run(cmd, capture_output=True, text=True)

            if proc.returncode != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"yt-dlp failed: {proc.stderr.strip() or proc.stdout.strip()}",
                )

            # 2) Locate downloaded audio file
            audio_file = next(
                f for f in os.listdir(tmpdir) if f.startswith("audio.")
            )
            audio_path = os.path.join(tmpdir, audio_file)

            # 3) Read audio bytes
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            # 4) Transcribe with OpenAI / Whisper
            result = client.audio.transcriptions.create(
                model=req.model,
                file=(audio_file, audio_bytes),
            )

            return {
                "video_id": req.video_id,
                "text": result.text,
            }

    except StopIteration:
        raise HTTPException(status_code=400, detail="Audio file not found after download")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
