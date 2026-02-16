from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    language = Column(String(2), default="ru")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    achievements = relationship("UserAchievement", back_populates="user")

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    name_ru = Column(String(200))
    name_en = Column(String(200))
    points = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    description_ru = Column(Text)
    description_en = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    users = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    awarded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")