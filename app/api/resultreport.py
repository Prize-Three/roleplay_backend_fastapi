from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
import openai
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from mysql.database import get_db
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from crud.user import *
from crud.history import *
from crud.voice import *
from crud.dialog import *
from mysql.models import *
from typing import List
from crud.history import *
from crud.resultreport import *
from crud.vocabulary import *
from crud.usedword import *
from crud.usedsentence import *


load_dotenv()

router = APIRouter()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

client = OpenAI(
    api_key = OPENAI_API_KEY,
)

messages = []

class RolePlayAnalysisRequest(BaseModel):
    history_id: int

class RolePlayAnalysisResponse(BaseModel):
    role_play: dict
    conversation_summary: str
    language_development_analysis: dict
    emotional_development_analysis: dict
    interaction_patterns: dict

class HistoryGetResponse(BaseModel):
    history_id: int
    situation: str
    date: str
    duration: str
    voice: str

    class Config:
        orm_mode = True

class ResponseModel(BaseModel):
    history_list: list[HistoryGetResponse]

class RolePlayAnalysisRequest(BaseModel):
    history_id: int

# #--------------------------------------

class Voice(BaseModel):
    voice_name: str

class HistoryResponse(BaseModel):
    type: str
    child_role: str
    ai_role: str
    setting_voice: str
    start_time: str
    end_time: str
    duration: str

class VocabularyResponse(BaseModel):
    total_word_count: int
    basic_word_count: int
    new_word_count: int
    new_used_words: List[str]

class SentenceStructureResponse(BaseModel):
    dialog_content: str
    comment: str

class LanguageDevelopmentResponse(BaseModel):
    vocabulary: VocabularyResponse
    sentence_structure: List[SentenceStructureResponse]

class EmotionalDevelopmentResponse(BaseModel):
    vocabulary: VocabularyResponse
    sentence_structure: List[SentenceStructureResponse]

class ReportResponse(BaseModel):
    conversation_summary: str
    child_questions: int
    child_responses: int
    interaction_summary: str
    comprehensive_results: str

class FullReportResponse(BaseModel):
    history: HistoryResponse
    report: ReportResponse
    language_development: LanguageDevelopmentResponse
    emotional_development: EmotionalDevelopmentResponse


def time_to_seconds(t):
    return t.hour * 3600 + t.minute * 60 + t.second

def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}시간 {minutes}분 {seconds}초"
    elif minutes > 0:
        return f"{minutes}분 {seconds}초"
    else:
        return f"{seconds}초"


