"""Message utilities for Kafka and Protobuf."""

import os
import time
from uuid import uuid4

from confluent_kafka import SerializingProducer, DeserializingConsumer
from confluent_kafka.serialization import StringSerializer, StringDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer, ProtobufDeserializer

from kafka_protobuf.utils import compile_protos

# Make sure protos are compiled
try:
    import user_pb2
except ImportError:
    compile_protos()
    import user_pb2


def get_schema_registry_client(url=None):
    """Get a Schema Registry client."""
    url = url or os.environ.get('SCHEMA_REGISTRY_URL', 'http://schema-registry:8081')
    return SchemaRegistryClient({'url': url})


def get_producer(bootstrap_servers=None, schema_registry_client=None):
    """Get a serializing producer for protobuf messages."""
    bootstrap_servers = bootstrap_servers or os.environ.get(
        'KAFKA_BOOTSTRAP_SERVER', 'kafka:9092'
    )
    
    # Create Schema Registry client if not provided
    if schema_registry_client is None:
        schema_registry_client = get_schema_registry_client()
    
    # Create Protobuf serializer
    protobuf_serializer = ProtobufSerializer(
        user_pb2.User,
        schema_registry_client,
        {'use.deprecated.format': False}
    )
    
    # Create the producer
    return SerializingProducer({
        'bootstrap.servers': bootstrap_servers,
        'key.serializer': StringSerializer('utf_8'),
        'value.serializer': protobuf_serializer,
    })


def get_consumer(bootstrap_servers=None, group_id=None):
    """Get a deserializing consumer for protobuf messages."""
    bootstrap_servers = bootstrap_servers or os.environ.get(
        'KAFKA_BOOTSTRAP_SERVER', 'kafka:9092'
    )
    
    group_id = group_id or 'protobuf-consumer-group'
    
    # Create Protobuf deserializer
    protobuf_deserializer = ProtobufDeserializer(
        user_pb2.User,
        {'use.deprecated.format': False}
    )
    
    # Create the consumer
    return DeserializingConsumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'key.deserializer': StringDeserializer('utf_8'),
        'value.deserializer': protobuf_deserializer,
    })


def create_user(user_id, name, email):
    """Create a User protobuf message."""
    user = user_pb2.User()
    user.id = user_id
    user.name = name
    user.email = email
    user.created_at = int(time.time())
    return user


def send_user(producer, topic, user, key=None):
    """Send a User message to Kafka."""
    if key is None:
        key = str(uuid4())  # Generate a random key
    
    producer.produce(
        topic=topic,
        key=key,
        value=user,
        on_delivery=delivery_report
    )
    producer.flush()


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")