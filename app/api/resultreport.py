from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
import json

load_dotenv()

router = APIRouter()

# 기본 역할 설정
messages = [{"role": "system", "content": "역할놀이 스크립트를 보고 사용자의 언어발달, 정서발달을 분석해주세요"}]

# ChatGPT API 설정하기
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

client = OpenAI(
    api_key = OPENAI_API_KEY,
)

class RolePlayAnalysisResponse(BaseModel):
    role_play: dict
    conversation_summary: str
    language_development_analysis: dict
    emotional_development_analysis: dict
    interaction_patterns: dict

@router.post("/analyze_role_play/", response_model=RolePlayAnalysisResponse)
async def analyze_role_play(file: UploadFile = File(...)): # 대화 내용이 포함된 순수 텍스트 파일 (.txt)
    global messages
    try:
        content = await file.read()
        script = content.decode('utf-8')
        print("파일 내용:", script)

        # 대화를 messages 리스트에 추가
        messages.append(
            {
                "role": "user",
                "content": script,
            },
        )

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        print("OpenAI 응답:", response)

        response_content = response.choices[0].message.content
        analysis_result = json.loads(response_content)
        print("분석 결과:", analysis_result)
        
        return RolePlayAnalysisResponse(
            role_play=analysis_result['role_play'],
            conversation_summary=analysis_result['conversation_summary'],
            language_development_analysis=analysis_result['language_development_analysis'],
            emotional_development_analysis=analysis_result['emotional_development_analysis'],
            interaction_patterns=analysis_result['interaction_patterns']
        )
    except Exception as e:
        print("예외 발생:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

