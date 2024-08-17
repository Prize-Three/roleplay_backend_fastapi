from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mysql.models import ResultReport

async def get_result_report_by_id(db: AsyncSession, report_id: int) -> ResultReport:
    result = await db.execute(select(ResultReport).where(ResultReport.id == report_id))
    return result.scalars().first()

async def get_result_report_by_history_id(db: AsyncSession, history_id: int) -> ResultReport:
    result = await db.execute(select(ResultReport).where(ResultReport.history_id == history_id))
    return result.scalars().first()


async def create_result_report(
    db: AsyncSession, 
    history_id: int, 
    conversation_summary: str, 
    child_questions: int, 
    child_responses: int, 
    interaction_summary: str, 
    comprehensive_results: str
) -> ResultReport:
    db_report = ResultReport(
        history_id=history_id,
        conversation_summary=conversation_summary,
        child_questions=child_questions,
        child_responses=child_responses,
        interaction_summary=interaction_summary,
        comprehensive_results=comprehensive_results
    )
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report