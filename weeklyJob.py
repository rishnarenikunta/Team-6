import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env FIRST before any other imports
load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    filename=str(Path(__file__).parent / "weekly_job.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logging.info("=== Weekly job started ===")

try:
    from youtubeTranscriptionApi import top_20_videos_by_bucket_store
    top_20_videos_by_bucket_store()
    logging.info("=== Weekly job completed successfully ===")
except Exception as e:
    logging.error(f"=== Weekly job FAILED: {e} ===")