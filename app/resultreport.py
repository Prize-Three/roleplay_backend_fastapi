from fastapi import FastAPI, APIRouter, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
import json

load_dotenv()

router = APIRouter()

# 기본 역할 설정
messages = [{"role": "system", "content": "역할놀이 스크립트를 보고 사용자의 언어발달, 정서발달을 분석해주세요"}]


# 1. ChatGPT API 설정하기
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
model = "gpt-3.5-turbo"

class RolePlayAnalysisResponse(BaseModel):
    role_play: dict
    conversation_summary: str
    language_development_analysis: dict
    emotional_development_analysis: dict
    interaction_patterns: dict

@router.post("/analyze_role_play/", response_model=RolePlayAnalysisResponse)
async def analyze_role_play(file: UploadFile = File(...)): # 대화 내용이 포함된 순수 텍스트 파일 (.txt)
    global messages
    content = await file.read()
    script = content.decode('utf-8')

    # 대화를 messages 리스트에 추가
    messages.append(
        {
            "role": "system",
            "content": script,
        },
    )

    # OpenAI API 호출
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"다음 대화를 바탕으로 역할놀이 요약 분석을 JSON 형식으로 작성해 주세요:\n\n대화:\n{script}\n\nJSON 형식의 역할놀이 요약 분석:",
        max_tokens=500
    )

    response_json = response.choices[0].text.strip()
    analysis_result = json.loads(response_json)
    
    return RolePlayAnalysisResponse(
        role_play=analysis_result['role_play'],
        conversation_summary=analysis_result['conversation_summary'],
        language_development_analysis=analysis_result['language_development_analysis'],
        emotional_development_analysis=analysis_result['emotional_development_analysis'],
        interaction_patterns=analysis_result['interaction_patterns']
    )

# DB관련 설정들은 아직 추가 안했음