# --- Stage 1: Build dependencies ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install build tools and pip
RUN apt-get update && apt-get install -y build-essential gcc

# Copy dependency file and install packages
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/usr/local -r requirements.txt

# --- Stage 2: Runtime container ---
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy installed Python packages from builder
COPY --from=builder /usr/local /usr/local

# Copy your FastAPI app code
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Start FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]