from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mysql.models import UsedSentence

async def get_used_sentences_by_report_id(db: AsyncSession, report_id: int, development_type: bool):
    result = await db.execute(
        select(UsedSentence).where(
            UsedSentence.result_report_id == report_id,
            UsedSentence.development_type == development_type
        )
    )
    return result.scalars().all()

async def get_used_sentence_by_id(db: AsyncSession, used_sentence_id: int) -> UsedSentence:
    result = await db.execute(select(UsedSentence).where(UsedSentence.id == used_sentence_id))
    return result.scalars().first()

async def create_used_sentence(
    db: AsyncSession, 
    result_report_id: int, 
    development_type: bool, 
    dialog_content: str, 
    comment: str
) -> UsedSentence:
    new_sentence = UsedSentence(
        result_report_id=result_report_id,
        development_type=development_type,
        dialog_content=dialog_content,
        comment=comment
    )
    db.add(new_sentence)
    await db.commit()
    await db.refresh(new_sentence)
    return new_sentence