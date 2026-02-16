import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from unittest.mock import Mock, patch

from db.database import Base, get_db
from db import db_models
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "language": "ru"
    }

@pytest.fixture
def test_user(db_session, test_user_data):
    user = db_models.User(**test_user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_achievement_data():
    return {
        "name": "Test Achievement",
        "name_ru": "Тестовое достижение",
        "name_en": "Test Achievement",
        "points": 100,
        "description": "Test description",
        "description_ru": "Тестовое описание",
        "description_en": "Test description"
    }

@pytest.fixture
def test_achievement(db_session, test_achievement_data):
    achievement = db_models.Achievement(**test_achievement_data)
    db_session.add(achievement)
    db_session.commit()
    db_session.refresh(achievement)
    return achievement

@pytest.fixture
def test_user_achievement(db_session, test_user, test_achievement):
    ua = db_models.UserAchievement(
        user_id=test_user.id,
        achievement_id=test_achievement.id,
        awarded_at=datetime.now()
    )
    db_session.add(ua)
    db_session.commit()
    db_session.refresh(ua)
    return ua

@pytest.fixture
def mock_crud():
    with patch('db.crud') as mock:
        yield mock

@pytest.fixture
def mock_get_db(mock_db):
    def _mock_get_db():
        return mock_db
    
    with patch('db.database.get_db', side_effect=_mock_get_db):
        yield