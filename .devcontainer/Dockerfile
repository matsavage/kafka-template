FROM python:3.10-slim

WORKDIR /workspace

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt /workspace/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
