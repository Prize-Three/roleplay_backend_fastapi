from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import User
from typing import Optional

# User 레코드 생성 함수
async def create_user(db: AsyncSession, name: str, email: str, play_time: Optional[float] = 0):
    db_user = User(
        name=name,
        email=email,
        play_time=play_time
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# 특정 User 레코드 조회 함수
async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()