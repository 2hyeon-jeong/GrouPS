"""
인증 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.schemas import UserLogin, Token, UserCreate, UserResponse
from app.models import User
from app.core.security import verify_password, create_access_token, get_password_hash
from app.services.solved_client import get_solved_client, SolvedAPIClient

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    로그인 API
    - 백준 아이디(handle)와 비밀번호로 로그인
    - 성공 시 JWT 토큰 반환
    """
    # 사용자 조회
    result = await db.execute(select(User).where(User.handle == user_login.handle))
    user = result.scalar_one_or_none()
    
    # 사용자가 없거나 비밀번호가 틀린 경우
    if not user or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.handle})
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    solved_client: SolvedAPIClient = Depends(get_solved_client)
):
    """
    회원가입 API - 백준 핸들 검증 포함
    
    Flow:
    1. 백준 핸들이 Solved.ac에 실존하는지 검증
    2. 검증 성공 시 사용자 정보를 DB에 저장
    3. 저장된 사용자 정보 반환
    """
    # 1. 중복 체크 (우리 DB)
    result = await db.execute(select(User).where(User.handle == user_create.handle))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 가입된 백준 아이디입니다"
        )
    
    # 2. 백준 핸들 검증 (Solved.ac API)
    exists, user_data = await solved_client.check_user_exists(user_create.handle)
    
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 백준 계정입니다. 백준 아이디를 확인해주세요."
        )
    
    # 3. 검증 성공 -> DB에 사용자 저장
    new_user = User(
        handle=user_create.handle,
        password_hash=get_password_hash(user_create.password),
        tier=user_data.get("tier", 0) if user_data else 0,
        solved_count=user_data.get("solvedCount", 0) if user_data else 0
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.get("/verify-handle/{handle}")
async def verify_handle(
    handle: str,
    solved_client: SolvedAPIClient = Depends(get_solved_client)
):
    """
    백준 핸들 검증 API (가입 전 미리 체크)
    
    Returns:
        - exists: 존재 여부
        - tier: Solved.ac 티어
        - solved_count: 푼 문제 수
    """
    exists, user_data = await solved_client.check_user_exists(handle)
    
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 백준 계정입니다"
        )
    
    return {
        "exists": True,
        "handle": user_data.get("handle"),
        "tier": user_data.get("tier", 0),
        "solved_count": user_data.get("solvedCount", 0),
        "message": "유효한 백준 계정입니다"
    }
