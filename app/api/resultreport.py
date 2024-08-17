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
from crud.history import *
from crud.resultreport import *
from crud.vocabulary import *
from crud.usedword import *
from crud.usedsentence import *


load_dotenv()

router = APIRouter()

## 기본 역할 설정
# messages = [{"role": "system", "content": "You are a kind child psychologist. Your task is to report on a child's developmental levels to their parents."}]

# ChatGPT API 설정하기
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# client = OpenAI(
#     api_key = OPENAI_API_KEY,
# )

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



# # messages = []

# @router.post("/roleplay/analysis")
# async def analyze_role_play(request: RolePlayAnalysisRequest, db: AsyncSession = Depends(get_db)):  # 요청 본문에서 history_id 받음
#     try:
#         history = await get_history_by_id(db, request.history_id)
#         if not history:
#             raise HTTPException(status_code=404, detail="History not found")

#         history.end_time = datetime.utcnow().time()
#         await db.commit()
#         await db.refresh(history)

#         dialogs = await get_dialogs_by_history_id(db, request.history_id)

#         dialog_content = ""
#         for dialog in dialogs:
#             dialog_content += f"{dialog.speaker}: {dialog.message}\n"

        # prompt_intro = """
        # You are an expert in child psychology and development analysis. You have been provided with a transcript of a role-play session between a child and an AI. Your task is to analyze the conversation and provide a detailed development report in JSON format. The JSON should include the following sections:

        # - role_play: An overview of the role-play, including the type of play, the roles of the child and AI, and the voice used by the AI.
        # - conversation_summary: A brief summary of the conversation that took place.
        # - language_development_analysis: An analysis of the child's language development, including vocabulary use and sentence structure.
        # - emotional_development_analysis: An analysis of the child's emotional development, focusing on vocabulary and sentence structure used to express emotions.
        # - interaction_patterns: An analysis of the interaction patterns, including the number of questions asked by the child and the responses made.
        # - comprehensive_results: A summary of the overall development observed during the session.

        # Below is an example of the desired JSON output:
        # """

        # example_json = """
        # {
        # "role_play": {
        #     "type": "병원놀이",
        #     "child_role": "환자",
        #     "ai_role": "의사",
        #     "setting_voice": "엄마"
        # },
        # "conversation_summary": "의사와 환자가 대화하는 상황입니다. 민규가 목이 아파서 의사 선생님에게 진료를 요청하고 있습니다. 의사 선생님은 민규의 열을 측정하고 약을 처방했습니다. 민규는 다음 번에 다시 진료받을 것을 기약하며 대화를 마무리 했습니다.",
        # "language_development_analysis": {
        #     "vocabulary_use": {
        #     "total_word_count": 36,
        #     "basic_word_count": 17,
        #     "new_word_count": 5,
        #     "new_used_words": ["약", "아파요", "열나요", "감사합니다"]
        #     },
        #     "sentence_structure": [
        #     {"dialog_content": "얼굴이 화끈하고 머리가 지끈합니다", "comment": "'화끈하다', '지끈하다'라는 감각적인 어휘를 사용하여 신체적 감각이나 감정을 구체적으로 묘사했습니다."},
        #     {"dialog_content": "목이 붓고 머리가 아파서 왔어요", "comment": "'목이 붓다', '머리가 아프다'라는 어휘를 사용하여 자신의 상태를 정확하게 묘사하고 있습니다. 단어 조합을 적절히 잘해서 활용하고 있습니다."}
        #     ]
        # },
        # "emotional_development_analysis": {
        #     "vocabulary_use": {
        #     "total_word_count": 15,
        #     "basic_word_count": 31,
        #     "new_word_count": 2,
        #     "new_used_words": ["감사합니다", "기뻐요", "행복해요"]
        #     },
        #     "sentence_structure": [
        #     {"dialog_content": "하루종일 머리가 아파서 우울했어요", "comment": "'우울하다'라는 감정 표현을 직접적으로 활용하여 자신의 기분을 묘사했습니다."},
        #     {"dialog_content": "하지만 맛있는 걸 먹어서 기분이 좋아졌어요", "comment": "'기분이 좋아지다'라는 감정 표현을 직접적으로 활용하여 자신의 기분을 묘사했습니다. 맛있는걸 먹고 난 후 긍정적인 감정 변화를 보였습니다."}
        #     ]
        # },
        # "interaction_patterns": {
        #     "child_questions_and_responses_rate": {
        #     "child_questions": 12,
        #     "child_responses": 23
        #     },
        #     "interaction_summary": "의사가 대부분의 대화를 주도하면서 상황을 이끌어갔고, 환자 자신의 아픈 부분을 자세하게 설명하면서 활발한 상호작용이 이루어졌습니다."
        # },
        # "comprehensive_results": "민규는 언어 발달 측면에서 매우 우수한 모습을 보이고 있습니다. 다양한 어휘를 활용하여 자신의 상태와 감정을 구체적으로 표현할 수 있으며, 대화의 주도권을 잡고 상호작용을 이끌어가는 능력이 있습니다. 감정 표현 능력도 충분히 발달되어 있으며, 이를 통해 자신의 정서 상태를 명확히 전달할 수 있습니다."
        # }
        # """

        # prompt = f"""
        # {prompt_intro}

        # {example_json}

        # Now, based on the following conversation, provide a similar JSON formatted report:

        # 대화 내용:
        # {dialog_content}
        # """

