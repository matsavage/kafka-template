#!/usr/bin/env python

import os
import time
import sys
from uuid import uuid4
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer

# Import from our package
from kafka_protobuf.utils import compile_protos

try:
    # Import the generated protobuf module
    import user_pb2
except ImportError:
    print("Compiling protobuf files first...")
    compile_protos()
    # Try importing again after compilation
    import user_pb2

# Configure the Schema Registry client
SCHEMA_REGISTRY_URL = os.environ.get('SCHEMA_REGISTRY_URL', 'http://schema-registry:8081')
KAFKA_BOOTSTRAP_SERVER = os.environ.get('KAFKA_BOOTSTRAP_SERVER', 'kafka:9092')
TOPIC_NAME = 'proto-users'

# Create Schema Registry client
schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})

# Create Protobuf serializer
protobuf_serializer = ProtobufSerializer(
    user_pb2.User,
    schema_registry_client,
    {'use.deprecated.format': False}
)

# Define a delivery callback
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

# Create the producer
producer = SerializingProducer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER,
    'key.serializer': StringSerializer('utf_8'),
    'value.serializer': protobuf_serializer,
})

def create_user(user_id, name, email):
    """Create a User protobuf message."""
    user = user_pb2.User()
    user.id = user_id
    user.name = name
    user.email = email
    user.created_at = int(time.time())
    return user

def send_user(user):
    """Send a User message to Kafka."""
    key = str(uuid4())  # Generate a random key
    producer.produce(
        topic=TOPIC_NAME,
        key=key,
        value=user,
        on_delivery=delivery_report
    )
    producer.flush()

if __name__ == "__main__":
    # Example: Send 5 user messages
    users = [
        create_user(1, "Alice Smith", "alice@example.com"),
        create_user(2, "Bob Johnson", "bob@example.com"),
        create_user(3, "Charlie Brown", "charlie@example.com"),
        create_user(4, "Diana Prince", "diana@example.com"),
        create_user(5, "Ethan Hunt", "ethan@example.com"),
    ]
    
    for user in users:
        print(f"Sending user: {user.name} (ID: {user.id})")
        send_user(user)
        time.sleep(1)  # Wait a second between messages
    
    print("All users sent successfully")