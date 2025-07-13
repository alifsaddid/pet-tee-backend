from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker
from sqlalchemy.orm import sessionmaker as sync_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

Base = declarative_base()

sync_engine = create_engine(settings.SYNC_DATABASE_URL)
SyncSessionLocal = sync_sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async_engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
