from sqlalchemy import *
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from mysql.database import Base
import pytz


# 한국 표준시(KST)로 시간 설정
kst = pytz.timezone('Asia/Seoul')

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(50))
    join_date = Column(DateTime, default=datetime.utcnow)
    play_time = Column(Float)

    voices = relationship("Voice", back_populates="user")
    histories = relationship("History", back_populates="user")

# class Voice(Base):
#     __tablename__ = "voices"
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     voice_name = Column(String(50))

#     user = relationship("User", back_populates="voices")
#     histories = relationship("History", back_populates="voice")

# class History(Base):
#     __tablename__ = "histories"
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     voice_id = Column(Integer, ForeignKey('voices.id'))
#     situation = Column(String(100))
#     duration = Column(DateTime)
#     date = Column(DateTime, default=datetime.utcnow)
#     my_role = Column(String(100))
#     ai_role = Column(String(100))

#     user = relationship("User", back_populates="histories")
#     voice = relationship("Voice", back_populates="histories")
#     tags = relationship("Tag", back_populates="history")
#     dialogs = relationship("Dialog", back_populates="history")
    # result_report = relationship("ResultReport", back_populates="history", uselist=False)
    
class Voice(Base):
    __tablename__ = "voices"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    voice_name = Column(String(50))

    user = relationship("User", back_populates="voices")
    histories = relationship("History", back_populates="voice")  # back_populates를 수정

class History(Base):
    __tablename__ = "histories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    voice_id = Column(Integer, ForeignKey('voices.id'))
    situation = Column(String(100))
    start_time = Column(Time)  # 시작 시간
    end_time = Column(Time)  # 종료 시간
    # date = Column(Date, default=datetime.utcnow)
    date = Column(Date, default=lambda: datetime.now(kst).date())
    my_role = Column(String(100))
    ai_role = Column(String(100))

    user = relationship("User", back_populates="histories")
    voice = relationship("Voice", back_populates="histories")  # Voice와 연결된 back_populates 수정
    tags = relationship("Tag", back_populates="history")
    dialogs = relationship("Dialog", back_populates="history")
    result_report = relationship("ResultReport", back_populates="history", uselist=False)



class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey('histories.id'))
    tag = Column(String(100))

    history = relationship("History", back_populates="tags")

class SenderType(enum.Enum):
    user = "user"
    bot = "bot"

class Dialog(Base):
    __tablename__ = "dialogs"
    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey('histories.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    speaker = Column(String(10))
    message = Column(Text)
    message_time = Column(DateTime, default=datetime.utcnow)

    history = relationship("History", back_populates="dialogs")

# 추가 모델 정의
class ResultReport(Base):
    __tablename__ = "result_reports"
    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey('histories.id'))
    conversation_summary = Column(Text)
    child_questions = Column(Integer)
    child_responses = Column(Integer)
    interaction_summary = Column(Text)
    comprehensive_results = Column(Text)

    history = relationship("History", back_populates="result_report")
    vocabularies = relationship("Vocabulary", back_populates="result_report")
    used_sentences = relationship("UsedSentence", back_populates="result_report")
    used_words = relationship("UsedWord", back_populates="result_report")

class Vocabulary(Base):
    __tablename__ = "vocabularies"
    id = Column(Integer, primary_key=True, index=True)
    result_report_id = Column(Integer, ForeignKey('result_reports.id'))
    development_type = Column(Boolean)
    total_word_count = Column(Integer)
    basic_word_count = Column(Integer)
    new_word_count = Column(Integer)

    result_report = relationship("ResultReport", back_populates="vocabularies")

class UsedSentence(Base):
    __tablename__ = "used_sentences"
    id = Column(Integer, primary_key=True, index=True)
    result_report_id = Column(Integer, ForeignKey('result_reports.id'))
    development_type = Column(Boolean)
    dialog_content = Column(Text)
    comment = Column(Text)

    result_report = relationship("ResultReport", back_populates="used_sentences")

class UsedWord(Base):
    __tablename__ = "used_words"
    id = Column(Integer, primary_key=True, index=True)
    result_report_id = Column(Integer, ForeignKey('result_reports.id'))
    development_type = Column(Boolean)
    word = Column(String(20))

    result_report = relationship("ResultReport", back_populates="used_words")
