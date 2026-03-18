claims_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["claim_id", "video_id", "claim_text"],
        "properties": {
            "claim_id": {"bsonType": "string"},
            "narrative_id": {"bsonType": "string"},
            "video_id": {"bsonType": "string"},
            "claim_text": {"bsonType": "string"},
            "claim_vector": {
                "bsonType": "array",
                "items": {"bsonType": "double"}
            },
            "risk": {
                "bsonType": "object",
                "properties": {
                    "sentiment_percent": {"bsonType": "double"},
                    "risk": {"bsonType": "string"}
                }
            },
            "date": {"bsonType": "date"}
        }
    }
}

db.create_collection("claims", validator=claims_validator)