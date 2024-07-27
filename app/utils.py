# # app/utils.py
# from mysql.database import SessionLocal

# # 종속성 만들기 : 요청 당 독립적인 데이터베이스 세션/연결이 필요하고 요청이 완료되면 닫음
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from sqlalchemy.ext.asyncio import AsyncSession
from mysql.database import SessionLocal

async def get_db() -> AsyncSession:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