#         # OpenAI API 호출
#         # response = await openai.ChatCompletion.create(
#         #     model="gpt-3.5-turbo",
#         #     messages=[
#         #         {"role": "system", "content": prompt}
#         #     ],
#         #     max_tokens=500,
#         #     temperature=0.7
#         # )

#         response = client.completions.create(
#             model="gpt-3.5-turbo-instruct",
#             prompt=prompt, 
#             max_tokens=1000,
#             temperature=0.7
#         )

#         report_json = response.choices[0].text.strip()

#         # JSON 파싱 및 데이터베이스 저장
#         report_data = json.loads(report_json)


#         # ResultReport에 저장
#         new_report = ResultReport(
#             history_id=request.history_id,
#             conversation_summary=report_data["conversation_summary"],
#             child_questions=report_data["interaction_patterns"]["child_questions_and_responses_rate"]["child_questions"],
#             child_responses=report_data["interaction_patterns"]["child_questions_and_responses_rate"]["child_responses"],
#             interaction_summary=report_data["interaction_patterns"]["interaction_summary"],
#             comprehensive_results=report_data["comprehensive_results"]
#         )
#         db.add(new_report)
#         await db.commit()
#         await db.refresh(new_report)

#         # 언어발달 분석 데이터를 Vocabulary 테이블에 저장
#         vocabulary_lang = Vocabulary(
#             result_report_id=new_report.id,
#             development_type=True,  # 언어발달
#             total_word_count=report_data["language_development_analysis"]["vocabulary_use"]["total_word_count"],
#             basic_word_count=report_data["language_development_analysis"]["vocabulary_use"]["basic_word_count"],
#             new_word_count=report_data["language_development_analysis"]["vocabulary_use"]["new_word_count"]
#         )
#         db.add(vocabulary_lang)

#         # 정서발달 분석 데이터를 Vocabulary 테이블에 저장
#         vocabulary_emotion = Vocabulary(
#             result_report_id=new_report.id,
#             development_type=False,  # 정서발달
#             total_word_count=report_data["emotional_development_analysis"]["vocabulary_use"]["total_word_count"],
#             basic_word_count=report_data["emotional_development_analysis"]["vocabulary_use"]["basic_word_count"],
#             new_word_count=report_data["emotional_development_analysis"]["vocabulary_use"]["new_word_count"]
#         )
#         db.add(vocabulary_emotion)

#         # 언어발달 관련 새로운 단어들을 UsedWord 테이블에 저장
#         for vocab in report_data["language_development_analysis"]["vocabulary_use"]["new_used_words"]:
#             new_used_word_lang = UsedWord(
#                 result_report_id=new_report.id,
#                 development_type=True,  # 언어발달
#                 word=vocab
#             )
#             db.add(new_used_word_lang)

