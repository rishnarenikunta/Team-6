# Setting up Youtube Transcription API

## Setup & Run Instructions

1. Install dependencies
``` pip install fastapi uvicorn youtube-transcript-api ```

2. Start the server
``` uvicorn youtubeTranscriptionApi:app --reload ```

3. Use the API

Endpoint format:

``` GET /transcript/{video_id} ```

Example request:

``` http://127.0.0.1:8000/transcript/FPX6zAA3tJI ```

4. API Documentation

Once the server is running, open:

``` http://127.0.0.1:8000/docs ```

to access the interactive Swagger UI

Example Response

```json 
{
  "video_id": "FPX6zAA3tJI",
  "text": "Never gonna give you up..."
}
```

# Setting up Whisper YouTube Transcription API

## Setup & Run Instructions

1. Install additional dependencies
``` pip install fastapi uvicorn openai yt-dlp ```

Ensure your OpenAI API key is set as an environment variable:

``` export OPENAI_API_KEY="your_openai_api_key" ```

2. Start the server
uvicorn whisperAPI:app --reload
 
3. Use the API

Endpoint format:

``` POST /transcribe/youtube ```

Request body:

``` json
{
  "video_id": "FPX6zAA3tJI"
}
```

4. API Documentation

Once the server is running, open:

``` http://127.0.0.1:8000/docs ```

to access the interactive Swagger UI

Example Response
``` json 
{
  "video_id": "FPX6zAA3tJI",
  "text": "We're no strangers to love..."
}
```
