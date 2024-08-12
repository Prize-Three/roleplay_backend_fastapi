from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mysql.models import ResultReport

async def get_result_report_by_id(db: AsyncSession, report_id: int) -> ResultReport:
    result = await db.execute(select(ResultReport).where(ResultReport.id == report_id))
    return result.scalars().first()

async def get_result_report_by_history_id(db: AsyncSession, history_id: int) -> ResultReport:
    result = await db.execute(select(ResultReport).where(ResultReport.history_id == history_id))
    return result.scalars().first()