#         # 정서발달 관련 새로운 단어들을 UsedWord 테이블에 저장
#         for vocab in report_data["emotional_development_analysis"]["vocabulary_use"]["new_used_words"]:
#             new_used_word_emotion = UsedWord(
#                 result_report_id=new_report.id,
#                 development_type=False,  # 정서발달
#                 word=vocab
#             )
#             db.add(new_used_word_emotion)

#         # 언어발달 관련 문장 구조를 UsedSentence 테이블에 저장
#         for sentence in report_data["language_development_analysis"]["sentence_structure"]:
#             new_sentence_lang = UsedSentence(
#                 result_report_id=new_report.id,
#                 development_type=True,  # 언어발달
#                 dialog_content=sentence["dialog_content"],
#                 comment=sentence["comment"]
#             )
#             db.add(new_sentence_lang)

#         # 정서발달 관련 문장 구조를 UsedSentence 테이블에 저장
#         for sentence in report_data["emotional_development_analysis"]["sentence_structure"]:
#             new_sentence_emotion = UsedSentence(
#                 result_report_id=new_report.id,
#                 development_type=False,  # 정서발달
#                 dialog_content=sentence["dialog_content"],
#                 comment=sentence["comment"]
#             )
#             db.add(new_sentence_emotion)

#         # 최종 커밋
#         await db.commit()
#         return {"message": "Report saved successfully", "report_id": new_report.id}

#     except Exception as e:
#         print("예외 발생:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         await db.close()




# # @router.get("/report/{history_id}", response_model=FullReportResponse)
# # async def get_report(history_id: int, db: AsyncSession = Depends(get_db)):
# #     history = await get_history_by_id(db, history_id)
# #     if not history:
# #         raise HTTPException(status_code=404, detail="History not found")
    
# #     findvoice = await get_voice_by_id(db, history.voice_id)
# #     if not findvoice:
# #         raise HTTPException(status_code=404, detail="Voice not found")

# #     report = await get_result_report_by_history_id(db, history_id)
# #     if not report:
# #         raise HTTPException(status_code=404, detail="Result Report not found")

# #     vocabulary_lang = await get_vocabularies_by_report_id(db, report.id, True)  # 언어발달
# #     vocabulary_emotion = await get_vocabularies_by_report_id(db, report.id, False)  # 정서발달

# #     used_words_lang = await get_used_words_by_report_id(db, report.id, True)  # 언어발달 관련 단어들
# #     used_words_emotion = await get_used_words_by_report_id(db, report.id, False)  # 정서발달 관련 단어들

# #     used_sentences_lang = await get_used_sentences_by_report_id(db, report.id, True)  # 언어발달 관련 문장들
# #     used_sentences_emotion = await get_used_sentences_by_report_id(db, report.id, False)  # 정서발달 관련 문장들

# #     return FullReportResponse(
# #         history=HistoryResponse(
# #             type=history.situation,
# #             child_role=history.my_role,
# #             ai_role=history.ai_role,
# #             setting_voice=findvoice.voice_name,
# #             start_time=history.start_time.strftime("%H:%M:%S") if history.start_time else None,
# #             end_time=history.end_time.strftime("%H:%M:%S") if history.end_time else None
# #         ),
# #         report=ReportResponse(
# #             conversation_summary=report.conversation_summary,
# #             child_questions=report.child_questions,
# #             child_responses=report.child_responses,
# #             interaction_summary=report.interaction_summary,
# #             comprehensive_results=report.comprehensive_results
# #         ),
# #         language_development=LanguageDevelopmentResponse(
# #             vocabulary=VocabularyResponse(
# #                 total_word_count=vocabulary_lang.total_word_count,
# #                 basic_word_count=vocabulary_lang.basic_word_count,
# #                 new_word_count=vocabulary_lang.new_word_count,
# #                 new_used_words=[word.word for word in used_words_lang]
# #             ),
# #             sentence_structure=[
# #                 SentenceStructureResponse(
# #                     dialog_content=sentence.dialog_content,
# #                     comment=sentence.comment
# #                 ) for sentence in used_sentences_lang
# #             ]
# #         ),
# #         emotional_development=EmotionalDevelopmentResponse(
# #             vocabulary=VocabularyResponse(
# #                 total_word_count=vocabulary_emotion.total_word_count,
# #                 basic_word_count=vocabulary_emotion.basic_word_count,
# #                 new_word_count=vocabulary_emotion.new_word_count,
# #                 new_used_words=[word.word for word in used_words_emotion]
# #             ),
# #             sentence_structure=[
# #                 SentenceStructureResponse(
# #                     dialog_content=sentence.dialog_content,
# #                     comment=sentence.comment
# #                 ) for sentence in used_sentences_emotion
# #             ]
# #         )
# #     )






