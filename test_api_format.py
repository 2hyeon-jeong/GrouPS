#!/usr/bin/env python3
"""
Solved.ac API 형식 테스트 스크립트
수정된 fetch_problems_detail 함수의 URL 형식 검증
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.services.solved_client import SolvedAPIClient


async def test_fetch_problems():
    """문제 조회 테스트"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 Solved.ac API 형식 테스트")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    client = SolvedAPIClient()
    
    # 테스트 1: 3개 문제 조회
    print("📋 테스트 1: 문제 1000, 1001, 1002 조회")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    test_ids = [1000, 1001, 1002]
    
    problems = await client.fetch_problems_detail(test_ids)
    
    print()
    print(f"✅ 조회된 문제 수: {len(problems)}개")
    print()
    
    for problem in problems:
        print(f"  - [{problem['problemId']}] {problem['titleKo']} (Level: {problem['level']})")
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # 테스트 2: 5개 문제 조회
    print("📋 테스트 2: 문제 1003~1007 조회")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    test_ids = [1003, 1004, 1005, 1006, 1007]
    
    problems = await client.fetch_problems_detail(test_ids)
    
    print()
    print(f"✅ 조회된 문제 수: {len(problems)}개")
    print()
    
    for problem in problems:
        print(f"  - [{problem['problemId']}] {problem['titleKo']} (Level: {problem['level']})")
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ 테스트 완료!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_fetch_problems())
