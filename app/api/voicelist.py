from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from mysql.database import get_db
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from crud.user import *
from crud.history import *
from crud.voice import *

load_dotenv()

router = APIRouter()

class VoiceResponse(BaseModel):
    voice_id: int
    voice_name: str

    class Config:
        orm_mode = True

class ResponseModel(BaseModel):
    voice_list: list[VoiceResponse]

@router.get("/roleplay/chat/voice-management", response_model=ResponseModel)
async def get_chat_analyze(user_id: int, db: AsyncSession = Depends(get_db)):
    voices = await get_voices_by_user_id(db, user_id)
    if not voices:
        raise HTTPException(status_code=404, detail="Voices not found for the given user_id")

    response_data = []
    for voice in voices:
        response_data.append(
            VoiceResponse(
                voice_id=voice.id,
                voice_name=voice.voice_name
            )
        )
    
    return {"voice_list": response_data}