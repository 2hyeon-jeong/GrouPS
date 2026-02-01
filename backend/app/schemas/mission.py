"""
GroupMission 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# ============== Mission 관련 스키마 ==============

class MissionCreate(BaseModel):
    """미션 생성 요청"""
    title: str = Field(..., min_length=1, max_length=200, description="미션 제목")
    description: Optional[str] = Field(None, description="미션 설명")
    start_date: datetime = Field(..., description="시작일")
    end_date: datetime = Field(..., description="종료일")
    problem_ids: List[int] = Field(..., min_items=1, description="문제 번호 리스트")


class MissionProblemResponse(BaseModel):
    """미션에 포함된 문제 정보"""
    id: int
    title: str
    level: int
    
    class Config:
        from_attributes = True


class MissionResponse(BaseModel):
    """미션 응답"""
    id: int
    group_id: int
    title: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    created_at: datetime
    problems: List[MissionProblemResponse] = []
    
    class Config:
        from_attributes = True


# ============== 미션 현황판 관련 스키마 ==============

class MemberSolveDetail(BaseModel):
    """멤버의 문제별 풀이 현황"""
    handle: str
    solved_count: int
    total_count: int
    completion_rate: float  # 달성률 (%)
    details: Dict[int, bool]  # {problem_id: solved}


class MissionStatusResponse(BaseModel):
    """미션 현황판 응답"""
    mission_id: int
    mission_title: str
    start_date: datetime
    end_date: datetime
    problems: List[MissionProblemResponse]
    members_status: List[MemberSolveDetail]
