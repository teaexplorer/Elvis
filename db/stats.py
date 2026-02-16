from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from db import db_models

def get_user_with_max_achievements(db: Session) -> Optional[Dict[str, Any]]:
    """Пользователь с максимальным количеством достижений"""
    result = db.query(
        db_models.User.id,
        db_models.User.username,
        func.count(db_models.UserAchievement.id).label('total')
    ).join(
        db_models.UserAchievement,
        db_models.User.id == db_models.UserAchievement.user_id
    ).group_by(
        db_models.User.id
    ).order_by(
        desc('total')
    ).first()
    
    if not result:
        return None
    
    return {
        "user_id": result.id,
        "username": result.username,
        "total_achievements": result.total
    }

def get_user_with_max_points(db: Session) -> Optional[Dict[str, Any]]:
    """Пользователь с максимальным количеством очков"""
    result = db.query(
        db_models.User.id,
        db_models.User.username,
        func.coalesce(func.sum(db_models.Achievement.points), 0).label('total_points')
    ).outerjoin(
        db_models.UserAchievement,
        db_models.User.id == db_models.UserAchievement.user_id
    ).outerjoin(
        db_models.Achievement,
        db_models.UserAchievement.achievement_id == db_models.Achievement.id
    ).group_by(
        db_models.User.id
    ).order_by(
        desc('total_points')
    ).first()
    
    if not result or result.total_points == 0:
        return None
    
    return {
        "user_id": result.id,
        "username": result.username,
        "total_points": result.total_points
    }

def get_users_with_max_difference(db: Session) -> Optional[Dict[str, Any]]:
    """Пользователи с максимальной разницей очков"""
    users_points = db.query(
        db_models.User.id,
        db_models.User.username,
        func.coalesce(func.sum(db_models.Achievement.points), 0).label('points')
    ).outerjoin(
        db_models.UserAchievement,
        db_models.User.id == db_models.UserAchievement.user_id
    ).outerjoin(
        db_models.Achievement,
        db_models.UserAchievement.achievement_id == db_models.Achievement.id
    ).group_by(
        db_models.User.id
    ).having(
        func.coalesce(func.sum(db_models.Achievement.points), 0) > 0
    ).all()
    
    if len(users_points) < 2:
        return None
    
    min_user = min(users_points, key=lambda x: x.points)
    max_user = max(users_points, key=lambda x: x.points)
    
    return {
        "user1_id": min_user.id,
        "user1_name": min_user.username,
        "user2_id": max_user.id,
        "user2_name": max_user.username,
        "difference": max_user.points - min_user.points
    }

def get_users_with_min_difference(db: Session) -> Optional[Dict[str, Any]]:
    """Пользователи с минимальной разницей очков"""
    users_points = db.query(
        db_models.User.id,
        db_models.User.username,
        func.coalesce(func.sum(db_models.Achievement.points), 0).label('points')
    ).outerjoin(
        db_models.UserAchievement,
        db_models.User.id == db_models.UserAchievement.user_id
    ).outerjoin(
        db_models.Achievement,
        db_models.UserAchievement.achievement_id == db_models.Achievement.id
    ).group_by(
        db_models.User.id
    ).having(
        func.coalesce(func.sum(db_models.Achievement.points), 0) > 0
    ).all()
    
    if len(users_points) < 2:
        return None
    
    users_points.sort(key=lambda x: x.points)
    min_diff = float('inf')
    result_pair = None
    
    for i in range(len(users_points) - 1):
        diff = users_points[i+1].points - users_points[i].points
        if diff < min_diff:
            min_diff = diff
            result_pair = (users_points[i], users_points[i+1])
    
    if result_pair:
        return {
            "user1_id": result_pair[0].id,
            "user1_name": result_pair[0].username,
            "user2_id": result_pair[1].id,
            "user2_name": result_pair[1].username,
            "difference": min_diff
        }
    
    return None

def get_seven_day_streak_users(db: Session) -> List[Dict[str, Any]]:
    """Пользователи с 7-дневным стриком получения достижений"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    result = []
    users = db.query(db_models.User).all()
    
    for user in users:
        dates = db.query(
            func.date(db_models.UserAchievement.awarded_at).label('date')
        ).filter(
            db_models.UserAchievement.user_id == user.id,
            func.date(db_models.UserAchievement.awarded_at) >= start_date,
            func.date(db_models.UserAchievement.awarded_at) <= end_date
        ).distinct().all()
        
        dates_set = {d.date for d in dates}
        expected_dates = {start_date + timedelta(days=i) for i in range(7)}
        
        if expected_dates.issubset(dates_set):
            count = db.query(db_models.UserAchievement).filter(
                db_models.UserAchievement.user_id == user.id,
                func.date(db_models.UserAchievement.awarded_at) >= start_date,
                func.date(db_models.UserAchievement.awarded_at) <= end_date
            ).count()
            
            result.append({
                "user_id": user.id,
                "username": user.username,
                "streak_start": start_date,
                "streak_end": end_date,
                "achievements_count": count
            })
    
    return result