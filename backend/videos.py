video_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["video_id", "creator_id", "title", "upload_date"],
        "properties": {
            "video_id": {"bsonType": "string"},
            "creator_id": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "description": {"bsonType": "string"},
            "duration": {"bsonType": "int"},
            "upload_date": {"bsonType": "date"},
            "view_count": {"bsonType": "int"},
            "like_count": {"bsonType": "int"},
            "tags": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            },
            "language": {"bsonType": "string"},
            "comment_count": {"bsonType": "int"},
            "summary": {"bsonType": "string"},
            "overview": {"bsonType": "string"},
            "topics": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            },
            "destinations": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            },
            "sentiment": {
                "bsonType": "object",
                "properties": {
                    "sentiment_percent": {"bsonType": "double"},
                    "risk_text": {"bsonType": "string"}
                }
            },
            "comments": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            }
        }
    }
}

db.create_collection("videos", validator=video_validator)