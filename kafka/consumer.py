import os
import json
import time
import csv
import psycopg2
from datetime import datetime
from kafka import KafkaConsumer

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = "user_actions"
DATALAKE_ROOT = "/datalake/raw"

def export_postgres_reference_data():
    """
    Export profiles and listings from Postgres to the Data Lake (Source 2)
    """
    print("Exporting Postgres Reference Data to Data Lake...")
    os.makedirs(f"{DATALAKE_ROOT}/reference_data", exist_ok=True)
    
    for _ in range(15):
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "postgres"),
                port=os.environ.get("DB_PORT", "5432"),
                database=os.environ.get("DB_NAME", "soko_db"),
                user=os.environ.get("DB_USER", "soko_admin"),
                password=os.environ.get("DB_PASSWORD", "soko_password")
            )
            cur = conn.cursor()
            
            # Export Profiles
            cur.execute("SELECT id, display_name, is_seller FROM profiles;")
            profiles = cur.fetchall()
            with open(f"{DATALAKE_ROOT}/reference_data/profiles.csv", "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "display_name", "is_seller"])
                writer.writerows(profiles)
                
            # Export Listings
            cur.execute("SELECT id, seller_id, category_id, title, price, status FROM listings;")
            listings = cur.fetchall()
            with open(f"{DATALAKE_ROOT}/reference_data/listings.csv", "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "seller_id", "category_id", "title", "price", "status"])
                writer.writerows(listings)
                
            cur.close()
            conn.close()
            print("Successfully exported reference data to Data Lake!")
            return
        except Exception as e:
            print(f"Waiting for Database... {e}")
            time.sleep(5)
            
    print("Failed to export reference data!")

def consume_kafka_events():
    """
    Consume from Kafka and write API events to the Data Lake (Source 1)
    """
    print("Starting Kafka Consumer...")
    os.makedirs(f"{DATALAKE_ROOT}/api_events", exist_ok=True)
    
    consumer = None
    for _ in range(15):
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='datalake_ingestion_group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                api_version=(2,8,1)
            )
            print("Successfully connected to Kafka Topic!")
            break
        except Exception as e:
            print(f"Waiting for Kafka to be ready... {e}")
            time.sleep(5)
            
    if not consumer:
        raise Exception("Failed to connect to Kafka.")

    current_date = datetime.utcnow().strftime('%Y-%m-%d')
    file_path = f"{DATALAKE_ROOT}/api_events/events_{current_date}.jsonl"
    
    print(f"Ready to ingest events into {file_path}...")
    
    with open(file_path, "a", encoding="utf-8") as f:
        for message in consumer:
            event = message.value
            f.write(json.dumps(event) + "\n")
            f.flush()
            print(f"Ingested event {event['event_id']} to Data Lake.")

if __name__ == "__main__":
    time.sleep(15) # Wait for Postgres to fully init schema and data
    export_postgres_reference_data()
    consume_kafka_events()
