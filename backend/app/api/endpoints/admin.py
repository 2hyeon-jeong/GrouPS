"""
관리자 전용 API 엔드포인트
백준 문제 동기화 등의 관리 기능
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.sync_service import sync_problems, get_sync_status

router = APIRouter()


@router.post("/sync/problems")
async def sync_problems_endpoint(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    백준 문제 동기화 (백그라운드 작업)
    
    - 현재 DB의 최대 문제 ID부터 Solved.ac의 최신 문제까지 크롤링
    - 100개씩 청크 단위로 처리
    - Rate Limit 준수 (0.5초 대기)
    
    Returns:
        즉시 응답 후 백그라운드에서 동기화 실행
    """
    # 백그라운드 태스크로 동기화 실행
    background_tasks.add_task(sync_problems, db)
    
    return {
        "status": "started",
        "message": "동기화 작업이 백그라운드에서 시작되었습니다.",
        "detail": "작업 완료까지 시간이 걸릴 수 있습니다. 서버 로그를 확인하세요."
    }


@router.get("/sync/status")
async def get_sync_status_endpoint(
    db: AsyncSession = Depends(get_db)
):
    """
    현재 동기화 상태 조회
    
    Returns:
        - db_problem_count: 현재 DB에 저장된 문제 수
        - db_max_id: 현재 DB의 최대 문제 ID
        - solved_max_id: Solved.ac의 최대 문제 ID
        - need_sync: 동기화가 필요한지 여부
        - pending_problems: 동기화 대기 중인 문제 수
    """
    status = await get_sync_status(db)
    
    return {
        "status": "success",
        "data": status
    }
