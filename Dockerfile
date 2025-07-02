# Base Image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama CLI (host must have the model server running)
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project into the container
COPY . .

# Entrypoint that runs all phases in sequence
CMD ["/bin/bash", "-c", "\
    echo '[Phase 1] Extracting Compliance Text...' && \
    python Phase1.py && \
    echo '[Phase 2] Framework Matching...' && \
    python Phase2.py && \
    echo '[Phase 3.1] Converting to Clause Format...' && \
    python Phase3_Convertor.py && \
    echo '[Phase 3.2] Generating Radar Graphs...' && \
    python Phase3_Graph.py && \
    echo '[Phase 4] Final Summary and Fix Suggestions...' && \
    python Phase4.py \
"]
