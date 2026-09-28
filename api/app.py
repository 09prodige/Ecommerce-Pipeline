import os
import time
import random
import uuid
import psycopg2
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="SOKO COMMERCE - Events API")

# Global variables to cache IDs from Postgres
PROFILE_IDS = []
LISTING_IDS = []

def init_db_connection():
    global PROFILE_IDS, LISTING_IDS
    print("Connecting to PostgreSQL to fetch reference data...")
    # Add retry logic because DB might take a few seconds to start
    for _ in range(10):
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "postgres"),
                port=os.environ.get("DB_PORT", "5432"),
                database=os.environ.get("DB_NAME", "soko_db"),
                user=os.environ.get("DB_USER", "soko_admin"),
                password=os.environ.get("DB_PASSWORD", "soko_password")
            )
            cur = conn.cursor()
            
            cur.execute("SELECT id FROM profiles;")
            PROFILE_IDS = [str(r[0]) for r in cur.fetchall()]
            
            cur.execute("SELECT id FROM listings;")
            LISTING_IDS = [str(r[0]) for r in cur.fetchall()]
            
            cur.close()
            conn.close()
            print(f"Successfully loaded {len(PROFILE_IDS)} profiles and {len(LISTING_IDS)} listings.")
            break
        except Exception as e:
            print(f"Database not ready yet... {e}")
            time.sleep(3)

@app.on_event("startup")
def startup_event():
    init_db_connection()

@app.get("/events")
def generate_events():
    """
    Returns a random number of user action events (e.g. view, like, message, offer).
    """
    # If DB failed to load or is empty, use some fake UUIDs just to not crash
    profiles = PROFILE_IDS if PROFILE_IDS else [str(uuid.uuid4())]
    listings = LISTING_IDS if LISTING_IDS else [str(uuid.uuid4())]
    
    events = []
    num_events = random.randint(1, 5)
    
    action_types = ["view_listing", "view_listing", "view_listing", "like_listing", "send_message", "create_offer"]
    
    for _ in range(num_events):
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": random.choice(profiles),
            "listing_id": random.choice(listings),
            "action_type": random.choice(action_types),
            "device": random.choice(["mobile", "mobile", "desktop", "tablet"])
        }
        events.append(event)
        
    return events

@app.get("/health")
def health_check():
    return {"status": "ok"}
