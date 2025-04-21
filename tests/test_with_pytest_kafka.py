"""Tests using pytest-kafka for Kafka testing."""

import os
import time
import threading
import queue
import pytest
from confluent_kafka import Producer, Consumer
from google.protobuf.message import Message as ProtobufMessage

from kafka_protobuf.utils import compile_protos

# Ensure proto files are compiled
compile_protos()
import user_pb2


@pytest.fixture(scope="function")
def message_queue():
    """Create a thread-safe queue for storing messages."""
    return queue.Queue()


@pytest.fixture(scope="function")
def kafka_topic(kafka_bootstrap_server):
    """Create a test topic."""
    from confluent_kafka.admin import AdminClient, NewTopic
    
    admin_client = AdminClient({"bootstrap.servers": kafka_bootstrap_server})
    
    # Create a unique topic name for this test
    topic_name = f"proto-users-test-{int(time.time())}"
    
    # Create the topic
    topic_list = [NewTopic(topic_name, num_partitions=1, replication_factor=1)]
    admin_client.create_topics(topic_list)
    
    # Wait for the topic to be created
    for _ in range(10):  # Try up to 10 times
        topics = admin_client.list_topics(timeout=10).topics
        if topic_name in topics:
            break
        time.sleep(1)
    
    yield topic_name
    
    # Cleanup: Delete the topic after the test
    try:
        admin_client.delete_topics([topic_name])
    except Exception as e:
        print(f"Warning: Failed to delete topic {topic_name}: {e}")


@pytest.fixture(scope="function")
def consumer_thread(kafka_topic, message_queue, kafka_bootstrap_server):
    """Create and run a Kafka consumer thread that stores messages in a queue."""
    stop_event = threading.Event()
    
    def consumer_task(topic, msg_queue, stop_event):
        # Create a plain consumer (not using Schema Registry)
        consumer = Consumer({
            "bootstrap.servers": kafka_bootstrap_server,
            "group.id": f"test-consumer-{int(time.time())}", # Unique group ID
            "auto.offset.reset": "earliest"
        })
        
        # Subscribe to the topic
        consumer.subscribe([topic])
        
        # Signal that the consumer is ready
        msg_queue.put("CONSUMER_READY")
        
        # Start consuming
        try:
            while not stop_event.is_set():
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                
                # Deserialize protobuf message
                try:
                    user = user_pb2.User()
                    user.ParseFromString(msg.value())
                    msg_queue.put(user)
                except Exception as e:
                    print(f"Error deserializing message: {e}")
        finally:
            consumer.close()
    
    # Create and start the consumer thread
    topic = kafka_topic
    thread = threading.Thread(
        target=consumer_task, 
        args=(topic, message_queue, stop_event),
        daemon=True
    )
    thread.start()
    
    # Wait for the consumer to be ready
    ready_signal = message_queue.get(timeout=10)
    assert ready_signal == "CONSUMER_READY"
    
    # Wait a moment to ensure the consumer has started
    time.sleep(2)
    
    yield thread
    
    # Signal the thread to stop
    stop_event.set()
    
    # Wait for the thread to finish
    thread.join(timeout=5)


def test_with_pytest_kafka(
    kafka_topic, 
    consumer_thread, 
    message_queue, 
    kafka_bootstrap_server,
    caplog
):
    """Test sending and receiving Protobuf messages using pytest-kafka."""
    # Create a simple producer (not using Schema Registry)
    producer = Producer({
        "bootstrap.servers": kafka_bootstrap_server
    })
    
    # Create a test user
    test_user_id = 42
    test_user_name = "Test User"
    test_user_email = "test@example.com"
    
    # Create a user message
    user = user_pb2.User()
    user.id = test_user_id
    user.name = test_user_name
    user.email = test_user_email
    user.created_at = int(time.time())
    
    # Serialize the user manually
    serialized_data = user.SerializeToString()
    
    # Send the message
    producer.produce(kafka_topic, value=serialized_data)
    producer.flush()
    
    # Wait for the consumer to receive the message
    try:
        received_user = message_queue.get(timeout=10)  # 10 seconds timeout
        # Skip over any string values (like "CONSUMER_READY")
        while isinstance(received_user, str):
            print(f"Received string: {received_user}")
            received_user = message_queue.get(timeout=10)
    except queue.Empty:
        print("Error: Timed out waiting for message")
        print(f"Test log: {caplog.text}")
        raise
    
    # Verify the received user matches what we sent
    assert received_user.id == test_user_id
    assert received_user.name == test_user_name
    assert received_user.email == test_user_email