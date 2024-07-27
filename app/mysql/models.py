from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from mysql.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(50))
    join_date = Column(DateTime, default=datetime.utcnow)
    play_time = Column(Float)

    voices = relationship("Voice", back_populates="user")
    histories = relationship("History", back_populates="user")

class Voice(Base):
    __tablename__ = "voices"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    voice_name = Column(String(50))

    user = relationship("User", back_populates="voices")

class History(Base):
    __tablename__ = "histories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    voice_id = Column(Integer, ForeignKey('voices.id'))
    situation = Column(String(100))
    duration = Column(DateTime)
    date = Column(DateTime, default=datetime.utcnow)
    my_role = Column(String(100))
    ai_role = Column(String(100))

    user = relationship("User", back_populates="histories")
    voice = relationship("Voice")
    tags = relationship("Tag", back_populates="history")
    dialogs = relationship("Dialog", back_populates="history")

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