# @router.get("/roleplay/chat/analysis", response_model=ResponseModel)
# async def get_chat_analyze(user_id: int, db: AsyncSession = Depends(get_db)):
#     histories = await get_histories_by_user_id(db, user_id)
#     if not histories:
#         raise HTTPException(status_code=404, detail="Histories not found for the given user_id")

#     response_data = []
#     for history in histories:
#         voice = await get_voice_by_id(db, history.voice_id)

#         if history.end_time and history.start_time:
#             duration_timedelta = datetime.combine(datetime.min, history.end_time) - datetime.combine(datetime.min, history.start_time)
#             # Format duration as 'HH:MM:SS'
#             duration_str = str(duration_timedelta)
#         else:
#             duration_str = "Unknown"

#         # Format date as 'YYYY-MM-DD'
#         date_str = history.date.strftime('%Y-%m-%d') if history.date else "Unknown"

#         response_data.append(
#             HistoryGetResponse(
#                 history_id=history.id,
#                 situation=history.situation,
#                 date=date_str,
#                 duration=duration_str,
#                 voice=voice.voice_name if voice else "Unknown"
#             )
#         )

#     return {"history_list": response_data}



# from fastapi import FastAPI, APIRouter, UploadFile, File
# from pydantic import BaseModel
# from datetime import datetime
# from dotenv import load_dotenv
# from fastapi.middleware.cors import CORSMiddleware
# import os
# import openai
# import json
# from openai import OpenAI
# from fastapi import APIRouter, UploadFile, File, HTTPException

# load_dotenv()

# router = APIRouter()

# # 기본 역할 설정
# messages = [{"role": "system", "content": "역할놀이 스크립트를 보고 사용자의 언어발달, 정서발달을 분석해주세요"}]


# # 1. ChatGPT API 설정하기
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

# client = OpenAI(
#     api_key = OPENAI_API_KEY,
# )
# class RolePlayAnalysisResponse(BaseModel):
#     role_play: dict
#     conversation_summary: str
#     language_development_analysis: dict
#     emotional_development_analysis: dict
#     interaction_patterns: dict

# @router.post("/analyze_role_play/", response_model=RolePlayAnalysisResponse)
# async def analyze_role_play(file: UploadFile = File(...)): # 대화 내용이 포함된 순수 텍스트 파일 (.txt)
#     global messages
#     try:
#         content = await file.read()
#         script = content.decode('utf-8')
#         print("파일 내용:", script)

#         # 대화를 messages 리스트에 추가
#         messages.append(
#             {
#                 "role": "user",
#                 "content": script,
#             },
#         )

#         # OpenAI API 호출
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=messages
#         )
#         print("OpenAI 응답:", response)

#         response_content = response.choices[0].message.content
#         analysis_result = json.loads(response_content)
#         print("분석 결과:", analysis_result)

#         return RolePlayAnalysisResponse(
#             role_play=analysis_result['role_play'],
#             conversation_summary=analysis_result['conversation_summary'],
#             language_development_analysis=analysis_result['language_development_analysis'],
#             emotional_development_analysis=analysis_result['emotional_development_analysis'],
#             interaction_patterns=analysis_result['interaction_patterns']
#         )
#     except Exception as e:
#         print("예외 발생:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
import json
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from mysql.database import get_db
from crud.history import get_history_by_id
from crud.dialog import get_dialogs_by_history_id
from datetime import datetime
# from openai import OpenAI
from dotenv import load_dotenv
import os
import openai

load_dotenv()

router = APIRouter()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

client = OpenAI(
    api_key = OPENAI_API_KEY,
)


