"""
Problem & SolvedLog 관련 Pydantic 스키마
"""
from datetime import datetime
from pydantic import BaseModel, Field


class SolvedLogBase(BaseModel):
    """문제 풀이 기록 기본 스키마"""
    problem_id: int = Field(..., gt=0, description="백준 문제 번호")


class SolvedLogCreate(SolvedLogBase):
    """문제 풀이 기록 생성 요청"""
    user_id: int = Field(..., gt=0, description="사용자 ID")


class SolvedLogResponse(SolvedLogBase):
    """문제 풀이 기록 응답"""
    id: int
    user_id: int
    solved_at: datetime
    
    class Config:
        from_attributes = True
