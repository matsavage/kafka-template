"""Pytest configuration and fixtures."""

import os
import time
import pytest
import requests
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer

from kafka_protobuf.utils import compile_protos

# Ensure proto files are compiled
compile_protos()
import user_pb2


@pytest.fixture(scope="session")
def kafka_bootstrap_server():
    """Return the Kafka bootstrap server address."""
    return os.environ.get("KAFKA_BOOTSTRAP_SERVER", "kafka:9092")


@pytest.fixture(scope="session")
def schema_registry_url():
    """Return the Schema Registry URL."""
    return os.environ.get("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")


@pytest.fixture(scope="session")
def wait_for_kafka(kafka_bootstrap_server):
    """Wait for Kafka to be ready."""
    from kafka_protobuf.utils import wait_for_kafka as wait_func
    
    if not wait_func(kafka_bootstrap_server, timeout=60):
        pytest.fail("Kafka did not become available within timeout")
    
    return True


@pytest.fixture(scope="session")
def wait_for_schema_registry(schema_registry_url):
    """Wait for Schema Registry to be ready."""
    from kafka_protobuf.utils import wait_for_schema_registry as wait_func
    
    if not wait_func(schema_registry_url, timeout=60):
        pytest.fail("Schema Registry did not become available within timeout")
    
    return True


@pytest.fixture(scope="function")
def schema_registry_client(schema_registry_url, wait_for_schema_registry):
    """Create a Schema Registry client."""
    return SchemaRegistryClient({"url": schema_registry_url})


@pytest.fixture(scope="function")
def protobuf_schema(schema_registry_client, kafka_bootstrap_server, wait_for_kafka):
    """Register a Protobuf schema and create a topic for testing."""
    schema_topic = "proto-users-test"
    
    # Create a serializer to register the schema
    serializer = ProtobufSerializer(
        user_pb2.User,
        schema_registry_client,
        {"use.deprecated.format": False}
    )
    
    # The schema gets registered when the serializer is created
    # Now we need to determine the subject name to clean up later
    subject_name = f"{schema_topic}-value"
    
    # Create the topic
    from confluent_kafka.admin import AdminClient, NewTopic
    admin_client = AdminClient({"bootstrap.servers": kafka_bootstrap_server})
    
    # Check if topic exists
    topics = admin_client.list_topics(timeout=10).topics
    if schema_topic not in topics:
        # Create the topic
        topic_list = [NewTopic(schema_topic, num_partitions=1, replication_factor=1)]
        admin_client.create_topics(topic_list)
        
        # Wait for the topic to be created
        for _ in range(10):  # Try up to 10 times
            topics = admin_client.list_topics(timeout=10).topics
            if schema_topic in topics:
                break
            time.sleep(1)
    
    yield schema_topic
    
    # Clean up: delete the schema after the test
    try:
        schema_registry_client.delete_subject(subject_name)
    except Exception as e:
        print(f"Warning: Failed to delete schema {subject_name}: {e}")