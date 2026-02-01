"""
JWT 토큰 관련 Pydantic 스키마
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """JWT 토큰 응답"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """토큰 데이터"""
    handle: Optional[str] = None
