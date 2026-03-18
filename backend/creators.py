creator_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["creator_id"],
        "properties": {
            "creator_id": {"bsonType": "string"},
            "subscriber_count": {"bsonType": "int"},
            "views": {"bsonType": "int"},
            "join_date": {"bsonType": "date"}
        }
    }
}

db.create_collection("creators", validator=creator_validator)