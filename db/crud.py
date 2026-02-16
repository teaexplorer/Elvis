from sqlalchemy.orm import Session
from db import db_models
from api import api_models as schemas

def get_user(db: Session, user_id: int):
    return db.query(db_models.User).filter(db_models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(db_models.User).filter(db_models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = db_models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_achievements(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_models.Achievement).offset(skip).limit(limit).all()

def get_achievement(db: Session, achievement_id: int):
    return db.query(db_models.Achievement).filter(db_models.Achievement.id == achievement_id).first()

def create_achievement(db: Session, achievement: schemas.AchievementCreate):
    db_achievement = db_models.Achievement(**achievement.model_dump())
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement


def award_achievement(db: Session, user_id: int, achievement_id: int):
   
    existing = db.query(db_models.UserAchievement).filter(
        db_models.UserAchievement.user_id == user_id,
        db_models.UserAchievement.achievement_id == achievement_id
    ).first()
    
    if existing:
        return existing
    
    db_ua = db_models.UserAchievement(user_id=user_id, achievement_id=achievement_id)
    db.add(db_ua)
    db.commit()
    db.refresh(db_ua)
    return db_ua

def get_user_achievements(db: Session, user_id: int):
    return db.query(db_models.UserAchievement).filter(
        db_models.UserAchievement.user_id == user_id
    ).all()

def get_user_achievements_with_details(db: Session, user_id: int, language: str):
    results = db.query(
        db_models.UserAchievement,
        db_models.Achievement
    ).join(
        db_models.Achievement,
        db_models.UserAchievement.achievement_id == db_models.Achievement.id
    ).filter(
        db_models.UserAchievement.user_id == user_id
    ).all()
    
    achievements = []
    for ua, ach in results:
        name = getattr(ach, f"name_{language}") or ach.name
        description = getattr(ach, f"description_{language}") or ach.description
        achievements.append({
            "name": name,
            "description": description,
            "points": ach.points,
            "awarded_at": ua.awarded_at
        })
    
    return achievements