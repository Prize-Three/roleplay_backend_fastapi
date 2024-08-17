from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mysql.models import Vocabulary

async def get_vocabularies_by_report_id(db: AsyncSession, report_id: int, development_type: bool):
    result = await db.execute(
        select(Vocabulary).where(
            Vocabulary.result_report_id == report_id,
            Vocabulary.development_type == development_type
        )
    )
    return result.scalars().first()

async def get_vocabulary_by_id(db: AsyncSession, vocabulary_id: int) -> Vocabulary:
    result = await db.execute(select(Vocabulary).where(Vocabulary.id == vocabulary_id))
    return result.scalars().first()

async def create_vocabulary(db: AsyncSession, result_report_id: int, development_type: bool, total_word_count: int, basic_word_count: int, new_word_count: int):
    new_vocabulary = Vocabulary(
        result_report_id=result_report_id,
        development_type=development_type,
        total_word_count=total_word_count,
        basic_word_count=basic_word_count,
        new_word_count=new_word_count
    )
    db.add(new_vocabulary)
    await db.commit()
    await db.refresh(new_vocabulary)
    return new_vocabulary
