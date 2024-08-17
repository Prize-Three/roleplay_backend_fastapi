from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mysql.models import Dialog

async def create_dialog(db: AsyncSession, history_id: int, speaker: str, message_content: str):
    db_dialog = Dialog(
        user_id=1,
        history_id=history_id,
        speaker=speaker,
        message=message_content
    )
    db.add(db_dialog)
    await db.commit()
    await db.refresh(db_dialog)
    return db_dialog

async def get_dialogs_by_history_id(db: AsyncSession, history_id: int):
    result = await db.execute(select(Dialog).where(Dialog.history_id == history_id))
    return result.scalars().all()
