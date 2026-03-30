FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY worldsim/ ./worldsim/
COPY config/ ./config/
COPY run_demo.py .
COPY tests/ ./tests/

# Create experiment dir
RUN mkdir -p experiments/results

EXPOSE 8000

# Run demo on startup, then serve API
CMD ["sh", "-c", "python run_demo.py && uvicorn worldsim.api.main:app --host 0.0.0.0 --port 8000"]
