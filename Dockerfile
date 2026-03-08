FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV MODEL_DIR=/app/model_saved_files

# Install curl for downloading model files from GitHub Release
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files (excluding model files - they'll be downloaded)
COPY requirements.txt ./
COPY streamlit_app.py ./
COPY .streamlit ./.streamlit
COPY download_models.sh ./

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download model files from GitHub Release
RUN chmod +x download_models.sh && \
    ./download_models.sh

# Verify model files are present and show their sizes
RUN echo "=== Model Verification ===" && \
    ls -lh /app/model_saved_files/*.h5 && \
    echo "Total size:" && \
    du -sh /app/model_saved_files

EXPOSE 8501

CMD ["sh", "-c", "streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
