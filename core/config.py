from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DB_HOST: str = Field(..., env='DB_HOST')
    DB_PORT: int = Field(5432, env='DB_PORT')
    DB_NAME: str = Field(..., env='DB_NAME')
    DB_USER: str = Field(..., env='DB_USER')
    DB_PASSWORD: str = Field(..., env='DB_PASSWORD')
    
    # Application
    APP_NAME: str = Field("Achievements API", env='APP_NAME')
    DEBUG: bool = Field(True, env='DEBUG')
    SECRET_KEY: str = Field(..., env='SECRET_KEY')  # Добавлено
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()