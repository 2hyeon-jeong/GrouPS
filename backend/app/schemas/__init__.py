"""
Schemas 패키지
모든 Pydantic 스키마를 한 곳에서 import
"""
from app.schemas.user import UserBase, UserCreate, UserLogin, UserResponse
from app.schemas.auth import Token, TokenData
from app.schemas.group import GroupBase, GroupCreate, GroupResponse, MemberInfo, GroupDetailResponse, GroupJoinRequest
from app.schemas.problem import SolvedLogBase, SolvedLogCreate, SolvedLogResponse
from app.schemas.mission import (
    MissionCreate,
    MissionResponse,
    MissionProblemResponse,
    MemberSolveDetail,
    MissionStatusResponse
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    # Auth
    "Token",
    "TokenData",
    # Group
    "GroupBase",
    "GroupCreate",
    "GroupResponse",
    "MemberInfo",
    "GroupDetailResponse",
    "GroupJoinRequest",
    # Problem
    "SolvedLogBase",
    "SolvedLogCreate",
    "SolvedLogResponse",
    # Mission
    "MissionCreate",
    "MissionResponse",
    "MissionProblemResponse",
    "MemberSolveDetail",
    "MissionStatusResponse",
]
