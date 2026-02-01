"""
데이터베이스 연결 및 세션 관리
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# 비동기 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # SQL 쿼리 로깅 (프로덕션에서는 False)
    future=True,
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base 클래스 (모든 모델의 부모)
Base = declarative_base()


async def get_db():
    """데이터베이스 세션 dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
