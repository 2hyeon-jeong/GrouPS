"""
Group 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    """그룹 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="그룹명")
    description: Optional[str] = Field(None, description="그룹 설명")


class GroupCreate(GroupBase):
    """그룹 생성 요청"""
    icon: str = Field(default="🎯", max_length=10, description="그룹 아이콘 (이모지)")
    password: Optional[str] = Field(None, min_length=4, description="비공개 그룹 비밀번호")
    max_members: int = Field(default=10, ge=2, le=100, description="최대 멤버 수")


class GroupResponse(GroupBase):
    """그룹 응답"""
    id: int
    owner_id: int
    icon: str
    max_members: int
    member_count: int = 0  # 현재 멤버 수
    created_at: datetime
    
    class Config:
        from_attributes = True


class MemberInfo(BaseModel):
    """그룹 멤버 정보"""
    user_id: int
    handle: str
    tier: int
    solved_count: int
    role: str  # 'admin' or 'member'
    joined_at: datetime
    
    class Config:
        from_attributes = True


class GroupDetailResponse(GroupBase):
    """그룹 상세 정보 (멤버 리스트 포함)"""
    id: int
    owner_id: int
    icon: str
    max_members: int
    member_count: int
    created_at: datetime
    members: List[MemberInfo] = []
    is_member: bool = False  # 현재 사용자가 멤버인지 여부
    
    class Config:
        from_attributes = True


class GroupJoinRequest(BaseModel):
    """그룹 가입 요청"""
    password: Optional[str] = Field(None, description="비공개 그룹인 경우 비밀번호")
