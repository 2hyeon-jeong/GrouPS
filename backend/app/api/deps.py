"""
API Dependencies (의존성 주입)
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import decode_access_token
from app.models import User

# HTTP Bearer 토큰 스키마
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """현재 로그인한 사용자 정보를 가져오는 dependency"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 토큰 디코딩
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    handle: Optional[str] = payload.get("sub")
    if handle is None:
        raise credentials_exception
    
    # 사용자 조회
    result = await db.execute(select(User).where(User.handle == handle))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user
