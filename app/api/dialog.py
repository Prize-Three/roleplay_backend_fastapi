from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from mysql.database import get_db
from crud.dialog import get_dialogs_by_history_id
from mysql.models import Dialog
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class DialogResponse(BaseModel):
    speaker: str
    message: str
    message_time: datetime

    class Config:
        orm_mode = True

@router.get("/{history_id}", response_model=List[DialogResponse])
async def get_dialogs(history_id: int, db: AsyncSession = Depends(get_db)):
    try:
        dialogs = await get_dialogs_by_history_id(db, history_id)
        if not dialogs:
            raise HTTPException(status_code=404, detail="No dialogs found for the given history_id.")
        
        return dialogs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dialogs: {e}")
