from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Voice
from typing import Optional

# Voice 레코드 생성 함수
async def create_voice(db: AsyncSession, user_id: int, voice_name: str):
    db_voice = Voice(
        user_id=user_id,
        voice_name=voice_name
    )
    db.add(db_voice)
    await db.commit()
    await db.refresh(db_voice)
    return db_voice

# 특정 Voice 레코드 조회 함수
async def get_voice_by_id(db: AsyncSession, voice_id: int):
    result = await db.execute(select(Voice).where(Voice.id == voice_id))
    return result.scalars().first()

# 특정 사용자의 모든 Voice 레코드 조회 함수
async def get_voices_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Voice).where(Voice.user_id == user_id))
    return result.scalars().all()