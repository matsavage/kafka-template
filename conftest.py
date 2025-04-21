"""Root conftest.py for global pytest configuration."""

import os
import pytest
import tempfile
import subprocess


@pytest.fixture(scope="session")
def kafka_bootstrap_server():
    """
    Provide the Kafka bootstrap server.
    
    This allows tests to use either:
    1. The running Kafka in the container (default)
    2. A Kafka instance launched by pytest-kafka
    3. A Kafka instance launched by testcontainers
    """
    # By default, use the docker-compose Kafka
    return os.environ.get("KAFKA_BOOTSTRAP_SERVER", "kafka:9092")


@pytest.fixture(scope="session")
def schema_registry_url():
    """Provide the Schema Registry URL."""
    return os.environ.get("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")