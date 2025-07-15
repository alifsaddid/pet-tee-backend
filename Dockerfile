# ---- Stage 1: Build dependencies ----
FROM python:3.11-slim as builder

WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---- Stage 2: Final runtime image ----
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/app"

# Create app directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /install

# Copy source code
COPY . .

# Expose port for uvicorn
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
