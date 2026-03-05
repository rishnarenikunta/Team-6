"""
backend/seed.py
Run once to populate MongoDB: python seed.py
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from sentence_transformers import SentenceTransformer

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["travel_app"]
client.drop_database("travel_app")
print("Emptying database...")

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text):
    return model.encode(text).tolist()

# ── Validators ────────────────────────────────────────────────────────────────

narrative_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "properties": {
            "narrative_id":     {"bsonType": "string"},
            "destination":      {"bsonType": "string"},
            "country":          {"bsonType": "string"},
            "signal_type":      {"enum": ["narrative_momentum", "search_interest", "watch_time"]},
            "value":            {"bsonType": "double"},
            "risk":             {"bsonType": "string"},
            "highlights":       {"bsonType": "array"},
            "blurb":            {"bsonType": "string"},
            "narrative_vector": {"bsonType": "array", "items": {"bsonType": "double"}},
            "refreshed_at":     {"bsonType": "date"},
        },
    }
}

claims_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "properties": {
            "destination": {"bsonType": "string"},
            "claim_text":  {"bsonType": "string"},
            "claim_vector":{"bsonType": "array", "items": {"bsonType": "double"}},
            "source":      {"bsonType": "string"},
            "claim_risk":  {"bsonType": "string"},
            "date":        {"bsonType": "string"},
        },
    }
}

creator_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "properties": {
            "name":             {"bsonType": "string"},
            "channel_id":       {"bsonType": "string"},
            "views":            {"bsonType": "int"},
            "join_date":        {"bsonType": "date"},
            "subscriber_count": {"bsonType": "int"},
        },
    }
}

existing = db.list_collection_names()
for name, validator in [
    ("creators",   creator_validator),
    ("narratives", narrative_validator),
    ("claims",     claims_validator),
]:
    if name not in existing:
        db.create_collection(name, validator=validator)
        print(f"✅ Created: {name}")
    else:
        db.command("collMod", name, validator=validator)
        print(f"↩  Exists (validator refreshed): {name}")

# ── Creators ──────────────────────────────────────────────────────────────────

db["creators"].insert_many([
    {"name": "WonderWithMia", "channel_id": "UC_mia_01",  "views": 12000000, "join_date": datetime(2018, 5, 1),  "subscriber_count": 980000},
    {"name": "TravelTomo",    "channel_id": "UC_tomo_01", "views": 5400000,  "join_date": datetime(2019, 3, 12), "subscriber_count": 450000},
    {"name": "NomadNick",     "channel_id": "UC_nick_01", "views": 32000000, "join_date": datetime(2016, 8, 20), "subscriber_count": 2100000},
    {"name": "WanderNina",    "channel_id": "UC_nina_01", "views": 4700000,  "join_date": datetime(2020, 1, 10), "subscriber_count": 320000},
])
print("✅ Inserted creators")

# ── Narratives (20 per destination) ──────────────────────────────────────────

kyoto_blurbs = [
    "Autumn in Kyoto is peak season; slow itineraries through Higashiyama draw massive engagement.",
    "Temple-hopping vlogs perform best when creators focus on early morning visits before crowds arrive.",
    "Neighborhood food crawls in Nishiki Market are the top-performing content format for Kyoto.",
    "Creators covering Arashiyama bamboo grove see 3x higher retention than average Japan content.",
    "Ryokan stay content dominates Kyoto watch time; audiences love the tatami and kaiseki experience.",
    "Autumn foliage at Tofuku-ji is the single most clipped moment in Kyoto travel content.",
    "Cycling content around Kyoto outperforms walking vlogs by engagement rate.",
    "Hidden shrines off the tourist trail are generating strong comment section discussion.",
    "Fushimi Inari night visits are an emerging content niche with low competition.",
    "Tea ceremony experience videos consistently earn high save rates from planning audiences.",
    "Day trips to Nara from Kyoto are frequently bundled in high-performing itinerary videos.",
    "Creators highlighting Kyoto's fashion district are seeing younger audience crossover.",
    "Machiya townhouse accommodation content is outperforming hotel content for saves.",
    "Gion district walking tours perform best when published in October and November.",
    "Kyoto street food content — especially yudofu and matcha — sees high rewatch rates.",
    "Budget Kyoto content under $50/day is underserved and trending in search.",
    "The Philosopher's Path in cherry blossom season generates the highest thumbnail CTR.",
    "Creators mixing cultural history with modern Kyoto cafes are building loyal audiences.",
    "Multi-day Kyoto itinerary videos over 20 minutes have the highest completion rates.",
    "Audience sentiment in Kyoto comments skews strongly positive with themes of peace and beauty.",
]

lisbon_blurbs = [
    "Shoulder-season Lisbon content is outperforming summer videos due to lower competition.",
    "Surf day-trips from Lisbon to Cascais are the fastest-growing content niche in Portugal.",
    "Budget travel content under 60 euros per day in Lisbon is seeing strong search-driven growth.",
    "Tram 28 content is highly clipped but creators warn about pickpockets in comments.",
    "Pastel de Belem content is evergreen and consistently drives traffic to Lisbon videos.",
    "Alfama district walking tours perform strongly with older, higher-income audiences.",
    "Nightlife content in Bairro Alto is polarizing — high views but lower save rates.",
    "Sintra day-trip content bundles well with Lisbon city guides for extended watch time.",
    "Miradouros viewpoint content generates the highest average thumbnail click-through rate.",
    "Fado music experience videos are niche but earn exceptionally high audience loyalty.",
    "Lisbon food tour content — especially petiscos — is outperforming restaurant review formats.",
    "Digital nomad content set in Lisbon resonates strongly with the 25 to 34 demographic.",
    "LX Factory weekend market content drives strong weekend publishing performance.",
    "Creators covering Lisbon's art scene see crossover audience from culture-focused channels.",
    "The Mouraria neighborhood is emerging as an underreported content location.",
    "Electric scooter tour content in Lisbon is a growing format with low creator saturation.",
    "Lisbon rooftop bar content consistently earns shares from aspirational travel audiences.",
    "Safety-focused Lisbon content is trending upward after increased search queries.",
    "Azulejo tile hunting content is niche but earns very high save rates.",
    "Multi-generational travel content set in Lisbon is an underserved audience opportunity.",
]

print("Embedding Kyoto narratives...")
kyoto_docs = [
    {
        "narrative_id": f"narr_kyoto_{i+1:02d}",
        "destination": "Kyoto",
        "country": "Japan",
        "signal_type": "narrative_momentum",
        "value": round(8.0 + (i % 5) * 0.8, 1),
        "risk": "Low creator risk",
        "highlights": ["culture", "food", "walkable"],
        "blurb": blurb,
        "narrative_vector": embed(blurb),
        "refreshed_at": datetime.utcnow(),
    }
    for i, blurb in enumerate(kyoto_blurbs)
]

print("Embedding Lisbon narratives...")
lisbon_docs = [
    {
        "narrative_id": f"narr_lisbon_{i+1:02d}",
        "destination": "Lisbon",
        "country": "Portugal",
        "signal_type": "search_interest",
        "value": round(6.0 + (i % 5) * 0.6, 1),
        "risk": "Moderate creator risk",
        "highlights": ["budget", "coast", "nightlife"],
        "blurb": blurb,
        "narrative_vector": embed(blurb),
        "refreshed_at": datetime.utcnow(),
    }
    for i, blurb in enumerate(lisbon_blurbs)
]

db["narratives"].insert_many(kyoto_docs + lisbon_docs)
print(f"✅ Inserted {len(kyoto_docs + lisbon_docs)} narratives with vectors")

# ── Claims (20 per creator, source = channel_id) ──────────────────────────────

mia_claims = [
    ("Tokyo",  "You can eat incredibly well in Tokyo for under $10 a meal."),
    ("Tokyo",  "Tokyo convenience stores are one of the best food experiences in Japan."),
    ("Tokyo",  "Shibuya crossing at night is worth staying up late for."),
    ("Tokyo",  "The teamLab digital art museums are worth the premium ticket price."),
    ("Tokyo",  "Tokyo's train system is confusing at first but mastered within a day."),
    ("Kyoto",  "Arashiyama bamboo grove is best visited before 7am to avoid crowds."),
    ("Kyoto",  "Kyoto temple gardens are among the most peaceful places I have ever visited."),
    ("Kyoto",  "A traditional ryokan stay in Kyoto is expensive but completely worth it."),
    ("Kyoto",  "Nishiki Market is the best place to try local Kyoto street food."),
    ("Kyoto",  "The Philosopher's Path in autumn is the most beautiful walk in Japan."),
    ("Japan",  "Japan is one of the safest countries for solo female travelers."),
    ("Japan",  "Learning a few Japanese phrases goes a long way with locals."),
    ("Japan",  "Japan's convenience stores solve every problem you'll encounter traveling."),
    ("Japan",  "Carrying cash is still essential in Japan despite card acceptance growing."),
    ("Japan",  "The shinkansen bullet train is the most efficient way to travel between cities."),
    ("Lisbon", "Lisbon in October is perfect — warm weather without summer crowds."),
    ("Lisbon", "The pasteis de nata at Pasteis de Belem are genuinely life-changing."),
    ("Lisbon", "Lisbon's miradouros viewpoints are free and offer stunning sunset views."),
    ("Lisbon", "Riding Tram 28 is iconic but keep a close eye on your belongings."),
    ("Lisbon", "Lisbon's Alfama district is best explored with no particular plan."),
]

tomo_claims = [
    ("Tokyo",  "Tokyo's ramen scene is so deep you could eat a different bowl every day for months."),
    ("Tokyo",  "Getting a Suica card on arrival makes navigating Tokyo seamless."),
    ("Tokyo",  "Golden Gai in Shinjuku is the best bar-hopping neighborhood in the world."),
    ("Tokyo",  "Tsukiji outer market for breakfast is one of Tokyo's great rituals."),
    ("Tokyo",  "Harajuku on a Sunday is an unmissable cultural experience."),
    ("Tokyo",  "Akihabara is overwhelming but fascinating even if you're not into anime."),
    ("Tokyo",  "Tokyo's vending machines are a surprisingly good source of cheap meals."),
    ("Tokyo",  "Yanaka is Tokyo's most charming old-town neighborhood and almost tourist-free."),
    ("Tokyo",  "The view from the Tokyo Skytree on a clear day is absolutely worth it."),
    ("Tokyo",  "Tokyo DisneySea is genuinely one of the best theme parks on the planet."),
    ("Kyoto",  "Fushimi Inari is stunning at dusk when most day-trippers have left."),
    ("Kyoto",  "Kyoto's coffee shop scene is world-class and criminally underreported."),
    ("Kyoto",  "Renting a kimono for a day in Kyoto is touristy but genuinely fun."),
    ("Kyoto",  "The bamboo groves outside the main Arashiyama area are crowd-free alternatives."),
    ("Kyoto",  "Kinkaku-ji is crowded but the golden reflection at golden hour is magical."),
    ("Japan",  "Japan in cherry blossom season is worth every crowd and every penny."),
    ("Japan",  "Japan's vending machine culture is one of the most underrated travel experiences."),
    ("Japan",  "Onsen etiquette is easy to learn and makes the experience far more enjoyable."),
    ("Japan",  "Japanese train station bento boxes are often better than sit-down restaurants."),
    ("Japan",  "Hiking in Japan — especially the Nakasendo trail — is world-class and underrated."),
]

nick_claims = [
    ("Japan",  "A 14-day Japan Rail Pass saves significant money if you're doing the full circuit."),
    ("Japan",  "Japan in November for autumn leaves is less crowded than cherry blossom season."),
    ("Japan",  "Osaka is better value than Tokyo for food and accommodation."),
    ("Japan",  "Japan has the best airport transit experience of any country I've visited."),
    ("Japan",  "The rural onsens in Hakone offer a completely different Japan experience."),
    ("Japan",  "Hiroshima is a deeply moving and essential stop on any Japan itinerary."),
    ("Japan",  "Japan's izakayas are the best way to experience local food culture on a budget."),
    ("Japan",  "The overnight sleeper trains in Japan are an underrated travel experience."),
    ("Japan",  "Nara's deer park is one of the most surreal and joyful experiences in travel."),
    ("Japan",  "Japan's hiking trails offer world-class scenery with minimal crowds."),
    ("Tokyo",  "Tokyo has more Michelin-starred restaurants than any other city in the world."),
    ("Tokyo",  "The robot restaurant in Tokyo is tourist-trap pricing but genuinely unforgettable."),
    ("Tokyo",  "Tokyo's neighborhood variety means you could visit ten times and find new areas."),
    ("Tokyo",  "Early morning Tokyo — before 7am — is a completely different and beautiful city."),
    ("Tokyo",  "Spending a full week in Tokyo without leaving the city is entirely justified."),
    ("Seoul",  "Seoul is significantly cheaper than Tokyo for almost every category of spend."),
    ("Seoul",  "The Korean BBQ experience in Mapo-gu is unmatched anywhere in the world."),
    ("Seoul",  "Seoul's subway is the most efficient and affordable metro system I've used."),
    ("Seoul",  "Bukchon Hanok Village at sunrise is one of the most photogenic spots in Asia."),
    ("Seoul",  "The street food in Gwangjang Market is a mandatory first-night experience in Seoul."),
]

nina_claims = [
    ("Seoul",  "T-money card works on every metro line in Seoul including the AREX airport express."),
    ("Seoul",  "Myeongdong street food at night is the most fun $10 you'll spend in Asia."),
    ("Seoul",  "Solo female travel in Seoul feels incredibly safe even very late at night."),
    ("Seoul",  "Korean skincare shopping in Myeongdong offers prices far below Western retail."),
    ("Seoul",  "The Han River park picnic scene is a beautiful slice of everyday Seoul life."),
    ("Seoul",  "Hongdae on a weekend night has the best free street performance culture in Asia."),
    ("Seoul",  "PC bangs in Seoul are a legitimate and cheap way to spend a rainy afternoon."),
    ("Seoul",  "Gwanghwamun Square at dusk with the palace backdrop is unmissable."),
    ("Seoul",  "Taking the cable car up Namsan to N Seoul Tower is worth it for the night view."),
    ("Seoul",  "Seoul's cafe culture is extraordinary — every neighborhood has a design-forward scene."),
    ("Lisbon", "Lisbon's LX Factory on a Sunday is one of Europe's best creative market experiences."),
    ("Lisbon", "The Mouraria neighborhood is authentic, beautiful, and almost entirely tourist-free."),
    ("Lisbon", "Lisbon's digital nomad scene makes it easy to find co-working and community."),
    ("Lisbon", "Sintra is only 40 minutes from Lisbon and feels like a fairytale — don't skip it."),
    ("Lisbon", "Lisbon's sunset from any miradouro is among the best in Europe."),
    ("Lisbon", "The electric tuk-tuks in Lisbon are overpriced — walk or take the tram instead."),
    ("Lisbon", "Lisbon's wine bars in Principe Real are the city's best-kept secret."),
    ("Lisbon", "Fado houses in Alfama are touristy but an emotionally powerful experience."),
    ("Lisbon", "The Mercado da Ribeira Time Out Market is excellent for a first-night food overview."),
    ("Lisbon", "Lisbon's public bike share is the cheapest and most fun way to reach Belem."),
]

print("Embedding claims (this may take a moment)...")
all_claims = []
for source, claim_list in [
    ("UC_mia_01",  mia_claims),
    ("UC_tomo_01", tomo_claims),
    ("UC_nick_01", nick_claims),
    ("UC_nina_01", nina_claims),
]:
    for dest, text in claim_list:
        all_claims.append({
            "destination": dest,
            "claim_text": text,
            "source": source,
            "claim_vector": embed(text),
            "claim_risk": "Low",
            "date": "2024-01-15",
        })

db["claims"].insert_many(all_claims)
print(f"✅ Inserted {len(all_claims)} claims with vectors")

print("\n🎉 Database ready.")
print(f"   Narratives : {db['narratives'].count_documents({})} docs")
print(f"   Claims     : {db['claims'].count_documents({})} docs")
print(f"   Creators   : {db['creators'].count_documents({})} docs")