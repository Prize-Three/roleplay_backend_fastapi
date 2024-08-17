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
from crud.dialog import *
import os
from dotenv import load_dotenv
from mysql.database import get_db
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

router = APIRouter()

llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
)

# class Message(BaseModel):
#     question: str  # 클라이언트에서 question 필드로 전송될 것으로 기대

# class ChatRequest(BaseModel):
#     history_id: int


class HistoryRequest(BaseModel):
    user_id: int
    voice_id: Optional[int]
    situation: str
    my_role: str
    ai_role: str

#------------------------------------

class MessageData(BaseModel):
    message: dict
    chat_history_id: dict



@router.post("/roleplay")
async def start_roleplay(history_request: HistoryRequest, db: AsyncSession = Depends(get_db)):
    try:
        history = await create_history(
            db,
            user_id=history_request.user_id,
            voice_id=history_request.voice_id,
            situation=history_request.situation,
            start_time=datetime.now().time(),
            my_role=history_request.my_role,
            ai_role=history_request.ai_role
        )
        return {"history_id": history.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/chat")
# async def chat_with_bot(data: MessageData, db: AsyncSession = Depends(get_db)):
#     try:
#         question = data.message.get('question')
#         history_id = data.chat_history_id.get('history_id')

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", "You are an assistant, and your task is to answer only in Korean as if you were a visiting patient. The doctor is asking questions to better understand your symptoms. You answer the doctor's questions with simple and easy expressions."),
#             ("human", question)
#         ])

#         chain = prompt | llm | StrOutputParser()

#         response = chain.invoke({"question": question})
#         print(f"response: {response}")

#         # Dialog 레코드 생성
#         await create_dialog(db, history_id=history_id, speaker="User", message_content=question)
#         print("db1 complete")
#         await create_dialog(db, history_id=history_id, speaker="AI", message_content=response)
        
#         print(f"Send message: {question}")
#         print(f"Processing history_id: {history_id}")

#         return {"response": response}

#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/chat")
async def chat_with_bot(data: MessageData, db: AsyncSession = Depends(get_db)):
    try:
        question = data.message.get('question')
        history_id = data.chat_history_id.get('history_id')

        # History 객체 가져오기
        history = await get_history_by_id(db, history_id)

        if not history:
            raise HTTPException(status_code=404, detail="History not found")

        # 상황에 따라 프롬프트 설정
        if history.situation == "병원놀이":
            prompt_text = ("You are an AI assistant, and your task is to answer only in Korean as if you were a patient visiting a doctor. "
                           "The user is the doctor asking questions to better understand your symptoms. "
                           "Respond to the doctor's questions with simple and easy expressions suitable for children aged 3-7.")
        elif history.situation == "요리놀이":
            prompt_text = ("You are an AI assistant, and your task is to answer only in Korean as if you were a customer at a restaurant. "
                           "The user is the chef asking what you would like to eat. "
                           "Respond to the chef's questions with simple and easy expressions suitable for children aged 3-7.")
        else:
            # 기본 프롬프트 설정 (필요에 따라 수정)
            prompt_text = ("You are an AI assistant, and your task is to answer only in Korean. "
                           "The user is asking questions, and you need to respond accordingly.")

        # 프롬프트와 질문 연결
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_text),
            ("human", question)
        ])

        chain = prompt | llm | StrOutputParser()

        # 질문에 대한 응답 생성
        response = chain.invoke({"question": question})
        print(f"response: {response}")

        # Dialog 레코드 생성
        await create_dialog(db, history_id=history_id, speaker="User", message_content=question)
        print("db1 complete")
        await create_dialog(db, history_id=history_id, speaker="AI", message_content=response)

        print(f"Send message: {question}")
        print(f"Processing history_id: {history_id}")

        return {"response": response}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
