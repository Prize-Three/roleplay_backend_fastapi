from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
import openai
import json
from datetime import datetime
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
from crud.history import get_history_by_id
from crud.resultreport import get_result_report_by_history_id
from crud.vocabulary import get_vocabularies_by_report_id
from crud.usedword import get_used_words_by_report_id
from crud.usedsentence import get_used_sentences_by_report_id


load_dotenv()

router = APIRouter()

# 기본 역할 설정
messages = [{"role": "system", "content": "You are a kind child psychologist. Your task is to report on a child's developmental levels to their parents."}]

# ChatGPT API 설정하기
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

client = OpenAI(
    api_key = OPENAI_API_KEY,
)

# openai.api_key = OPENAI_API_KEY

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

#--------------------------------------

class Voice(BaseModel):
    voice_name: str

class HistoryResponse(BaseModel):
    type: str
    child_role: str
    ai_role: str
    setting_voice: str
    start_time: str
    end_time: str

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



# messages = []

@router.post("/roleplay/analysis")
async def analyze_role_play(request: RolePlayAnalysisRequest, db: AsyncSession = Depends(get_db)):  # 요청 본문에서 history_id 받음
    try:
        history = await get_history_by_id(db, request.history_id)
        if not history:
            raise HTTPException(status_code=404, detail="History not found")

        history.end_time = datetime.utcnow().time()
        await db.commit()
        await db.refresh(history)

        dialogs = await get_dialogs_by_history_id(db, request.history_id)

        dialog_content = ""
        for dialog in dialogs:
            dialog_content += f"{dialog.speaker}: {dialog.message}\n"

        prompt_intro = """
        You are an expert in child psychology and development analysis. You have been provided with a transcript of a role-play session between a child and an AI. Your task is to analyze the conversation and provide a detailed development report in JSON format. The JSON should include the following sections:

        - role_play: An overview of the role-play, including the type of play, the roles of the child and AI, and the voice used by the AI.
        - conversation_summary: A brief summary of the conversation that took place.
        - language_development_analysis: An analysis of the child's language development, including vocabulary use and sentence structure.
        - emotional_development_analysis: An analysis of the child's emotional development, focusing on vocabulary and sentence structure used to express emotions.
        - interaction_patterns: An analysis of the interaction patterns, including the number of questions asked by the child and the responses made.
        - comprehensive_results: A summary of the overall development observed during the session.

        Below is an example of the desired JSON output:
        """

        example_json = """
        {
        "role_play": {
            "type": "병원놀이",
            "child_role": "환자",
            "ai_role": "의사",
            "setting_voice": "엄마"
        },
        "conversation_summary": "의사와 환자가 대화하는 상황입니다. 민규가 목이 아파서 의사 선생님에게 진료를 요청하고 있습니다. 의사 선생님은 민규의 열을 측정하고 약을 처방했습니다. 민규는 다음 번에 다시 진료받을 것을 기약하며 대화를 마무리 했습니다.",
        "language_development_analysis": {
            "vocabulary_use": {
            "total_word_count": 36,
            "basic_word_count": 17,
            "new_word_count": 5,
            "new_used_words": ["약", "아파요", "열나요", "감사합니다"]
            },
            "sentence_structure": [
            {"dialog_content": "얼굴이 화끈하고 머리가 지끈합니다", "comment": "'화끈하다', '지끈하다'라는 감각적인 어휘를 사용하여 신체적 감각이나 감정을 구체적으로 묘사했습니다."},
            {"dialog_content": "목이 붓고 머리가 아파서 왔어요", "comment": "'목이 붓다', '머리가 아프다'라는 어휘를 사용하여 자신의 상태를 정확하게 묘사하고 있습니다. 단어 조합을 적절히 잘해서 활용하고 있습니다."}
            ]
        },
        "emotional_development_analysis": {
            "vocabulary_use": {
            "total_word_count": 15,
            "basic_word_count": 31,
            "new_word_count": 2,
            "new_used_words": ["감사합니다", "기뻐요", "행복해요"]
            },
            "sentence_structure": [
            {"dialog_content": "하루종일 머리가 아파서 우울했어요", "comment": "'우울하다'라는 감정 표현을 직접적으로 활용하여 자신의 기분을 묘사했습니다."},
            {"dialog_content": "하지만 맛있는 걸 먹어서 기분이 좋아졌어요", "comment": "'기분이 좋아지다'라는 감정 표현을 직접적으로 활용하여 자신의 기분을 묘사했습니다. 맛있는걸 먹고 난 후 긍정적인 감정 변화를 보였습니다."}
            ]
        },
        "interaction_patterns": {
            "child_questions_and_responses_rate": {
            "child_questions": 12,
            "child_responses": 23
            },
            "interaction_summary": "의사가 대부분의 대화를 주도하면서 상황을 이끌어갔고, 환자 자신의 아픈 부분을 자세하게 설명하면서 활발한 상호작용이 이루어졌습니다."
        },
        "comprehensive_results": "민규는 언어 발달 측면에서 매우 우수한 모습을 보이고 있습니다. 다양한 어휘를 활용하여 자신의 상태와 감정을 구체적으로 표현할 수 있으며, 대화의 주도권을 잡고 상호작용을 이끌어가는 능력이 있습니다. 감정 표현 능력도 충분히 발달되어 있으며, 이를 통해 자신의 정서 상태를 명확히 전달할 수 있습니다."
        }
        """

        prompt = f"""
        {prompt_intro}

        {example_json}

        Now, based on the following conversation, provide a similar JSON formatted report:

        대화 내용:
        {dialog_content}
        """

        # OpenAI API 호출
        response = await openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        report_json = response.choices[0].message['content'].strip()

        # JSON 파싱 및 데이터베이스 저장
        report_data = json.loads(report_json)

        # ResultReport에 저장
        new_report = ResultReport(
            history_id=request.history_id,
            conversation_summary=report_data["conversation_summary"],
            child_questions=report_data["interaction_patterns"]["child_questions_and_responses_rate"]["child_questions"],
            child_responses=report_data["interaction_patterns"]["child_questions_and_responses_rate"]["child_responses"],
            interaction_summary=report_data["interaction_patterns"]["interaction_summary"],
            comprehensive_results=report_data["comprehensive_results"]
        )
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)

        # 언어발달 분석 데이터를 Vocabulary 테이블에 저장
        vocabulary_lang = Vocabulary(
            result_report_id=new_report.id,
            development_type=True,  # 언어발달
            total_word_count=report_data["language_development_analysis"]["vocabulary_use"]["total_word_count"],
            basic_word_count=report_data["language_development_analysis"]["vocabulary_use"]["basic_word_count"],
            new_word_count=report_data["language_development_analysis"]["vocabulary_use"]["new_word_count"]
        )
        db.add(vocabulary_lang)

        # 정서발달 분석 데이터를 Vocabulary 테이블에 저장
        vocabulary_emotion = Vocabulary(
            result_report_id=new_report.id,
            development_type=False,  # 정서발달
            total_word_count=report_data["emotional_development_analysis"]["vocabulary_use"]["total_word_count"],
            basic_word_count=report_data["emotional_development_analysis"]["vocabulary_use"]["basic_word_count"],
            new_word_count=report_data["emotional_development_analysis"]["vocabulary_use"]["new_word_count"]
        )
        db.add(vocabulary_emotion)

        # 언어발달 관련 새로운 단어들을 UsedWord 테이블에 저장
        for vocab in report_data["language_development_analysis"]["vocabulary_use"]["new_used_words"]:
            new_used_word_lang = UsedWord(
                result_report_id=new_report.id,
                development_type=True,  # 언어발달
                word=vocab
            )
            db.add(new_used_word_lang)

        # 정서발달 관련 새로운 단어들을 UsedWord 테이블에 저장
        for vocab in report_data["emotional_development_analysis"]["vocabulary_use"]["new_used_words"]:
            new_used_word_emotion = UsedWord(
                result_report_id=new_report.id,
                development_type=False,  # 정서발달
                word=vocab
            )
            db.add(new_used_word_emotion)

        # 언어발달 관련 문장 구조를 UsedSentence 테이블에 저장
        for sentence in report_data["language_development_analysis"]["sentence_structure"]:
            new_sentence_lang = UsedSentence(
                result_report_id=new_report.id,
                development_type=True,  # 언어발달
                dialog_content=sentence["dialog_content"],
                comment=sentence["comment"]
            )
            db.add(new_sentence_lang)

        # 정서발달 관련 문장 구조를 UsedSentence 테이블에 저장
        for sentence in report_data["emotional_development_analysis"]["sentence_structure"]:
            new_sentence_emotion = UsedSentence(
                result_report_id=new_report.id,
                development_type=False,  # 정서발달
                dialog_content=sentence["dialog_content"],
                comment=sentence["comment"]
            )
            db.add(new_sentence_emotion)

        # 최종 커밋
        await db.commit()
        return {"message": "Report saved successfully", "report_id": new_report.id}

    except Exception as e:
        print("예외 발생:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await db.close()




@router.get("/report/{history_id}", response_model=FullReportResponse)
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

    return FullReportResponse(
        history=HistoryResponse(
            type=history.situation,
            child_role=history.my_role,
            ai_role=history.ai_role,
            setting_voice=findvoice.voice_name,
            start_time=history.start_time.strftime("%H:%M:%S") if history.start_time else None,
            end_time=history.end_time.strftime("%H:%M:%S") if history.end_time else None
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




@router.get("/roleplay/chat/analysis", response_model=ResponseModel)
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