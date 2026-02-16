from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    language: str = "ru"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AchievementBase(BaseModel):
    name: str
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    points: int = Field(gt=0)
    description: str
    description_ru: Optional[str] = None
    description_en: Optional[str] = None

class AchievementCreate(AchievementBase):
    pass

class AchievementResponse(AchievementBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserAchievementBase(BaseModel):
    user_id: int
    achievement_id: int

class UserAchievementResponse(BaseModel):
    id: int
    user_id: int
    achievement_id: int
    awarded_at: datetime
    username: Optional[str] = None
    achievement_name: Optional[str] = None

class UserAchievementDetail(BaseModel):
    name: str
    description: str
    points: int
    awarded_at: datetime

class StatsResponse(BaseModel):
    user_id: int
    username: str
    total: int

class UserDifferenceResponse(BaseModel):
    user1_id: int
    user1_name: str
    user2_id: int
    user2_name: str
    difference: int