"""
애플리케이션 설정
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """앱 설정 클래스"""
    
    # 프로젝트 정보
    PROJECT_NAME: str = "BOJ Squad"
    VERSION: str = "0.1.0"
    API_PREFIX: str = ""
    
    # 데이터베이스
    DATABASE_URL: str = "postgresql+asyncpg://boj_user:boj_password@db:5432/boj_soma_db"
    
    # JWT 설정
    SECRET_KEY: str = "your-secret-key-change-this-in-production-make-it-very-long-and-random"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24시간
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """설정 객체를 캐시하여 반환"""
    return Settings()


settings = get_settings()
