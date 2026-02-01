"""
Solved.ac API 클라이언트
"""
import httpx
import logging
from typing import Optional, Dict, Any, List

# 로거 설정
logger = logging.getLogger(__name__)


class SolvedAPIClient:
    """Solved.ac API 클라이언트"""
    
    BASE_URL = "https://solved.ac/api/v3"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def __init__(self):
        # User-Agent 헤더를 기본으로 포함
        headers = {
            "User-Agent": self.USER_AGENT
        }
        self.client = httpx.AsyncClient(timeout=10.0, headers=headers)
    
    async def check_user_exists(self, handle: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        백준 핸들이 실존하는지 확인
        
        Args:
            handle: 백준 아이디
            
        Returns:
            (존재 여부, 사용자 정보 또는 None)
        """
        try:
            url = f"{self.BASE_URL}/user/show"
            params = {"handle": handle}
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                user_data = response.json()
                return True, user_data
            else:
                return False, None
                
        except Exception as e:
            print(f"Solved.ac API Error: {e}")
            return False, None
    
    async def get_user_info(self, handle: str) -> Optional[Dict[str, Any]]:
        """
        백준 사용자 상세 정보 조회
        
        Args:
            handle: 백준 아이디
            
        Returns:
            사용자 정보 딕셔너리 또는 None
        """
        exists, user_data = await self.check_user_exists(handle)
        return user_data if exists else None
    
    async def get_max_problem_id(self) -> int:
        """
        현재 백준에서 가장 큰 문제 번호를 조회
        
        Returns:
            최대 문제 ID
        """
        try:
            url = f"{self.BASE_URL}/search/problem"
            params = {
                "query": "*",
                "sort": "id",
                "direction": "desc",
                "page": 1
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    max_id = items[0].get("problemId", 0)
                    print(f"✅ Solved.ac 최대 문제 ID: {max_id}")
                    return max_id
                else:
                    print("⚠️  문제 데이터를 찾을 수 없습니다.")
                    return 0
            else:
                print(f"❌ API 호출 실패: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"❌ Solved.ac API Error (get_max_problem_id): {e}")
            return 0
    
    async def fetch_problems_detail(self, problem_ids: List[int]) -> List[Dict[str, Any]]:
        """
        특정 문제 ID들의 상세 정보를 조회 (100개씩 청크 처리)
        
        Args:
            problem_ids: 조회할 문제 ID 리스트 (최대 100개 권장)
            
        Returns:
            문제 정보 리스트
        """
        if not problem_ids:
            return []
        
        try:
            # 1. 파라미터 변환: 리스트를 콤마로 구분된 문자열로 변환
            ids_str = ",".join(map(str, problem_ids))
            
            # 2. URL 및 파라미터 설정
            url = f"{self.BASE_URL}/problem/lookup"
            params = {"problemIds": ids_str}
            
            # 3. 검증용 로그: 실제 요청 URL 출력
            # httpx는 params를 자동으로 URL에 인코딩하므로 수동으로 구성
            full_url = f"{url}?problemIds={ids_str}"
            logger.info(f"🔗 Solved.ac API 요청: {full_url}")
            print(f"🔗 API 요청: {full_url}")
            
            # 4. API 호출
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # /problem/lookup은 배열을 직접 반환
                if isinstance(data, list):
                    items = data
                else:
                    items = []
                
                # 필요한 필드만 추출
                problems = []
                for item in items:
                    problem = {
                        "problemId": item.get("problemId"),
                        "titleKo": item.get("titleKo", ""),
                        "level": item.get("level", 0),
                        "tags": [tag.get("key") for tag in item.get("tags", [])]
                    }
                    problems.append(problem)
                
                print(f"✅ 문제 조회 성공: {len(problems)}개")
                return problems
            else:
                print(f"⚠️  문제 상세 조회 실패: {response.status_code}")
                print(f"   응답: {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"❌ fetch_problems_detail Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        await self.client.aclose()


# 싱글톤 인스턴스
_solved_client: Optional[SolvedAPIClient] = None


def get_solved_client() -> SolvedAPIClient:
    """Solved.ac API 클라이언트 의존성 주입"""
    global _solved_client
    if _solved_client is None:
        _solved_client = SolvedAPIClient()
    return _solved_client
