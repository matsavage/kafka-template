"""Tests for Protobuf message serialization and Kafka integration."""

import time
import threading
import queue
import pytest
from confluent_kafka import Producer, Consumer

from kafka_protobuf.messages import (
    get_producer, 
    get_consumer, 
    create_user, 
    send_user
)


@pytest.fixture(scope="function")
def message_queue():
    """Create a thread-safe queue for storing messages."""
    return queue.Queue()


@pytest.fixture(scope="function")
def consumer_thread(protobuf_schema, message_queue, kafka_bootstrap_server, wait_for_kafka):
    """Create and run a Kafka consumer thread that stores messages in a queue."""
    stop_event = threading.Event()
    
    def consumer_task(topic, msg_queue, stop_event):
        # Create a consumer
        consumer = get_consumer(
            bootstrap_servers=kafka_bootstrap_server,
            group_id=f"test-consumer-{int(time.time())}"  # Unique group ID for each test
        )
        
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
                
                # Put the received message in the queue
                user = msg.value()
                msg_queue.put(user)
        finally:
            consumer.close()
    
    # Create and start the consumer thread
    topic = protobuf_schema
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


def test_protobuf_send_receive(
    protobuf_schema, 
    schema_registry_client, 
    consumer_thread, 
    message_queue, 
    kafka_bootstrap_server, 
    wait_for_kafka,
    caplog
):
    """Test sending and receiving Protobuf messages through Kafka."""
    # Get the topic name from the fixture
    topic = protobuf_schema
    
    # Create a producer
    producer = get_producer(
        bootstrap_servers=kafka_bootstrap_server,
        schema_registry_client=schema_registry_client
    )
    
    # Create a test user
    test_user_id = 42
    test_user_name = "Test User"
    test_user_email = "test@example.com"
    
    user = create_user(test_user_id, test_user_name, test_user_email)
    
    # Send the user message
    send_user(producer, topic, user)
    
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