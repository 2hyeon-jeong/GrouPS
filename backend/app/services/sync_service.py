"""
백준 문제 동기화 서비스
스마트하게 신규 문제만 업데이트
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.models import Problem
from app.services.solved_client import get_solved_client


async def sync_problems(db: AsyncSession):
    """
    백준 문제 데이터를 스마트하게 동기화
    
    Logic:
    1. 우리 DB의 최대 문제 ID 조회
    2. Solved.ac의 최대 문제 ID 조회
    3. 차이가 있으면 그 구간만 크롤링 & 저장
    """
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 백준 문제 동기화 시작")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    solved_client = get_solved_client()
    
    # 1. 범위 산정
    # 우리 DB의 최대 ID
    result = await db.execute(select(func.max(Problem.id)))
    db_max_id = result.scalar()
    
    start_id = db_max_id if db_max_id else 1000  # 기본값: 1000번부터
    
    print(f"📊 현재 DB 최대 문제 ID: {start_id}")
    
    # Solved.ac의 최대 ID
    end_id = await solved_client.get_max_problem_id()
    
    if end_id == 0:
        print("❌ Solved.ac API에서 최대 ID를 가져오지 못했습니다.")
        return
    
    print(f"🎯 Solved.ac 최대 문제 ID: {end_id}")
    
    # 업데이트 필요 여부 체크
    if start_id >= end_id:
        print("✅ 이미 최신 상태입니다. 업데이트할 데이터가 없습니다.")
        return
    
    total_problems = end_id - start_id
    print(f"📦 동기화 대상: {total_problems}개 문제 ({start_id + 1} ~ {end_id})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # 2. 크롤링 & 저장 (100개씩 청크 처리)
    CHUNK_SIZE = 100
    current_id = start_id + 1
    saved_count = 0
    
    while current_id <= end_id:
        chunk_end = min(current_id + CHUNK_SIZE - 1, end_id)
        chunk_ids = list(range(current_id, chunk_end + 1))
        
        print(f"🔄 처리 중: {current_id}~{chunk_end} / 목표: {end_id} ({len(chunk_ids)}개)")
        
        # API 호출
        problems_data = await solved_client.fetch_problems_detail(chunk_ids)
        
        # DB에 Upsert
        if problems_data:
            for problem_data in problems_data:
                problem_id = problem_data.get("problemId")
                title = problem_data.get("titleKo", "")
                level = problem_data.get("level", 0)
                tags = problem_data.get("tags", [])
                
                # 기존 문제 조회
                result = await db.execute(
                    select(Problem).where(Problem.id == problem_id)
                )
                existing_problem = result.scalar_one_or_none()
                
                if existing_problem:
                    # 업데이트
                    existing_problem.title = title
                    existing_problem.level = level
                    existing_problem.tags = tags
                else:
                    # 새로 추가
                    new_problem = Problem(
                        id=problem_id,
                        title=title,
                        level=level,
                        tags=tags
                    )
                    db.add(new_problem)
                
                saved_count += 1
            
            # 커밋
            await db.commit()
            print(f"✅ 저장 완료: {len(problems_data)}개 (누적: {saved_count}개)")
        else:
            print(f"⚠️  해당 구간에서 데이터를 가져오지 못했습니다.")
        
        # Rate Limit 준수
        await asyncio.sleep(0.5)
        
        # 다음 청크로 이동
        current_id = chunk_end + 1
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🎉 동기화 완료! 총 {saved_count}개 문제 처리")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


async def get_sync_status(db: AsyncSession) -> dict:
    """
    현재 동기화 상태 조회
    
    Returns:
        상태 정보 딕셔너리
    """
    # 우리 DB의 문제 개수
    result = await db.execute(select(func.count(Problem.id)))
    db_problem_count = result.scalar()
    
    # 우리 DB의 최대 ID
    result = await db.execute(select(func.max(Problem.id)))
    db_max_id = result.scalar()
    
    # Solved.ac의 최대 ID
    solved_client = get_solved_client()
    solved_max_id = await solved_client.get_max_problem_id()
    
    return {
        "db_problem_count": db_problem_count or 0,
        "db_max_id": db_max_id or 0,
        "solved_max_id": solved_max_id,
        "need_sync": (db_max_id or 0) < solved_max_id,
        "pending_problems": max(0, solved_max_id - (db_max_id or 0))
    }
