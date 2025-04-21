import os
import json
import time
from kafka import KafkaProducer

# Configure the Kafka producer
KAFKA_BOOTSTRAP_SERVER = os.environ.get('KAFKA_BOOTSTRAP_SERVER', 'kafka:9092')
TOPIC_NAME = 'example-topic'

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_message(message_data):
    """Send a message to the Kafka topic."""
    future = producer.send(TOPIC_NAME, value=message_data)
    producer.flush()  # Ensure message is sent
    return future

if __name__ == "__main__":
    # Example: Send 10 messages
    for i in range(10):
        message = {
            'id': i,
            'timestamp': time.time(),
            'message': f'Test message {i}'
        }
        print(f"Sending message: {message}")
        send_message(message)
        time.sleep(1)  # Wait a second between messages
    
    print("Messages sent successfully")
