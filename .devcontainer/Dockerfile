FROM python:3.10-slim

WORKDIR /workspace

# Install git, protobuf compiler, and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    protobuf-compiler \
    make \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Copy pyproject.toml
COPY pyproject.toml /workspace/

# Configure poetry to not create a virtual environment inside the container
RUN poetry config virtualenvs.create false

# Install dependencies (with --no-root to avoid error if the package isn't installable yet)
RUN poetry install --no-interaction --no-ansi --no-root