@router.get("/{history_id}", response_model=FullReportResponse)
async def get_report(history_id: int, db: AsyncSession = Depends(get_db)):
    history = await get_history_by_id(db, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    
    findvoice = await get_voice_by_id(db, history.voice_id)
    if not findvoice:
        raise HTTPException(status_code=404, detail="Voice not found")

    report = await get_result_report_by_history_id(db, history_id)
    if not report:
        raise HTTPException(status_code=404, detail="Result Report not found")

    vocabulary_lang = await get_vocabularies_by_report_id(db, report.id, True)  # 언어발달
    vocabulary_emotion = await get_vocabularies_by_report_id(db, report.id, False)  # 정서발달

    used_words_lang = await get_used_words_by_report_id(db, report.id, True)  # 언어발달 관련 단어들
    used_words_emotion = await get_used_words_by_report_id(db, report.id, False)  # 정서발달 관련 단어들

    used_sentences_lang = await get_used_sentences_by_report_id(db, report.id, True)  # 언어발달 관련 문장들
    used_sentences_emotion = await get_used_sentences_by_report_id(db, report.id, False)  # 정서발달 관련 문장들

    # duration 계산 (datetime.time에서 초 단위로 변환 후 계산)
    if history.start_time and history.end_time:
        start_seconds = time_to_seconds(history.start_time)
        end_seconds = time_to_seconds(history.end_time)
        duration_seconds = end_seconds - start_seconds

        if duration_seconds < 0:
            # 만약 end_time이 start_time보다 작다면, 그날의 시간을 넘어간 것으로 간주하여 24시간을 추가
            duration_seconds += 24 * 3600
        
        formatted_duration = format_duration(duration_seconds)  # 사람이 읽기 쉬운 형식으로 변환
    else:
        formatted_duration = None

    return FullReportResponse(
        history=HistoryResponse(
            type=history.situation,
            child_role=history.my_role,
            ai_role=history.ai_role,
            setting_voice=findvoice.voice_name,
            start_time=history.start_time.strftime("%H:%M:%S") if history.start_time else None,
            end_time=history.end_time.strftime("%H:%M:%S") if history.end_time else None,
            duration=formatted_duration
        ),
        report=ReportResponse(
            conversation_summary=report.conversation_summary,
            child_questions=report.child_questions,
            child_responses=report.child_responses,
            interaction_summary=report.interaction_summary,
            comprehensive_results=report.comprehensive_results
        ),
        language_development=LanguageDevelopmentResponse(
            vocabulary=VocabularyResponse(
                total_word_count=vocabulary_lang.total_word_count,
                basic_word_count=vocabulary_lang.basic_word_count,
                new_word_count=vocabulary_lang.new_word_count,
                new_used_words=[word.word for word in used_words_lang]
            ),
            sentence_structure=[
                SentenceStructureResponse(
                    dialog_content=sentence.dialog_content,
                    comment=sentence.comment
                ) for sentence in used_sentences_lang
            ]
        ),
        emotional_development=EmotionalDevelopmentResponse(
            vocabulary=VocabularyResponse(
                total_word_count=vocabulary_emotion.total_word_count,
                basic_word_count=vocabulary_emotion.basic_word_count,
                new_word_count=vocabulary_emotion.new_word_count,
                new_used_words=[word.word for word in used_words_emotion]
            ),
            sentence_structure=[
                SentenceStructureResponse(
                    dialog_content=sentence.dialog_content,
                    comment=sentence.comment
                ) for sentence in used_sentences_emotion
            ]
        )
    )



@router.get("/result/analysis", response_model=ResponseModel)
async def get_chat_analyze(user_id: int, db: AsyncSession = Depends(get_db)):
    histories = await get_histories_by_user_id(db, user_id)
    if not histories:
        raise HTTPException(status_code=404, detail="Histories not found for the given user_id")

    response_data = []
    for history in histories:
        voice = await get_voice_by_id(db, history.voice_id)

        if history.end_time and history.start_time:
            duration_timedelta = datetime.combine(datetime.min, history.end_time) - datetime.combine(datetime.min, history.start_time)
            # Format duration as 'HH:MM:SS'
            duration_str = str(duration_timedelta)
        else:
            duration_str = "Unknown"

        # Format date as 'YYYY-MM-DD'
        date_str = history.date.strftime('%Y-%m-%d') if history.date else "Unknown"

        response_data.append(
            HistoryGetResponse(
                history_id=history.id,
                situation=history.situation,
                date=date_str,
                duration=duration_str,
                voice=voice.voice_name if voice else "Unknown"
            )
        )

    return {"history_list": response_data}


@router.post("/chat/result")
async def analyze_role_play(request: RolePlayAnalysisRequest, db: AsyncSession = Depends(get_db)):  # 텍스트 입력을 받아서 처리
    global messages
    try:
        history = await get_history_by_id(db, request.history_id)
        if not history:
            raise HTTPException(status_code=404, detail="History not found")

        history.end_time = datetime.now().time(),
        await db.commit()
        await db.refresh(history)

        dialogs = await get_dialogs_by_history_id(db, request.history_id)

        dialog_content = ""
        for dialog in dialogs:
            dialog_content += f"{dialog.speaker}: {dialog.message}\n"

        prompt_intro = """
        You are an expert in child psychology and development analysis. You have been provided with a transcript of a role-play session between a child and an AI. Your task is to analyze the conversation and provide a detailed development report in JSON format.

        The JSON must follow the exact structure below, with all fields filled appropriately based on the conversation. Each field must be included in the analysis, and the response must be in **Korean**. Please ensure that **all key values** are present in the JSON structure as described below:

        1. **role_play**: Include details about the role-play such as:
        - type: Type of role-play (e.g., 병원놀이)
        - child_role: Role the child is playing (e.g., 환자)
        - ai_role: Role the AI is playing (e.g., 의사)
        - setting_voice: The voice setting of the AI (e.g., 엄마)

        2. **conversation_summary**: Provide a concise and informative summary of the conversation that took place between the child and AI. Describe the main events that happened.

        3. **language_development_analysis**: Analyze the child's language development with the following details:
        - **vocabulary_use**: Provide the following information:
            - total_word_count: Total number of words the child used.
            - basic_word_count: Number of basic words the child used.
            - new_word_count: Number of new words the child used during the conversation.
            - new_used_words: List of new words the child used.
        - **sentence_structure**: Provide an analysis of key sentences used by the child. Each sentence analysis should be in the following format and should be part of a list:
            - dialog_content: The sentence spoken by the child.
            - comment: Explanation of how the sentence shows language development.

        4. **emotional_development_analysis**: Analyze the emotional vocabulary and expression used by the child:
        - **vocabulary_use**: Provide the following:
            - total_word_count: Total number of words related to emotional expression.
            - basic_word_count: Number of basic emotional words the child used.
            - new_word_count: Number of new emotional words the child used.
            - new_used_words: List of new emotional words the child used.
        - **sentence_structure**: Provide an analysis of key emotional sentences spoken by the child. Each sentence analysis should be part of a list and follow the format:
            - dialog_content: The sentence spoken by the child.
            - comment: Explanation of how the sentence reflects emotional development.

        5. **interaction_patterns**: Analyze the interaction between the child and the AI:
        - **child_questions_and_responses_rate**: Provide counts of:
            - child_questions: The number of questions the child asked.
            - child_responses: The number of responses the child gave.
        - **interaction_summary**: Provide a summary of how the interaction proceeded and how the child participated.

        6. **comprehensive_results**: Provide a comprehensive analysis of the child's overall language and emotional development, summarizing the key observations from the role-play session.

        Ensure that the output is a valid JSON object with all the required fields populated based on the conversation.

        """

        prompt = f"""
        {prompt_intro}

        Now, based on the following conversation, provide a JSON formatted report:

        대화 내용:
        {dialog_content}
        """


        messages.append(
            {
                "role": "system",
                "content": prompt,
            },
        )

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        # print("OpenAI 응답:", response)

        response_content = response.choices[0].message.content
        report_data = json.loads(response_content)
        print("분석 결과:", report_data)

        # ResultReport에 저장
        new_report = await create_result_report(
            db=db,
            history_id=request.history_id,
            conversation_summary=report_data.get("conversation_summary", None),
            child_questions=report_data.get("interaction_patterns", {}).get("child_questions_and_responses_rate", {}).get("child_questions", None),
            child_responses=report_data.get("interaction_patterns", {}).get("child_questions_and_responses_rate", {}).get("child_responses", None),
            interaction_summary=report_data.get("interaction_patterns", {}).get("interaction_summary", None),
            comprehensive_results=report_data.get("comprehensive_results", None)
        )
        print("ResultReport 저장됨")

        # 언어발달 분석 데이터를 Vocabulary 테이블에 저장
        vocabulary_lang = await create_vocabulary(
            db=db,
            result_report_id=new_report.id,
            development_type=True,  # 언어발달
            total_word_count=report_data.get("language_development_analysis", {}).get("vocabulary_use", {}).get("total_word_count", None),
            basic_word_count=report_data.get("language_development_analysis", {}).get("vocabulary_use", {}).get("basic_word_count", None),
            new_word_count=report_data.get("language_development_analysis", {}).get("vocabulary_use", {}).get("new_word_count", None)
        )
        print("Vocabulary 언어발달 저장됨")

        # 정서발달 분석 데이터를 Vocabulary 테이블에 저장
        vocabulary_emotion = await create_vocabulary(
            db=db,
            result_report_id=new_report.id,
            development_type=False,  # 정서발달
            total_word_count=report_data.get("emotional_development_analysis", {}).get("vocabulary_use", {}).get("total_word_count", None),
            basic_word_count=report_data.get("emotional_development_analysis", {}).get("vocabulary_use", {}).get("basic_word_count", None),
            new_word_count=report_data.get("emotional_development_analysis", {}).get("vocabulary_use", {}).get("new_word_count", None)
        )
        print("Vocabulary 정서발달 저장됨")

        # 언어발달 관련 새로운 단어들을 UsedWord 테이블에 저장
        for vocab in report_data.get("language_development_analysis", {}).get("vocabulary_use", {}).get("new_used_words", []):
            new_word = await create_used_word(
                db=db,
                result_report_id=new_report.id,
                development_type=True,  # 언어발달
                word=vocab
            )
        print("UsedWord 언어발달 저장됨")

        # 정서발달 관련 새로운 단어들을 UsedWord 테이블에 저장
        for vocab in report_data.get("emotional_development_analysis", {}).get("vocabulary_use", {}).get("new_used_words", []):
            new_word = await create_used_word(
                db=db,
                result_report_id=new_report.id,
                development_type=False,  # 정서발달
                word=vocab
            )
        print("UsedWord 정서발달 저장됨")

        # 언어발달 관련 문장 구조를 UsedSentence 테이블에 저장
        for sentence in report_data.get("language_development_analysis", {}).get("sentence_structure", []):
            new_sentence = await create_used_sentence(
                db=db,
                result_report_id=new_report.id,
                development_type=True,  # 언어발달
                dialog_content=sentence.get("dialog_content", None),
                comment=sentence.get("comment", None)
            )
        print("UsedSentence 언어발달 저장됨")

        # 정서발달 관련 문장 구조를 UsedSentence 테이블에 저장
        for sentence in report_data.get("emotional_development_analysis", {}).get("sentence_structure", []):
            new_sentence = await create_used_sentence(
                db=db,
                result_report_id=new_report.id,
                development_type=False,  # 정서발달
                dialog_content=sentence.get("dialog_content", None),
                comment=sentence.get("comment", None)
            )
        print("UsedSentence 정서발달 저장됨")

        # 최종 커밋
        await db.commit()
        return {"message": "Report saved successfully", "report_id": new_report.id}


    except Exception as e:
        print("예외 발생:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await db.close()
