"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.endpoints import auth, users, admin, groups
from app.database import engine, Base

# 앱 초기화
app = FastAPI(
    title="BOJ Squad API",
    description="함께 성장하는 알고리즘 스터디 서비스",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록 (StaticFiles보다 먼저 등록해야 함)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(groups.router, prefix="/groups", tags=["Groups & Missions"])

# Frontend 정적 파일 서빙
# Docker 환경: /app/frontend
# 로컬 환경: ../frontend
frontend_path = "/app/frontend" if os.path.exists("/app/frontend") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
frontend_path = os.path.abspath(frontend_path)
print(f"📁 Frontend path: {frontend_path}")
print(f"✅ Frontend exists: {os.path.exists(frontend_path)}")

# 루트(/)에 정적 파일 마운트 - index.html이 메인 페이지가 됨
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
    print(f"🌐 Static files mounted at / (root)")


@app.on_event("startup")
async def startup_event():
    """앱 시작 시 실행"""
    # 데이터베이스 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 실행"""
    await engine.dispose()
    print("✅ Database connection closed")


@app.get("/api/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "message": "BOJ Squad API", "version": "0.1.0"}
