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
