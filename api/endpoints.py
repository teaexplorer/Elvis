from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db import crud, stats
from api import api_models as schemas

router = APIRouter()

# Users endpoints
@router.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Achievements endpoints
@router.get("/achievements/", response_model=List[schemas.AchievementResponse])
def get_achievements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_achievements(db, skip=skip, limit=limit)

@router.post("/achievements/", response_model=schemas.AchievementResponse)
def create_achievement(achievement: schemas.AchievementCreate, db: Session = Depends(get_db)):
    return crud.create_achievement(db=db, achievement=achievement)

# Award achievement
@router.post("/achievements/award/", response_model=schemas.UserAchievementResponse)
def award_achievement(award: schemas.UserAchievementBase, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=award.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    achievement = crud.get_achievement(db, achievement_id=award.achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    result = crud.award_achievement(db, user_id=award.user_id, achievement_id=award.achievement_id)
    
    return {
        "id": result.id,
        "user_id": result.user_id,
        "achievement_id": result.achievement_id,
        "awarded_at": result.awarded_at,
        "username": user.username,
        "achievement_name": achievement.name
    }

# User achievements
@router.get("/users/{user_id}/achievements/")
def get_user_achievements(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    achievements = crud.get_user_achievements_with_details(db, user_id, user.language)
    return {
        "user_id": user_id,
        "username": user.username,
        "language": user.language,
        "achievements": achievements
    }

# Statistics endpoints - теперь используют stats модуль
@router.get("/stats/max-achievements/")
def get_user_with_max_achievements(db: Session = Depends(get_db)):
    result = stats.get_user_with_max_achievements(db)
    if not result:
        return {"message": "No achievements found"}
    return result

@router.get("/stats/max-points/")
def get_user_with_max_points(db: Session = Depends(get_db)):
    result = stats.get_user_with_max_points(db)
    if not result:
        return {"message": "No achievements found"}
    return result

@router.get("/stats/max-difference/")
def get_users_with_max_difference(db: Session = Depends(get_db)):
    result = stats.get_users_with_max_difference(db)
    if not result:
        return {"message": "Not enough users with achievements"}
    return result

@router.get("/stats/min-difference/")
def get_users_with_min_difference(db: Session = Depends(get_db)):
    result = stats.get_users_with_min_difference(db)
    if not result:
        return {"message": "Could not calculate minimum difference"}
    return result

@router.get("/stats/seven-day-streak/")
def get_seven_day_streak_users(db: Session = Depends(get_db)):
    return stats.get_seven_day_streak_users(db)