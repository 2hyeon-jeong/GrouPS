# BOJ Squad

Baekjoon Online Judge와 solved.ac 데이터를 활용해 알고리즘 학습 그룹을 관리하는 개인 프로젝트입니다.
그룹 멤버의 문제 풀이 기록을 확인하고, 주차별 미션과 진행률을 관리하는 것을 목표로 합니다.

## 프로젝트 소개

BOJ Squad는 알고리즘 스터디를 조금 더 편하게 운영하기 위해 만든 웹 서비스입니다.
사용자는 자신의 백준 핸들을 기준으로 가입하고, 그룹을 만들거나 참여해 함께 풀 문제를 관리할 수 있습니다.

현재는 인증, 사용자 정보 조회, 문제 데이터 동기화, 그룹과 미션 관리 API를 중심으로 구현되어 있습니다.

## 주요 기능

- 사용자 회원가입 및 로그인
- JWT 기반 인증
- solved.ac 문제 데이터 동기화
- 그룹 생성 및 멤버 관리
- 그룹별 미션 생성
- 미션 문제 목록과 멤버별 진행률 조회
- 정적 프론트엔드 제공

## 기술 스택

### Backend

- FastAPI
- SQLAlchemy Async ORM
- PostgreSQL
- Pydantic
- JWT

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Bootstrap 5

### Infrastructure

- Docker
- Docker Compose

## 프로젝트 구조

```text
GrouPS/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── endpoints/
│   │   │       ├── admin.py
│   │   │       ├── auth.py
│   │   │       ├── groups.py
│   │   │       └── users.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
├── docker-compose.yml
├── env.example
├── MISSION_GUIDE.md
├── SYNC_USAGE.md
├── test_api_format.py
├── test_sync.sh
└── README.md
```

## 데이터 모델

### User

- `id`: 사용자 ID
- `handle`: 백준 핸들
- `password_hash`: 해시된 비밀번호
- `created_at`: 가입 일시

### Group

- `id`: 그룹 ID
- `name`: 그룹 이름
- `description`: 그룹 설명
- `owner_id`: 그룹장 ID
- `created_at`: 생성 일시

### Problem

- `id`: 백준 문제 번호
- `title`: 문제 제목
- `level`: solved.ac 난이도
- `tags`: 문제 태그

### GroupMission

- `id`: 미션 ID
- `group_id`: 그룹 ID
- `title`: 미션 제목
- `description`: 미션 설명
- `start_date`: 시작 일시
- `end_date`: 종료 일시

### SolvedLog

- `id`: 풀이 기록 ID
- `user_id`: 사용자 ID
- `problem_id`: 백준 문제 번호
- `solved_at`: 풀이 완료 일시

## 시작하기

### 사전 준비

- Docker
- Docker Compose
- Git

### Docker Compose로 실행

1. 저장소를 클론합니다.

```bash
git clone <repository-url>
cd GrouPS
```

2. 환경 변수 파일을 준비합니다.

```bash
cp env.example .env
```

3. 서비스를 실행합니다.

```bash
docker-compose up -d
```

4. 브라우저에서 접속합니다.

- 프론트엔드: http://localhost:8000
- API 문서: http://localhost:8000/docs
- 헬스 체크: http://localhost:8000/api/health

## 로컬 개발

### 백엔드 단독 실행

1. Python 가상환경을 만듭니다.

```bash
cd backend
python -m venv venv
```

2. 가상환경을 활성화합니다.

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. 의존성을 설치합니다.

```bash
pip install -r requirements.txt
```

4. PostgreSQL을 실행합니다.

```bash
docker run -d \
  --name boj_groups_db \
  -e POSTGRES_USER=boj_user \
  -e POSTGRES_PASSWORD=boj_password \
  -e POSTGRES_DB=boj_groups_db \
  -p 5432:5432 \
  postgres:15-alpine
```

5. 환경 변수를 설정합니다.

```bash
export DATABASE_URL="postgresql+asyncpg://boj_user:boj_password@localhost:5432/boj_groups_db"
export SECRET_KEY="your-secret-key"
```

6. API 서버를 실행합니다.

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 요약

### 인증

#### `POST /auth/register`

회원가입

```json
{
  "handle": "testuser",
  "password": "password123"
}
```

#### `POST /auth/login`

로그인 및 JWT 토큰 발급

```json
{
  "handle": "testuser",
  "password": "password123"
}
```

### 사용자

#### `GET /users/me`

현재 로그인한 사용자 정보를 조회합니다.

```text
Authorization: Bearer <token>
```

### 문제 동기화

#### `GET /admin/sync/status`

현재 DB에 저장된 문제 수와 solved.ac 최신 문제 번호를 비교합니다.

#### `POST /admin/sync/problems`

아직 저장되지 않은 문제 정보를 solved.ac에서 가져와 DB에 저장합니다.

### 그룹과 미션

#### `POST /groups`

새 그룹을 생성합니다.

#### `GET /groups`

참여 가능한 그룹 목록을 조회합니다.

#### `POST /groups/{group_id}/missions`

그룹 미션을 생성합니다.

#### `GET /groups/{group_id}/missions/{mission_id}/status`

미션에 포함된 문제와 멤버별 풀이 진행률을 조회합니다.

## 유용한 명령어

```bash
# 전체 로그 확인
docker-compose logs -f

# API 서버 로그 확인
docker-compose logs -f api

# DB 로그 확인
docker-compose logs -f db

# 컨테이너 재시작
docker-compose restart

# 컨테이너 중지
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

## 환경 변수

기본값은 `env.example`에서 확인할 수 있습니다.

```env
DATABASE_URL=postgresql+asyncpg://boj_user:boj_password@db:5432/boj_groups_db
SECRET_KEY=your-super-secret-key-change-in-production-please-make-it-very-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
BACKEND_CORS_ORIGINS=["*"]
PROJECT_NAME=BOJ Squad
VERSION=0.1.0
```

## 보안 체크리스트

- 운영 환경에서는 `SECRET_KEY`를 반드시 강한 랜덤 문자열로 바꿉니다.
- 운영 환경에서는 `BACKEND_CORS_ORIGINS`를 실제 허용 도메인으로 제한합니다.
- 기본 DB 비밀번호 `boj_password`는 개발 환경에서만 사용합니다.
- SQLAlchemy 로그 설정은 운영 환경에서 비활성화합니다.

## TODO

- [ ] 그룹 관리 화면 개선
- [ ] 미션 생성 및 수정 UI
- [ ] solved.ac 사용자 풀이 기록 자동 동기화
- [ ] 미션 통계 대시보드
- [ ] 알림 기능
- [ ] 관리자 페이지

## 라이선스

This project is licensed under the MIT License.

## 문의

버그나 개선 아이디어가 있으면 이슈로 남겨 주세요.
