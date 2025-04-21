#!/usr/bin/env python

import os
import sys
from confluent_kafka import DeserializingConsumer
from confluent_kafka.serialization import StringDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer

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

# Create Protobuf deserializer
protobuf_deserializer = ProtobufDeserializer(
    user_pb2.User,
    {'use.deprecated.format': False}
)

# Create the consumer
consumer = DeserializingConsumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER,
    'group.id': 'protobuf-consumer-group',
    'auto.offset.reset': 'earliest',
    'key.deserializer': StringDeserializer('utf_8'),
    'value.deserializer': protobuf_deserializer,
})

def consume_users():
    """Consume User messages from Kafka."""
    # Subscribe to the topic
    consumer.subscribe([TOPIC_NAME])
    
    print(f"Listening for messages on {TOPIC_NAME}...")
    
    try:
        while True:
            # Poll for messages
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
                
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
                
            # Process the User message
            user = msg.value()
            print(f"Received user: ID={user.id}, Name={user.name}, Email={user.email}, Created={user.created_at}")
                
    except KeyboardInterrupt:
        # Close the consumer on Ctrl+C
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_users()