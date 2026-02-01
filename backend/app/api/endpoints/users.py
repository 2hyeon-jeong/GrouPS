"""
사용자 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_info(
    current_user: User = Depends(get_current_user)
):
    """
    현재 로그인한 사용자 정보 조회
    - JWT 토큰으로 인증된 사용자의 정보 반환
    """
    return current_user
