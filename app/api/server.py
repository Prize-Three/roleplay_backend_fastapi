from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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

@router.post("/chat")
async def chat_with_bot(message: Message):
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
        return {"response": response}  # JSON 형태로 응답

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
