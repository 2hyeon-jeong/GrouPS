"""
User 관련 Pydantic 스키마
"""
from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    handle: str = Field(..., min_length=1, max_length=50, description="백준 아이디")


class UserCreate(UserBase):
    """사용자 생성 요청"""
    password: str = Field(..., min_length=4, description="비밀번호")


class UserLogin(BaseModel):
    """로그인 요청"""
    handle: str = Field(..., description="백준 아이디")
    password: str = Field(..., description="비밀번호")


class UserResponse(UserBase):
    """사용자 응답"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
