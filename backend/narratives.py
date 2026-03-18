narrative_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["narrative_id", "video_id", "narrative_text"],
        "properties": {
            "narrative_id": {"bsonType": "string"},
            "video_id": {"bsonType": "string"},
            "narrative_text": {"bsonType": "string"},
            "narrative_vector": {
                "bsonType": "array",
                "items": {"bsonType": "double"}
            },
            "date": {"bsonType": "date"}
        }
    }
}

db.create_collection("narratives", validator=narrative_validator)