class RolePlayAnalysisRequest(BaseModel):
    history_id: int

messages = []

@router.post("/analyze_role_play/")
async def analyze_role_play(request: RolePlayAnalysisRequest, db: AsyncSession = Depends(get_db)):  # 텍스트 입력을 받아서 처리
    global messages
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

#DB연결없이 api바로 출력
# @router.post("/analyze_role_play/")
# async def analyze_role_play(request: RolePlayAnalysisRequest, db: AsyncSession = Depends(get_db)):  # 텍스트 입력을 받아서 처리
#     global messages
#     try:
#         history = await get_history_by_id(db, request.history_id)
#         if not history:
#             raise HTTPException(status_code=404, detail="History not found")

#         history.end_time = datetime.utcnow().time()
#         await db.commit()
#         await db.refresh(history)

#         dialogs = await get_dialogs_by_history_id(db, request.history_id)

#         dialog_content = ""
#         for dialog in dialogs:
#             dialog_content += f"{dialog.speaker}: {dialog.message}\n"

#         prompt_intro = """
#         You are an expert in child psychology and development analysis. You have been provided with a transcript of a role-play session between a child and an AI. Your task is to analyze the conversation and provide a detailed development report in JSON format.

#         The JSON must follow the exact structure below, with all fields filled appropriately based on the conversation. Each field must be included in the analysis, and the response must be in **Korean**. Please ensure that **all key values** are present in the JSON structure as described below:

#         1. **role_play**: Include details about the role-play such as:
#         - type: Type of role-play (e.g., 병원놀이)
#         - child_role: Role the child is playing (e.g., 환자)
#         - ai_role: Role the AI is playing (e.g., 의사)
#         - setting_voice: The voice setting of the AI (e.g., 엄마)

#         2. **conversation_summary**: Provide a concise and informative summary of the conversation that took place between the child and AI. Describe the main events that happened.

#         3. **language_development_analysis**: Analyze the child's language development with the following details:
#         - **vocabulary_use**: Provide the following information:
#             - total_word_count: Total number of words the child used.
#             - basic_word_count: Number of basic words the child used.
#             - new_word_count: Number of new words the child used during the conversation.
#             - new_used_words: List of new words the child used.
#         - **sentence_structure**: Provide an analysis of key sentences used by the child and explain how they reflect language development. Include:
#             - dialog_content: The sentence spoken by the child.
#             - comment: Explanation of how the sentence shows language development.

#         4. **emotional_development_analysis**: Analyze the emotional vocabulary and expression used by the child:
#         - **vocabulary_use**: Provide the following:
#             - total_word_count: Total number of words related to emotional expression.
#             - basic_word_count: Number of basic emotional words the child used.
#             - new_word_count: Number of new emotional words the child used.
#             - new_used_words: List of new emotional words the child used.
#         - **sentence_structure**: Provide an analysis of key sentences that reflect the child’s emotional expressions. Include:
#             - dialog_content: The sentence spoken by the child.
#             - comment: Explanation of how the sentence reflects emotional development.

#         5. **interaction_patterns**: Analyze the interaction between the child and the AI:
#         - **child_questions_and_responses_rate**: Provide counts of:
#             - child_questions: The number of questions the child asked.
#             - child_responses: The number of responses the child gave.
#         - **interaction_summary**: Provide a summary of how the interaction proceeded and how the child participated.

#         6. **comprehensive_results**: Provide a comprehensive analysis of the child's overall language and emotional development, summarizing the key observations from the role-play session.

#         Ensure that the output is a valid JSON object with all the required fields populated based on the conversation.
#         """

#         prompt = f"""
#         {prompt_intro}

#         Now, based on the following conversation, provide a JSON formatted report:

#         대화 내용:
#         {dialog_content}
#         """


#         messages.append(
#             {
#                 "role": "system",
#                 "content": prompt,
#             },
#         )

#         # OpenAI API 호출
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=messages
#         )

#         # GPT 모델의 응답을 JSON으로 반환
#         response_content = response.choices[0].message.content
#         report_data = json.loads(response_content)
#         print("분석 결과:", report_data)

