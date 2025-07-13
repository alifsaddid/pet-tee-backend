# ---- Stage 1: Build ----
FROM python:3.11-slim as builder

WORKDIR /install

# Install pip-tools if needed, and build dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# ---- Stage 2: Runtime ----
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy your app code
COPY . .

# Expose the port (adjust as needed)
EXPOSE 8000

# Start your app (adjust depending on your framework)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
