FROM python:3.10-slim

WORKDIR /app

# System dependencies needed by pyrofork / tgcrypto
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all bot files
COPY . .

# Make run.sh executable
RUN chmod +x run.sh git_sync.sh

EXPOSE 5000

CMD ["bash", "run.sh"]