#         # GPT 결과를 그대로 반환
#         return {"analysis_result": report_data}

#     except Exception as e:
#         print("예외 발생:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))





# OpenAI API 키 설정
# openai.api_key = "your-api-key"

# router = APIRouter()

# # Function schema 정의
# def get_function_schema():
#     return {
#         "name": "generate_role_play_analysis",
#         "description": "Generates a detailed development report in JSON format based on a role-play conversation.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "role_play": {
#                     "type": "object",
#                     "properties": {
#                         "type": {"type": "string"},
#                         "child_role": {"type": "string"},
#                         "ai_role": {"type": "string"},
#                         "setting_voice": {"type": "string"}
#                     },
#                     "required": ["type", "child_role", "ai_role", "setting_voice"]
#                 },
#                 "conversation_summary": {"type": "string"},
#                 "language_development_analysis": {
#                     "type": "object",
#                     "properties": {
#                         "vocabulary_use": {
#                             "type": "object",
#                             "properties": {
#                                 "total_word_count": {"type": "integer"},
#                                 "basic_word_count": {"type": "integer"},
#                                 "new_word_count": {"type": "integer"},
#                                 "new_used_words": {"type": "array", "items": {"type": "string"}}
#                             },
#                             "required": ["total_word_count", "basic_word_count", "new_word_count", "new_used_words"]
#                         },
#                         "sentence_structure": {
#                             "type": "array",
#                             "items": {
#                                 "type": "object",
#                                 "properties": {
#                                     "dialog_content": {"type": "string"},
#                                     "comment": {"type": "string"}
#                                 },
#                                 "required": ["dialog_content", "comment"]
#                             }
#                         }
#                     },
#                     "required": ["vocabulary_use", "sentence_structure"]
#                 },
#                 "emotional_development_analysis": {
#                     "type": "object",
#                     "properties": {
#                         "vocabulary_use": {
#                             "type": "object",
#                             "properties": {
#                                 "total_word_count": {"type": "integer"},
#                                 "basic_word_count": {"type": "integer"},
#                                 "new_word_count": {"type": "integer"},
#                                 "new_used_words": {"type": "array", "items": {"type": "string"}}
#                             },
#                             "required": ["total_word_count", "basic_word_count", "new_word_count", "new_used_words"]
#                         },
#                         "sentence_structure": {
#                             "type": "array",
#                             "items": {
#                                 "type": "object",
#                                 "properties": {
#                                     "dialog_content": {"type": "string"},
#                                     "comment": {"type": "string"}
#                                 },
#                                 "required": ["dialog_content", "comment"]
#                             }
#                         }
#                     },
#                     "required": ["vocabulary_use", "sentence_structure"]
#                 },
#                 "interaction_patterns": {
#                     "type": "object",
#                     "properties": {
#                         "child_questions_and_responses_rate": {
#                             "type": "object",
#                             "properties": {
#                                 "child_questions": {"type": "integer"},
#                                 "child_responses": {"type": "integer"}
#                             },
#                             "required": ["child_questions", "child_responses"]
#                         },
#                         "interaction_summary": {"type": "string"}
#                     },
#                     "required": ["child_questions_and_responses_rate", "interaction_summary"]
#                 },
#                 "comprehensive_results": {"type": "string"}
#             },
#             "required": ["role_play", "conversation_summary", "language_development_analysis",
#                          "emotional_development_analysis", "interaction_patterns", "comprehensive_results"]
#         }
#     }
# messages=[]

# @router.post("/analyze_role_play/")
# async def analyze_role_play(request: RolePlayAnalysisRequest, db: AsyncSession = Depends(get_db)):
#     global messages
#     try:
#         # Fetching history and dialogs
#         history = await get_history_by_id(db, request.history_id)
#         if not history:
#             raise HTTPException(status_code=404, detail="History not found")

#         history.end_time = datetime.utcnow().time()
#         await db.commit()
#         await db.refresh(history)

#         dialogs = await get_dialogs_by_history_id(db, request.history_id)

#         dialog_content = ""
#         for dialog in dialogs:
#             dialog_content += f"{dialog.speaker}: {dialog.message}\n"

