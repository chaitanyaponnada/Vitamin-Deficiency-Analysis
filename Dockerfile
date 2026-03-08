FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV MODEL_DIR=/app/model_saved_files

# Install Git and Git LFS for pulling model files
RUN apt-get update && \
    apt-get install -y --no-install-recommends git git-lfs && \
    git lfs install && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy repo files first (this gets LFS pointer files initially)
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Pull actual LFS files (replaces pointers with real model files)
RUN cd /app && \
    if [ -d .git ]; then \
        echo "Git repo detected, pulling LFS files..." && \
        git lfs pull && \
        echo "LFS pull completed"; \
    else \
        echo "No .git directory, skipping LFS pull"; \
    fi

# Verify model files are present and show their sizes
RUN echo "Model directory contents:" && \
    ls -lh /app/model_saved_files/*.h5 2>/dev/null || echo "Warning: No .h5 files found" && \
    echo "Total model directory size:" && \
    du -sh /app/model_saved_files 2>/dev/null || true

# Optional: Remove .git to reduce image size after LFS pull
RUN rm -rf /app/.git

EXPOSE 8501

CMD ["sh", "-c", "streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
