from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from app.routers import health, auth, tasks
from app.core.redis import get_redis
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI(
    title="Pet-Tee API",
    description="Backend for Pet-Tee image generation service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide schemas section by default
        "deepLinking": True,  # Allow direct links to operations
        "displayRequestDuration": True,  # Show request duration
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    # Initialize Redis connection on startup
    redis_client = await get_redis()
    app.state.redis = redis_client


@app.on_event("shutdown")
async def shutdown_db_client():
    # Close Redis connection on shutdown
    if hasattr(app.state, "redis"):
        await app.state.redis.close()


app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])