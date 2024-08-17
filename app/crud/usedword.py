from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mysql.models import UsedWord

async def get_used_words_by_report_id(db: AsyncSession, report_id: int, development_type: bool):
    result = await db.execute(
        select(UsedWord).where(
            UsedWord.result_report_id == report_id,
            UsedWord.development_type == development_type
        )
    )
    return result.scalars().all()

async def get_used_word_by_id(db: AsyncSession, used_word_id: int) -> UsedWord:
    result = await db.execute(select(UsedWord).where(UsedWord.id == used_word_id))
    return result.scalars().first()

async def create_used_word(
    db: AsyncSession, 
    result_report_id: int, 
    development_type: bool, 
    word: str
) -> UsedWord:
    new_word = UsedWord(
        result_report_id=result_report_id,
        development_type=development_type,
        word=word
    )
    db.add(new_word)
    await db.commit()
    await db.refresh(new_word)
    return new_word