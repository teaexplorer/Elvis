from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytest
from unittest.mock import Mock, patch

from db.database import Base, get_db
from db import db_models, crud
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

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_database):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

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

class TestUserEndpoints:
    def test_create_user_success(self, client, setup_database):
        user_data = {
            "username": "newuser",
            "language": "ru"
        }
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["language"] == user_data["language"]

    def test_create_user_duplicate_username(self, client, test_user):
        user_data = {
            "username": test_user.username,
            "language": "en"
        }
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.text

    def test_get_user_success(self, client, test_user):
        response = client.get(f"/api/users/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username

    def test_get_user_not_found(self, client):
        response = client.get("/api/users/999")
        assert response.status_code == 404

class TestAchievementEndpoints:
    def test_create_achievement_success(self, client, setup_database):
        achievement_data = {
            "name": "New Achievement",
            "name_ru": "Новое достижение",
            "name_en": "New Achievement",
            "points": 50,
            "description": "New description",
            "description_ru": "Новое описание",
            "description_en": "New description"
        }
        response = client.post("/api/achievements/", json=achievement_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == achievement_data["name"]
        assert data["points"] == achievement_data["points"]

    def test_create_achievement_invalid_points(self, client, test_achievement_data):
        invalid_data = test_achievement_data.copy()
        invalid_data["points"] = -100
        response = client.post("/api/achievements/", json=invalid_data)
        assert response.status_code == 422

    def test_get_achievements_list(self, client, test_achievement):
        response = client.get("/api/achievements/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == test_achievement.name

    def test_get_achievements_with_pagination(self, client, test_achievement):
        response = client.get("/api/achievements/?skip=0&limit=10")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestAwardEndpoints:
    def test_award_achievement_success(self, client, test_user, test_achievement):
        award_data = {
            "user_id": test_user.id,
            "achievement_id": test_achievement.id
        }
        response = client.post("/api/achievements/award/", json=award_data)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["achievement_id"] == test_achievement.id

    def test_award_achievement_user_not_found(self, client, test_achievement):
        award_data = {
            "user_id": 999,
            "achievement_id": test_achievement.id
        }
        response = client.post("/api/achievements/award/", json=award_data)
        assert response.status_code == 404

    def test_award_achievement_not_found(self, client, test_user):
        award_data = {
            "user_id": test_user.id,
            "achievement_id": 999
        }
        response = client.post("/api/achievements/award/", json=award_data)
        assert response.status_code == 404

    def test_award_duplicate_achievement(self, client, test_user, test_achievement, test_user_achievement):
        award_data = {
            "user_id": test_user.id,
            "achievement_id": test_achievement.id
        }
        response = client.post("/api/achievements/award/", json=award_data)
        assert response.status_code == 200

class TestUserAchievementsEndpoints:
    def test_get_user_achievements_with_language(self, client, test_user, test_achievement, test_user_achievement):
        response = client.get(f"/api/users/{test_user.id}/achievements/")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["language"] == test_user.language
        assert len(data["achievements"]) == 1
        achievement = data["achievements"][0]
        assert achievement["name"] == test_achievement.name_ru
        assert achievement["description"] == test_achievement.description_ru

    def test_get_user_achievements_empty(self, client, test_user):
        response = client.get(f"/api/users/{test_user.id}/achievements/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["achievements"]) == 0

    def test_get_user_achievements_user_not_found(self, client):
        response = client.get("/api/users/999/achievements/")
        assert response.status_code == 404

class TestStatisticsEndpoints:
    def test_max_achievements_with_data(self, client, db_session):
        user1 = db_models.User(username="user1", language="ru")
        user2 = db_models.User(username="user2", language="en")
        db_session.add_all([user1, user2])
        db_session.commit()

        ach = db_models.Achievement(
            name="Test",
            points=10,
            description="Test"
        )
        db_session.add(ach)
        db_session.commit()

        for _ in range(3):
            ua = db_models.UserAchievement(user_id=user2.id, achievement_id=ach.id)
            db_session.add(ua)
        db_session.commit()

        response = client.get("/api/stats/max-achievements/")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "user2"
        assert data["total_achievements"] == 3

    def test_max_achievements_no_data(self, client):
        response = client.get("/api/stats/max-achievements/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_max_points_with_data(self, client, db_session):
        user1 = db_models.User(username="user1", language="ru")
        user2 = db_models.User(username="user2", language="en")
        db_session.add_all([user1, user2])
        db_session.commit()

        ach1 = db_models.Achievement(name="Ach1", points=50, description="Test")
        ach2 = db_models.Achievement(name="Ach2", points=100, description="Test")
        db_session.add_all([ach1, ach2])
        db_session.commit()

        ua1 = db_models.UserAchievement(user_id=user1.id, achievement_id=ach1.id)
        ua2 = db_models.UserAchievement(user_id=user2.id, achievement_id=ach2.id)
        db_session.add_all([ua1, ua2])
        db_session.commit()

        response = client.get("/api/stats/max-points/")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "user2"
        assert data["total_points"] == 100

    def test_max_difference_with_data(self, client, db_session):
        users = []
        for i in range(3):
            user = db_models.User(username=f"user{i}", language="ru")
            users.append(user)
        db_session.add_all(users)
        db_session.commit()

        ach = db_models.Achievement(name="Test", points=10, description="Test")
        db_session.add(ach)
        db_session.commit()

        for i, count in enumerate([1, 3, 5]):
            for _ in range(count):
                ua = db_models.UserAchievement(user_id=users[i].id, achievement_id=ach.id)
                db_session.add(ua)
        db_session.commit()

        response = client.get("/api/stats/max-difference/")
        assert response.status_code == 200
        data = response.json()
        assert data["difference"] == 40

    def test_min_difference_with_data(self, client, db_session):
        users = []
        for i in range(3):
            user = db_models.User(username=f"user{i}", language="ru")
            users.append(user)
        db_session.add_all(users)
        db_session.commit()

        ach = db_models.Achievement(name="Test", points=10, description="Test")
        db_session.add(ach)
        db_session.commit()

        for i, count in enumerate([2, 3, 5]):
            for _ in range(count):
                ua = db_models.UserAchievement(user_id=users[i].id, achievement_id=ach.id)
                db_session.add(ua)
        db_session.commit()

        response = client.get("/api/stats/min-difference/")
        assert response.status_code == 200
        data = response.json()
        assert data["difference"] == 10

    def test_seven_day_streak_no_data(self, client):
        response = client.get("/api/stats/seven-day-streak/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

class TestCRUDOperations:
    def test_get_user_by_username_with_mock(self, mock_db):
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = db_models.User(
            id=1, username="testuser", language="ru"
        )
        result = crud.get_user_by_username(mock_db, "testuser")
        assert result is not None
        assert result.username == "testuser"

    def test_create_user_with_mock(self, mock_db):
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_achievements_with_mock(self, mock_db):
        mock_query = mock_db.query.return_value
        mock_offset = mock_query.offset.return_value
        mock_offset.limit.return_value.all.return_value = [
            db_models.Achievement(id=1, name="Ach1", points=10, description="Test")
        ]
        result = crud.get_achievements(mock_db, skip=0, limit=10)
        assert len(result) == 1
        assert result[0].name == "Ach1"

    def test_award_achievement_existing_with_mock(self, mock_db):
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = db_models.UserAchievement(id=1)
        
        result = crud.award_achievement(mock_db, 1, 1)
        
        assert result.id == 1
        mock_db.add.assert_not_called()

    def test_award_achievement_new_with_mock(self, mock_db):
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()