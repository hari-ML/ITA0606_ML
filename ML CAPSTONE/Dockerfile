# NOTE: Pinned numpy==2.5.5 and scipy==1.18.1 (from the local Python 3.12 environment)
# declare Requires-Python >=3.12 on PyPI. Using python:3.12-slim ensures pip install
# succeeds cleanly on Cloud Build and matches the scikit-learn==1.9.1 pickle ABI.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# Minimal CA certificates required for F-Droid / Google Play HTTPS requests
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source, theme, assets, and model/ directory
COPY . .

EXPOSE 8080

CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false"]