#         # Define the prompt
#         prompt_intro = """
#         You are an expert in child psychology and development analysis. Analyze the following conversation and return a JSON formatted report with all the required fields.
#         The JSON must follow this structure and be in Korean.
#         """

#         prompt = f"""
#         {prompt_intro}

#         대화 내용:
#         {dialog_content}
#         """

#         messages.append({
#             "role": "system",
#             "content": prompt
#         })

#         # OpenAI API with function calling
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo-0613",
#             messages=messages,
#             functions=[get_function_schema()],
#             function_call="auto"  # Automatically call the function
#         )

#         # Extract function output
#         function_response = response.choices[0].message['function_call']['arguments']
#         report_data = json.loads(function_response)

#         # Saving the results in the database
#         new_report = await create_result_report(
#             db=db,
#             history_id=request.history_id,
#             conversation_summary=report_data["conversation_summary"],
#             child_questions=report_data["interaction_patterns"]["child_questions_and_responses_rate"]["child_questions"],
#             child_responses=report_data["interaction_patterns"]["child_questions_and_responses_rate"]["child_responses"],
#             interaction_summary=report_data["interaction_patterns"]["interaction_summary"],
#             comprehensive_results=report_data["comprehensive_results"]
#         )

#         # Save language and emotional development analysis
#         vocabulary_lang = await create_vocabulary(
#             db=db,
#             result_report_id=new_report.id,
#             development_type=True,  # Language development
#             total_word_count=report_data["language_development_analysis"]["vocabulary_use"]["total_word_count"],
#             basic_word_count=report_data["language_development_analysis"]["vocabulary_use"]["basic_word_count"],
#             new_word_count=report_data["language_development_analysis"]["vocabulary_use"]["new_word_count"]
#         )

#         vocabulary_emotion = await create_vocabulary(
#             db=db,
#             result_report_id=new_report.id,
#             development_type=False,  # Emotional development
#             total_word_count=report_data["emotional_development_analysis"]["vocabulary_use"]["total_word_count"],
#             basic_word_count=report_data["emotional_development_analysis"]["vocabulary_use"]["basic_word_count"],
#             new_word_count=report_data["emotional_development_analysis"]["vocabulary_use"]["new_word_count"]
#         )

#         # Save used words and sentences
#         for vocab in report_data["language_development_analysis"]["vocabulary_use"]["new_used_words"]:
#             await create_used_word(db=db, result_report_id=new_report.id, development_type=True, word=vocab)

#         for vocab in report_data["emotional_development_analysis"]["vocabulary_use"]["new_used_words"]:
#             await create_used_word(db=db, result_report_id=new_report.id, development_type=False, word=vocab)

#         for sentence in report_data["language_development_analysis"]["sentence_structure"]:
#             await create_used_sentence(
#                 db=db, result_report_id=new_report.id, development_type=True,
#                 dialog_content=sentence["dialog_content"], comment=sentence["comment"])

#         for sentence in report_data["emotional_development_analysis"]["sentence_structure"]:
#             await create_used_sentence(
#                 db=db, result_report_id=new_report.id, development_type=False,
#                 dialog_content=sentence["dialog_content"], comment=sentence["comment"])

#         # Commit all changes
#         await db.commit()
#         return {"message": "Report saved successfully", "report_id": new_report.id}

#     except Exception as e:
#         print("Exception occurred:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         await db.close()


#DB test-------------------------------------------------------------------
# # JSON 데이터 구조를 위한 Pydantic 모델
# class AnalysisData(BaseModel):
#     role_play: dict
#     conversation_summary: str
#     language_development_analysis: dict
#     emotional_development_analysis: dict
#     interaction_patterns: dict
#     comprehensive_results: str

# # DB 저장 로직 (기존 코드)
# async def save_analysis_to_db(analysis_result: dict, db: AsyncSession):
#     try:
#         # 1. ResultReport 테이블에 저장
#         new_report = await create_result_report(
#             db=db,
#             history_id=1,  # 여기에 실제 history_id를 전달해야 함
#             conversation_summary=analysis_result.get("conversation_summary"),
#             comprehensive_results=analysis_result.get("comprehensive_results"),
#             child_questions=analysis_result.get("interaction_patterns", {}).get("child_questions_and_responses_rate", {}).get("child_questions"),
#             child_responses=analysis_result.get("interaction_patterns", {}).get("child_questions_and_responses_rate", {}).get("child_responses"),
#             interaction_summary=analysis_result.get("interaction_patterns", {}).get("interaction_summary")
#         )
#         await db.commit()
#         print("ResultReport 저장됨")

