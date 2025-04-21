import os
import json
from kafka import KafkaConsumer

# Configure the Kafka consumer
KAFKA_BOOTSTRAP_SERVER = os.environ.get('KAFKA_BOOTSTRAP_SERVER', 'kafka:9092')
TOPIC_NAME = 'example-topic'

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='example-consumer-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def consume_messages():
    """Consume messages from the Kafka topic."""
    print(f"Listening for messages on {TOPIC_NAME}...")
    for message in consumer:
        message_data = message.value
        print(f"Received message: {message_data}")

if __name__ == "__main__":
    consume_messages()
