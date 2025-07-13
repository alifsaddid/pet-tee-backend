from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SYNC_DATABASE_URL: str
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    REPLICATE_API_TOKEN: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()