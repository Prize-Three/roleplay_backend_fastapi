from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os

load_dotenv()

ASYNC_DB_URL = os.getenv("DATABASE_URL")
# engine = create_engine(DB_URL,echo=True)
# SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
async_session = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session