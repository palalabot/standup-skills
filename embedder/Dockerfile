FROM python:3.11-slim

WORKDIR /app
ENV MODEL_NAME=all-MiniLM-L6-v2 \
    HF_HOME=/app/hf \
    PYTHONUNBUFFERED=1

# CPU-only torch keeps the image small; MiniLM doesn't need a GPU
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir runpod sentence-transformers

# bake the model in at build time so cold starts don't download it
RUN python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['MODEL_NAME'])"
ENV HF_HUB_OFFLINE=1

COPY handler.py .
CMD ["python", "handler.py"]
