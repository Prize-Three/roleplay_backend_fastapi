from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mysql.models import History, User, Voice
from datetime import time

# History 레코드 생성 함수
async def create_history(db: AsyncSession, user_id: int, voice_id: int, situation: str, start_time: time, my_role: str, ai_role: str):
    db_history = History(
        user_id=user_id,
        voice_id=voice_id,
        situation=situation,
        start_time=start_time,
        my_role=my_role,
        ai_role=ai_role
    )
    db.add(db_history)
    await db.commit()
    await db.refresh(db_history)
    return db_history

# 특정 사용자의 History 레코드 조회 함수
async def get_histories_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(History).where(History.user_id == user_id))
    return result.scalars().all()

async def get_history_by_voice_id(db: AsyncSession, voice_id: int):
    result = await db.execute(select(History).where(History.voice_id == voice_id))
    return result.scalars().first()

# 특정 History 레코드 조회 함수
async def get_history_by_id(db: AsyncSession, history_id: int):
    result = await db.execute(select(History).where(History.id == history_id))
    history = result.scalars().first()
    return history
