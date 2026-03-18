top_narratives_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "properties": {
            "type": {"enum": ["creator", "country", "overall"]},
            "type_id": {"bsonType": "string"},
            "narrative_text": {"bsonType": "string"},
            "claim_texts": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            },
            "summarized_comments": {"bsonType": "string"},
            "risk": {
                "bsonType": "object",
                "properties": {
                    "sentiment_percent": {"bsonType": "double"},
                    "risk": {"bsonType": "string"}
                }
            },
            "video_ids": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            }
        }
    }
}

db.create_collection("top_narratives", validator=top_narratives_validator)