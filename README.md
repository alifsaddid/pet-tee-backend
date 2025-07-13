# Pet-Tee Backend

A FastAPI backend service for generating pet-themed images.

## Features

- JWT-based authentication and authorization (User and Admin roles)
- PostgreSQL database with SQLAlchemy ORM
- Redis and RQ for background task management
- AI-powered image generation
- Docker support for local development and production

## Setup

### Prerequisites

- Python 3.13+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development

1. Clone the repository

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit the .env file with your settings
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Using Docker

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Access the API at http://localhost:8000

3. API documentation is available at http://localhost:8000/docs

## Running Migrations
# Redis Queue Consumer Service

## Overview

The Redis Queue Consumer Service is a robust asynchronous task processing component that complements our FastAPI application. This service continuously listens to a Redis queue for incoming tasks, processes them according to their type, and updates task statuses in the PostgreSQL database.

Key responsibilities:
- Monitoring Redis queues for new tasks
- Processing tasks asynchronously in the background
- Updating task statuses in the database
- Handling errors and maintaining process resilience

## Setup and Local Development

### Prerequisites

- Docker and Docker Compose installed on your system
- Basic understanding of Redis and PostgreSQL

### Running the Application

The entire application stack (FastAPI app, Redis, PostgreSQL, and Consumer service) can be launched with a single command:

```bash
docker-compose up --build
```

This will:
1. Build all necessary Docker images
2. Start the PostgreSQL database
3. Start the Redis server
4. Launch the FastAPI application
5. Start the Redis queue consumer service

The consumer service is built from the `Dockerfile.consumer` configuration with the container name `redis_queue_consumer`.

## Configuration

The consumer service is configured via environment variables, which are set in the `docker-compose.yml` file:

| Environment Variable | Purpose |
|----------------------|----------|
| `DATABASE_URL` | PostgreSQL connection string for the database |
| `REDIS_URL` | Redis connection string for the queue system |
| `SYNC_DATABASE_URL` | Synchronous database connection (when needed) |
| `PYTHONUNBUFFERED` | Ensures Python output is unbuffered for proper logging |

These variables ensure the consumer can connect to the same Redis and PostgreSQL instances used by the FastAPI application.

## Functionality and Usage

### Task Types

Currently, the consumer processes the following task types:

- `process_item_task`: Processes items with associated text and animal type

### Task Flow

1. Tasks are enqueued by the FastAPI application through endpoints in the tasks router
2. The consumer picks up tasks from the `my_queue` Redis queue
3. Each task is processed according to its type
4. The task status is updated in the database (IN_PROGRESS → DONE or ERROR)

### Monitoring Processing

To observe the consumer's operation in real-time:

```bash
docker-compose logs -f consumer_service
```

This command will display continuous logs from the consumer service, showing task processing, errors, and general operational information.

## Technical Details

### Redis Communication

The consumer uses `redis.asyncio` for asynchronous communication with Redis, providing efficient, non-blocking interaction with the queue system.

### Database Interaction

Database operations are performed using SQLAlchemy's async functionality via `AsyncSessionLocal`. This ensures the consumer interacts with the same PostgreSQL database as the FastAPI application but with proper async handling.

### Error Handling

The consumer implements several error handling mechanisms:

- Redis connection issues: Automatic reconnection attempts
- Malformed messages: Logging and skipping
- Processing errors: Exception catching and task status updates
- Graceful shutdown: Proper cleanup on SIGTERM/SIGINT signals

## Troubleshooting

### Common Issues

1. **Consumer not processing tasks**
   - Check if Redis is running: `docker-compose ps redis`
   - Verify Redis connectivity: `docker-compose exec redis redis-cli ping`
   - Ensure tasks are being enqueued correctly

2. **Database connection errors**
   - Verify PostgreSQL is running: `docker-compose ps db`
   - Check database credentials in environment variables
   - Ensure database migrations have been applied

3. **Application not enqueueing tasks**
   - Check FastAPI logs: `docker-compose logs api`
   - Verify Redis connectivity from the API service

### Debugging Steps

1. Check container logs: `docker-compose logs consumer_service`
2. Inspect Redis queue contents: `docker-compose exec redis redis-cli LLEN my_queue`
3. Verify database task statuses directly in PostgreSQL

## Future Enhancements

Potential improvements for the consumer service:

- Implement sophisticated retry mechanisms with exponential backoff
- Add dead-letter queues for failed tasks
- Incorporate health checks for better monitoring
- Add Prometheus metrics for operational insights
- Scale horizontally with multiple consumer instances
- Implement task prioritization

---

For more information about the FastAPI application that enqueues tasks for this consumer, refer to the API documentation available at `/docs` when the application is running.
To create a new migration after model changes:

```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

## Project Structure

```
pet-tee-backend/
├── alembic/                # Database migrations
├── app/
│   ├── core/               # Core application components
│   │   ├── config.py       # Configuration settings
│   │   └── db/             # Database connection
│   ├── internal/           # Internal service logs, temp files
│   ├── models/             # SQLAlchemy models
│   ├── routers/            # API route handlers
│   ├── schemas/            # Pydantic schemas
│   ├── utils/              # Utility functions
│   └── main.py             # Application entry point
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## API Endpoints

- `GET /ping`: Health check endpoint
- `POST /auth/register`: Register a new user
- `POST /auth/token`: Login and get JWT token

## Background Tasks

Background tasks are handled using Redis Queue (RQ).

To start a worker:

```bash
rq worker --url redis://localhost:6379/0 default
```

Or with Docker:

```bash
docker-compose up -d worker
```
