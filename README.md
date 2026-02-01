# BOJ SOMA Manager

백준(Solved.ac) 그룹 관리 및 분석 서비스

## 📋 프로젝트 소개

이 프로젝트는 백준 온라인 저지의 그룹을 효율적으로 관리하고 분석하는 웹 서비스입니다.
사용자들의 문제 풀이 기록을 추적하고 통계를 제공합니다.

## 🛠 기술 스택

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **SQLAlchemy**: ORM (비동기 지원)
- **PostgreSQL**: 관계형 데이터베이스
- **Pydantic**: 데이터 검증 및 설정 관리
- **JWT**: 사용자 인증

### Frontend
- **HTML5/CSS3**: 마크업 및 스타일링
- **JavaScript (Vanilla)**: 클라이언트 로직
- **Bootstrap 5**: UI 프레임워크

### Infrastructure
- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 컨테이너 오케스트레이션

## 📁 프로젝트 구조

```
temp_project/
├── backend/                  # 백엔드 애플리케이션
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI 메인 애플리케이션
│   │   ├── database.py      # DB 연결 및 세션 관리
│   │   ├── core/            # 핵심 유틸리티
│   │   │   ├── config.py    # 설정 관리
│   │   │   └── security.py  # 보안 (JWT, 해싱)
│   │   ├── models/          # SQLAlchemy 모델
│   │   │   └── models.py    # User, Group, SolvedLog
│   │   ├── schemas/         # Pydantic 스키마
│   │   │   └── schemas.py   # Request/Response 모델
│   │   └── api/             # API 엔드포인트
│   │       ├── deps.py      # 의존성 주입
│   │       └── endpoints/
│   │           ├── auth.py  # 인증 API
│   │           └── users.py # 사용자 API
│   ├── requirements.txt     # Python 의존성
│   └── Dockerfile          # Docker 이미지 빌드
├── frontend/                # 프론트엔드 애플리케이션
│   ├── index.html          # 로그인 페이지
│   ├── css/
│   │   └── style.css       # 커스텀 스타일
│   └── js/
│       └── app.js          # 클라이언트 로직
├── docker-compose.yml      # Docker Compose 설정
├── env.example             # 환경 변수 예시
├── .gitignore              # Git 무시 파일
└── README.md               # 프로젝트 문서
```

## 🗄 데이터베이스 스키마

### User (사용자)
- `id`: Primary Key
- `handle`: 백준 아이디 (Unique)
- `password_hash`: 해시된 비밀번호
- `created_at`: 가입 일시

### Group (그룹)
- `id`: Primary Key
- `name`: 그룹명 (Unique)
- `description`: 그룹 설명
- `created_at`: 생성 일시

### SolvedLog (문제 풀이 기록)
- `id`: Primary Key
- `user_id`: 사용자 ID (Foreign Key)
- `problem_id`: 백준 문제 번호
- `solved_at`: 풀이 완료 일시

## 🚀 시작하기

### 사전 요구사항
- Docker & Docker Compose
- Git

### 설치 및 실행

1. **저장소 클론**
```bash
git clone <repository-url>
cd temp_project
```

2. **환경 변수 설정**
```bash
cp env.example .env
# .env 파일을 열어 필요한 값들을 수정하세요
```

3. **Docker Compose로 실행**
```bash
docker-compose up -d
```

4. **서비스 확인**
- API 서버: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- 로그인 페이지: http://localhost:8000/static/index.html

5. **초기 테스트 계정 생성**

브라우저에서 http://localhost:8000/static/index.html 로 접속 후:
- "회원가입" 버튼 클릭
- 테스트 계정 생성 (예: `testuser` / `test1234`)

또는 API 문서에서 직접 호출:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"handle": "testuser", "password": "test1234"}'
```

## 📡 API 엔드포인트

### 인증 (Authentication)

#### POST `/auth/register`
회원가입
```json
{
  "handle": "testuser",
  "password": "password123"
}
```

#### POST `/auth/login`
로그인 (JWT 토큰 발급)
```json
{
  "handle": "testuser",
  "password": "password123"
}
```

### 사용자 (Users)

#### GET `/users/me`
현재 로그인한 사용자 정보 조회
- Authorization: Bearer {token} 필요

## 🧪 개발 환경

### 로컬 개발 (Docker 없이)

1. **Python 가상환경 생성**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **PostgreSQL 실행** (별도로 설치 필요)
```bash
# Docker로 DB만 실행하는 경우
docker run -d \
  --name boj_postgres \
  -e POSTGRES_USER=boj_user \
  -e POSTGRES_PASSWORD=boj_password \
  -e POSTGRES_DB=boj_soma_db \
  -p 5432:5432 \
  postgres:15-alpine
```

4. **환경 변수 설정**
```bash
export DATABASE_URL="postgresql+asyncpg://boj_user:boj_password@localhost:5432/boj_soma_db"
export SECRET_KEY="your-secret-key"
```

5. **API 서버 실행**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# API 서버 로그만
docker-compose logs -f api

# DB 로그만
docker-compose logs -f db
```

### 컨테이너 재시작

```bash
docker-compose restart
```

### 컨테이너 중지 및 제거

```bash
docker-compose down

# 볼륨까지 제거 (데이터베이스 데이터 삭제)
docker-compose down -v
```

## 🔐 보안 설정

### 프로덕션 환경 배포 시 주의사항

1. **SECRET_KEY 변경**
   - `env.example`의 `SECRET_KEY`를 강력한 랜덤 키로 변경

2. **CORS 설정**
   - `backend/app/core/config.py`에서 `BACKEND_CORS_ORIGINS`를 특정 도메인만 허용

3. **데이터베이스 비밀번호**
   - 기본 비밀번호 `boj_password`를 강력한 비밀번호로 변경

4. **SQL 쿼리 로깅 비활성화**
   - `backend/app/database.py`의 `echo=True`를 `echo=False`로 변경

## 📝 TODO

- [ ] 그룹 관리 API 구현
- [ ] 문제 풀이 기록 API 구현
- [ ] Solved.ac API 연동
- [ ] 대시보드 페이지 구현
- [ ] 그룹 통계 및 분석 기능
- [ ] 알림 기능
- [ ] 관리자 페이지

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License.

## 👥 팀

- 소마 프로젝트 팀

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ for SOMA Project**
