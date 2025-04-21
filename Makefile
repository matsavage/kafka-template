# Makefile for Kafka project

.PHONY: compile-protos clean test lint coverage format

# Compile all proto files in the protos directory
compile-protos:
	protoc -I=protos --python_out=build protos/*.proto
	# Create __init__.py to make the build directory a proper package
	touch build/__init__.py

# Clean compiled protos
clean:
	rm -rf build/*.py build/*.pyc build/__pycache__
	rm -rf .coverage coverage.xml htmlcov/ test-reports/

# Run tests
test:
	pytest

# Run tests with verbose output
test-verbose:
	pytest -v

# Run a specific test file
test-file:
	pytest $(file) -v

# Run linting checks
lint:
	black --check kafka_protobuf tests
	flake8 kafka_protobuf tests
	isort --check-only --profile black kafka_protobuf tests

# Run code coverage
coverage:
	pytest --cov=kafka_protobuf tests/ --cov-report=xml --cov-report=term --cov-report=html

# Format code
format:
	black kafka_protobuf tests
	isort --profile black kafka_protobuf tests