#         # 2. 언어발달 Vocabulary 데이터 저장
#         vocab_lang = analysis_result.get("language_development_analysis", {}).get("vocabulary_use", {})
#         try:
#             new_vocabulary_lang = await create_vocabulary(
#                 db=db,
#                 result_report_id=new_report.id,
#                 development_type=True,  # 언어발달
#                 total_word_count=vocab_lang.get("total_word_count"),
#                 basic_word_count=vocab_lang.get("basic_word_count"),
#                 new_word_count=vocab_lang.get("new_word_count")
#             )
#             await db.commit()
#             print("언어발달 Vocabulary 저장됨")
#         except Exception as e:
#             print(f"언어발달 Vocabulary 저장 중 예외 발생: {e}")

#         # 3. 정서발달 Vocabulary 데이터 저장
#         vocab_emotion = analysis_result.get("emotional_development_analysis", {}).get("vocabulary_use", {})
#         try:
#             new_vocabulary_emotion = await create_vocabulary(
#                 db=db,
#                 result_report_id=new_report.id,
#                 development_type=False,  # 정서발달
#                 total_word_count=vocab_emotion.get("total_word_count"),
#                 basic_word_count=vocab_emotion.get("basic_word_count"),
#                 new_word_count=vocab_emotion.get("new_word_count")
#             )
#             await db.commit()
#             print("정서발달 Vocabulary 저장됨")
#         except Exception as e:
#             print(f"정서발달 Vocabulary 저장 중 예외 발생: {e}")

#         # 4. 언어발달 UsedWord 데이터 저장
#         for word in vocab_lang.get("new_used_words", []):
#             await create_used_word(
#                 db=db,
#                 result_report_id=new_report.id,
#                 development_type=True,  # 언어발달
#                 word=word
#             )
#         await db.commit()
#         print("언어발달 UsedWord 저장됨")

#         # 5. 정서발달 UsedWord 데이터 저장
#         for word in vocab_emotion.get("new_used_words", []):
#             await create_used_word(
#                 db=db,
#                 result_report_id=new_report.id,
#                 development_type=False,  # 정서발달
#                 word=word
#             )
#         await db.commit()
#         print("정서발달 UsedWord 저장됨")

#         # 6. 언어발달 Sentence 데이터 저장
#         lang_sentence = analysis_result.get("language_development_analysis", {}).get("sentence_structure", {})
#         await create_used_sentence(
#             db=db,
#             result_report_id=new_report.id,
#             development_type=True,  # 언어발달
#             dialog_content=lang_sentence.get("dialog_content"),
#             comment=lang_sentence.get("comment")
#         )
#         await db.commit()
#         print("언어발달 Sentence 저장됨")

#         # 7. 정서발달 Sentence 데이터 저장
#         emotion_sentence = analysis_result.get("emotional_development_analysis", {}).get("sentence_structure", {})
#         await create_used_sentence(
#             db=db,
#             result_report_id=new_report.id,
#             development_type=False,  # 정서발달
#             dialog_content=emotion_sentence.get("dialog_content"),
#             comment=emotion_sentence.get("comment")
#         )
#         await db.commit()
#         print("정서발달 Sentence 저장됨")

#     except Exception as e:
#         print(f"DB 저장 중 예외 발생: {e}")
#         raise e

# # API 엔드포인트 정의
# @router.post("/save_analysis/")
# async def save_analysis_endpoint(analysis_data: AnalysisData, db: AsyncSession = Depends(get_db)):
#     try:
#         # Pydantic 모델에서 dict로 변환하여 save_analysis_to_db에 전달
#         await save_analysis_to_db(analysis_data.dict(), db)
#         return {"message": "Analysis data saved successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error saving analysis data: {str(e)}")