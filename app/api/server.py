from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from crud.history import *
from crud.chat_history import *
from main import get_db


router = APIRouter()

llm = ChatOpenAI(
    base_url="http://localhost:5000/v1",  # LM Studio의 URL
    api_key="lm-studio",
    model="sangthree/0707_gguf",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
)

class Message(BaseModel):
    question: str  # 클라이언트에서 question 필드로 전송될 것으로 기대

class ChatRequest(BaseModel):
    history_id: int


class HistoryRequest(BaseModel):
    user_id: int
    voice_id: Optional[int]
    situation: str
    start_time: datetime
    my_role: str
    ai_role: str

@router.post("/roleplay")
async def start_roleplay(history_request: HistoryRequest, db: AsyncSession = Depends(get_db)):
    try:
        history = await create_history(
            db,
            user_id=history_request.user_id,
            voice_id=history_request.voice_id,
            situation=history_request.situation,
            duration=history_request.start_time,
            my_role=history_request.my_role,
            ai_role=history_request.ai_role
        )
        return {"history_id": history.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_with_bot(message: Message, chat_history_id: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        prompt = PromptTemplate.from_template(
            """You are a helpful, smart, kind, and efficient AI assistant. You always fulfill the user's requests to the best of your ability.
            You must generate an answer in Korean.

            #Question:
            {question}

            #Answer: """
        )

        chain = prompt | llm | StrOutputParser()

        response = chain.invoke({"question": message.question})  # 클라이언트로부터 받은 질문 사용

        # Dialog 레코드 생성
        await create_dialog(db, history_id=chat_history_id, speaker="User", message=message.question)
        await create_dialog(db, history_id=chat_history_id, speaker="AI", message=response)

        return {"response": response}  # JSON 형태로 응답

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
