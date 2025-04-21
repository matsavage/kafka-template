# Kafka Python Development Environment

[![Tests](https://github.com/yourusername/kafka/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/kafka/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/yourusername/kafka/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/kafka)
[![Lint](https://github.com/yourusername/kafka/actions/workflows/lint.yml/badge.svg)](https://github.com/yourusername/kafka/actions/workflows/lint.yml)

This repository contains a development environment for working with Apache Kafka using Python, with Protobuf serialization and Schema Registry integration.

## Setup

1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
3. Clone this repository
4. Open the repository in VS Code
5. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Remote-Containers: Reopen in Container"

## Environment

The development environment includes:

- Python 3.10 with Poetry for dependency management
- Kafka broker (using the Confluent Kafka image)
- Zookeeper (required for Kafka)
- Schema Registry with Protobuf support
- Protobuf compiler

## Directory Structure

```
├── .devcontainer/      # Dev container configuration
├── .github/            # GitHub Actions workflows
├── build/              # Directory for compiled protobuf files (gitignored)
├── examples/           # Example scripts
├── kafka_protobuf/     # Python package
├── protos/             # Protobuf schema definitions
├── tests/              # Unit and integration tests
├── Makefile            # Commands for compiling protos and running tests
├── pyproject.toml      # Poetry configuration
└── README.md           # This file
```

## Working with Protobuf

### Compiling Protobuf Schemas

Protobuf schema files (`.proto`) are stored in the `protos/` directory. To compile them:

```bash
make compile-protos
```

This will generate Python modules in the `build/` directory.

### Using the Package

The `kafka_protobuf` package contains utilities for working with Kafka and Protobuf:

- `utils.py`: Utilities for compiling protos and managing paths
- `messages.py`: Helpers for creating and sending Protobuf messages

Example usage:

```python
from kafka_protobuf.messages import get_producer, create_user, send_user

# Get a producer configured for Protobuf
producer = get_producer()

# Create a user message
user = create_user(1, "Alice Smith", "alice@example.com")

# Send the user message
send_user(producer, "users-topic", user)
```

### Example Scripts

The `examples/` directory contains ready-to-use scripts:

- `protobuf_producer.py`: Sends messages using Protobuf serialization
- `protobuf_consumer.py`: Receives and deserializes Protobuf messages

Both examples automatically compile the proto files if needed.

## Running Examples

```bash
# Start a consumer in one terminal
python examples/protobuf_consumer.py

# Start a producer in another terminal
python examples/protobuf_producer.py
```

## Testing

The project includes integration tests that require the Kafka and Schema Registry services to be running. The tests are set up to connect to these services through the Docker Compose network.

To run tests:

```bash
# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run a specific test file
make test-file file=tests/test_protobuf_messaging.py

# Run tests with coverage
python -m pytest --cov=kafka_protobuf tests/
```

The test suite includes:

- Integration tests for sending and receiving Protobuf messages
- Tests for schema registration and management
- Fixtures that automate schema cleanup after tests

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and delivery:

- **Tests**: Runs all tests in the devcontainer environment
- **Coverage**: Generates and reports code coverage
- **Lint**: Enforces code style using Black, Flake8, and isort

## Environment Variables

- `KAFKA_BOOTSTRAP_SERVER`: The Kafka broker address (default: `kafka:9092`)
- `SCHEMA_REGISTRY_URL`: The Schema Registry URL (default: `http://schema-registry:8081`)