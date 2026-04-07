import os
import json
import argparse
import time
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import json_util
from google.cloud import run_v2

def run_dispatcher(override_all: bool):
    load_dotenv()
    
    # 1. Connect to MongoDB
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("[ERROR] MONGODB_URI missing.")
        return

    client = MongoClient(mongo_uri)
    db = client["travel_app"]
    videos = db["metadata"]

    # 2. Build Query
    query = {} if override_all else {"is_travel": {"$exists": False}}
    mode_text = "OVERRIDE ALL" if override_all else "MISSING ONLY"
    
    docs = list(videos.find(query))
    total_docs = len(docs)
    
    if total_docs == 0:
        print(f"[INFO] Mode: {mode_text}. No documents to process. Exiting.")
        return

    print(f"[INFO] Mode: {mode_text}. Found {total_docs} documents. Dispatching to youtravel-llm-job...")

    # 3. Initialize Cloud Run Client
    run_client = run_v2.JobsClient()
    job_name = "projects/youtravel-487521/locations/us-central1/jobs/youtravel-llm-job"

    # 4. Loop and Trigger Cloud Run Jobs
    for index, doc in enumerate(docs, start=1):
        video_id = doc.get("_id", "Unknown")
        print(f"[{index}/{total_docs}] Dispatching execution for Video ID: {video_id}...")

        # Serialize document safely handling ObjectIds and Dates
        document_data = json_util.dumps(doc)

        try:
            env_vars = [run_v2.EnvVar(name="MONGO_DOCUMENT", value=document_data)]
            overrides = run_v2.RunJobRequest.Overrides(
                container_overrides=[
                    run_v2.RunJobRequest.Overrides.ContainerOverride(env=env_vars)
                ]
            )

            job_request = run_v2.RunJobRequest(
                name=job_name,
                overrides=overrides
            )
            
            # Asynchronous trigger - fires and forgets
            run_client.run_job(request=job_request)
            
            # Brief sleep to avoid hitting GCP API rate limits if dispatching thousands
            time.sleep(0.1) 

        except Exception as e:
            print(f"[ERROR] Failed to dispatch job for {video_id}: {e}")

    print("\n[SUCCESS] All batch jobs dispatched to Google Cloud Run.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Process all documents and override.")
    parser.add_argument("--collection", type=str, default="metadata", help="MongoDB collection to read from.")
    args = parser.parse_args()
    
    run_dispatcher(override_all=args.all, collection_name=args.collection)