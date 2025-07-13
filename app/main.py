from fastapi import FastAPI
from app.routers import health, auth

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


# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])