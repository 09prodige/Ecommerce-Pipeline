import time
import json
import requests
import os
from kafka import KafkaProducer

API_URL = os.environ.get("API_URL", "http://localhost:8000/events")
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = "user_actions"

def init_producer():
    for _ in range(15):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(2,8,1) # Fix for newer kafka brokers in kafka-python
            )
            print("Successfully connected to Kafka!")
            return producer
        except Exception as e:
            print(f"Waiting for Kafka to be ready... {e}")
            time.sleep(5)
    raise Exception("Failed to connect to Kafka.")

if __name__ == "__main__":
    print("Starting SOKO COMMERCE Kafka Producer...")
    
    # Wait for the API to be ready
    while True:
        try:
            res = requests.get(API_URL.replace("/events", "/health"))
            if res.status_code == 200:
                print("API is ready.")
                break
        except:
            print("Waiting for API to be ready...")
            time.sleep(2)

    producer = init_producer()
    
    while True:
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                events = response.json()
                for event in events:
                    producer.send(TOPIC_NAME, event)
                    print(f"Sent event: {event['action_type']} by user {event['user_id'][:8]}...")
                
                producer.flush()
            else:
                print(f"API Error: {response.status_code}")
        except Exception as e:
            print(f"Error fetching/sending events: {e}")
            
        # Simulate real-time continuous traffic
        time.sleep(1)
