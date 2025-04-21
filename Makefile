# Makefile for Kafka project

.PHONY: compile-protos clean test

# Compile all proto files in the protos directory
compile-protos:
	protoc -I=protos --python_out=build protos/*.proto
	# Create __init__.py to make the build directory a proper package
	touch build/__init__.py

# Clean compiled protos
clean:
	rm -rf build/*.py build/*.pyc build/__pycache__

# Run tests
test:
	pytest

# Run tests with verbose output
test-verbose:
	pytest -v

# Run a specific test file
test-file:
	pytest $(file) -v