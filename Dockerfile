# ============================================================
# Stage 1: Build the React Frontend
# ============================================================
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Install frontend dependencies
COPY frontend/package*.json ./
RUN npm ci || npm install

# Copy frontend source code and compile production bundle
COPY frontend/ ./
RUN npm run build

# ============================================================
# Stage 2: Python FastAPI Backend + AI Agent + Vector DB
# ============================================================
FROM python:3.10-slim

# Create a non-root user (UID 1000) for security
RUN useradd -m -u 1000 user

# Configure environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/home/user/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/home/user/.cache/sentence_transformers

WORKDIR /app

# Install system dependencies (build tools for packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements (CPU-only PyTorch first to stay lightweight and save RAM)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy application source code with correct ownership
COPY --chown=user:user export-agent/ /app/export-agent/
COPY --chown=user:user frontend/backend/ /app/frontend/backend/

# Copy the built React frontend from Stage 1
COPY --chown=user:user --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Switch to non-root user for security and compatibility
USER user

# Ensure cache directory exists and is writable
RUN mkdir -p /home/user/.cache/huggingface /home/user/.cache/sentence_transformers

# Pre-download SentenceTransformer embedding model and build ChromaDB index
# This bakes the vector database into the image so the container starts instantly
RUN python /app/export-agent/src/build_index.py

# Expose default port
EXPOSE 7860

# Launch FastAPI server (supports PORT env var from Render, falls back to 7860)
CMD ["sh", "-c", "uvicorn frontend.backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
