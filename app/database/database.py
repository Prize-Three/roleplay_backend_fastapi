import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# .env 파일 로드
load_dotenv()

# 환경변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# 데이터베이스 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# 세션 로컬 생성
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 베이스 클래스 생성
Base = declarative_base()

# 데이터베이스 세션 종속성
async def get_db():
    async with SessionLocal() as session:
        yield session

# 테이블 생성 함수
async def init_db():
    async with engine.begin() as conn:
        # 모든 테이블 삭제 (선택사항)
        # await conn.run_sync(Base.metadata.drop_all)
        # 모든 테이블 생성
        await conn.run_sync(Base.metadata.create_all)
