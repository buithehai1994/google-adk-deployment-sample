FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (uncomment if you need build tools)
# RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y git && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 9999

CMD ["python", "api.py"]