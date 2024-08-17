from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os

load_dotenv()

# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine)

ASYNC_SQLALCHEMY_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# 동기용 의존성
# def get_db(): #이름 아래와 다르게
#     db = SessionLocal()
#     try:
#         # Generator
#         yield db
#     finally:
#         db.close()

# 비동기용 의존성
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session