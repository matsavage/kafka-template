# Kafka Python Development Environment

This repository contains a development environment for working with Apache Kafka using Python.

## Setup

1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
3. Clone this repository
4. Open the repository in VS Code
5. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Remote-Containers: Reopen in Container"

## Environment

The development environment includes:

- Python 3.10
- Kafka broker (using the official Confluent Kafka image)
- Zookeeper (required for Kafka)
- Python packages for working with Kafka

## Usage

After the container is built and started, you can interact with Kafka using the `kafka-python` library.

Example code for a producer and consumer can be found in the `examples` directory.

## Environment Variables

- `KAFKA_BOOTSTRAP_SERVER`: The Kafka broker address (default: `kafka:9092`)
