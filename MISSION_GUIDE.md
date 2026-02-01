# 그룹 스터디 관리 기능 가이드

## 📋 개요

이 기능은 **그룹 스터디의 주차별 학습 목표**를 관리하고, **멤버들의 달성률을 실시간으로 확인**할 수 있게 해줍니다.

---

## 🗂️ 데이터 구조

### DB 테이블

```
Group (그룹)
  ├─ GroupMember (멤버)
  └─ GroupMission (미션)
       └─ MissionProblem (문제)
              └─ Problem (문제 정보)

SolvedLog (풀이 기록)
  ├─ User
  └─ Problem
```

### 핵심 모델

#### 1. `GroupMission` (그룹 미션)
```python
{
  "id": 1,
  "group_id": 1,
  "title": "1주차 DP 부수기",
  "description": "기초 DP 문제 5개",
  "start_date": "2026-02-01T00:00:00",
  "end_date": "2026-02-07T23:59:59",
  "created_at": "2026-01-31T10:00:00"
}
```

#### 2. `MissionProblem` (미션-문제 연결)
```python
{
  "mission_id": 1,
  "problem_id": 1003,
  "order": 0  # 문제 순서
}
```

---

## 🔧 API 사용법

### 1️⃣ 미션 생성 (방장 전용)

**Endpoint:** `POST /groups/{group_id}/missions`

**권한:** 그룹 방장만 가능

**Request Body:**
```json
{
  "title": "1주차 DP 부수기",
  "description": "기초 DP 문제 5개를 풀어봅시다",
  "start_date": "2026-02-01T00:00:00",
  "end_date": "2026-02-07T23:59:59",
  "problem_ids": [1003, 9461, 1904, 9184, 1149]
}
```

**Response:**
```json
{
  "id": 1,
  "group_id": 1,
  "title": "1주차 DP 부수기",
  "description": "기초 DP 문제 5개를 풀어봅시다",
  "start_date": "2026-02-01T00:00:00",
  "end_date": "2026-02-07T23:59:59",
  "created_at": "2026-01-31T10:30:00",
  "problems": [
    {"id": 1003, "title": "피보나치 함수", "level": 8},
    {"id": 9461, "title": "파도반 수열", "level": 6},
    {"id": 1904, "title": "01타일", "level": 8},
    {"id": 9184, "title": "신나는 함수 실행", "level": 8},
    {"id": 1149, "title": "RGB거리", "level": 10}
  ]
}
```

**동작 원리:**
1. 그룹 존재 여부 확인
2. 방장 권한 확인
3. 문제 정보가 DB에 없으면 Solved.ac API로 자동 조회 & 저장 (Upsert)
4. 미션 생성
5. 문제들을 미션에 연결

**cURL 예시:**
```bash
curl -X POST "http://localhost:8000/groups/1/missions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1주차 DP 부수기",
    "description": "기초 DP 문제 5개",
    "start_date": "2026-02-01T00:00:00",
    "end_date": "2026-02-07T23:59:59",
    "problem_ids": [1003, 9461, 1904, 9184, 1149]
  }'
```

---

### 2️⃣ 미션 현황판 조회 (핵심 기능)

**Endpoint:** `GET /groups/{group_id}/missions/{mission_id}/status`

**권한:** 그룹 멤버 누구나 가능

**Response:**
```json
{
  "mission_id": 1,
  "mission_title": "1주차 DP 부수기",
  "start_date": "2026-02-01T00:00:00",
  "end_date": "2026-02-07T23:59:59",
  "problems": [
    {"id": 1003, "title": "피보나치 함수", "level": 8},
    {"id": 9461, "title": "파도반 수열", "level": 6},
    {"id": 1904, "title": "01타일", "level": 8},
    {"id": 9184, "title": "신나는 함수 실행", "level": 8},
    {"id": 1149, "title": "RGB거리", "level": 10}
  ],
  "members_status": [
    {
      "handle": "koosaga",
      "solved_count": 3,
      "total_count": 5,
      "completion_rate": 60.0,
      "details": {
        "1003": true,
        "9461": true,
        "1904": true,
        "9184": false,
        "1149": false
      }
    },
    {
      "handle": "tourist",
      "solved_count": 5,
      "total_count": 5,
      "completion_rate": 100.0,
      "details": {
        "1003": true,
        "9461": true,
        "1904": true,
        "9184": true,
        "1149": true
      }
    },
    {
      "handle": "student1",
      "solved_count": 1,
      "total_count": 5,
      "completion_rate": 20.0,
      "details": {
        "1003": true,
        "9461": false,
        "1904": false,
        "9184": false,
        "1149": false
      }
    }
  ]
}
```

**동작 원리:**
1. 미션 정보 조회
2. 미션에 포함된 문제 목록 조회
3. 그룹의 모든 멤버 조회
4. 각 멤버에 대해:
   - `SolvedLog` 테이블에서 해당 문제를 푼 기록 확인
   - 문제별 풀이 여부 계산 (`details`)
   - 달성률 계산 (`completion_rate`)

**cURL 예시:**
```bash
curl -X GET "http://localhost:8000/groups/1/missions/1/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 3️⃣ 그룹의 모든 미션 목록 조회

**Endpoint:** `GET /groups/{group_id}/missions`

**권한:** 그룹 멤버 누구나 가능

**Response:**
```json
[
  {
    "id": 2,
    "group_id": 1,
    "title": "2주차 그래프 탐색",
    "description": "BFS/DFS 기초",
    "start_date": "2026-02-08T00:00:00",
    "end_date": "2026-02-14T23:59:59",
    "created_at": "2026-02-05T10:00:00",
    "problems": [...]
  },
  {
    "id": 1,
    "group_id": 1,
    "title": "1주차 DP 부수기",
    "description": "기초 DP 문제 5개",
    "start_date": "2026-02-01T00:00:00",
    "end_date": "2026-02-07T23:59:59",
    "created_at": "2026-01-31T10:30:00",
    "problems": [...]
  }
]
```

**cURL 예시:**
```bash
curl -X GET "http://localhost:8000/groups/1/missions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🎯 사용 시나리오

### 시나리오 1: 주차별 스터디 운영

1. **월요일**: 방장이 이번 주 미션 생성
   ```bash
   POST /groups/1/missions
   {
     "title": "1주차 DP 부수기",
     "problem_ids": [1003, 9461, 1904, 9184, 1149],
     "start_date": "2026-02-03",
     "end_date": "2026-02-09"
   }
   ```

2. **화~토**: 멤버들이 문제 풀이
   - 백준에서 문제 풀면 자동으로 `SolvedLog` 업데이트 (별도 크롤링 필요)

3. **일요일**: 현황판 확인 & 회고
   ```bash
   GET /groups/1/missions/1/status
   
   결과:
   - 민수: 5/5 (100%) ✅
   - 영희: 3/5 (60%)  ⚠️
   - 철수: 2/5 (40%)  ❌
   ```

---

## 🔐 권한 관리

| API | 방장 | 일반 멤버 |
|-----|------|-----------|
| 미션 생성 | ✅ | ❌ |
| 미션 목록 조회 | ✅ | ✅ |
| 미션 현황판 조회 | ✅ | ✅ |

---

## 💡 주의사항

### 1. 문제 정보 자동 저장
- 미션 생성 시 문제 ID를 입력하면, DB에 없는 문제는 자동으로 Solved.ac API에서 가져와 저장합니다.
- 33,000개 이상의 문제가 이미 동기화되어 있으므로, 대부분의 문제는 API 호출 없이 바로 연결됩니다.

### 2. SolvedLog 업데이트
- 현재는 수동으로 `SolvedLog`를 생성해야 합니다.
- 추후 백준 크롤링 기능을 추가하면 자동으로 업데이트됩니다.

### 3. 방장 권한
- 그룹의 `owner_id`와 현재 로그인한 사용자의 `id`가 일치해야 미션을 생성할 수 있습니다.

---

## 🚀 다음 단계

추가하면 좋을 기능들:

1. **미션 수정/삭제**
   - `PUT /groups/{group_id}/missions/{mission_id}`
   - `DELETE /groups/{group_id}/missions/{mission_id}`

2. **자동 SolvedLog 업데이트**
   - Solved.ac API로 사용자의 최근 풀이 기록 크롤링
   - 주기적으로 실행 (Celery + Redis)

3. **미션 통계**
   - 평균 달성률
   - 가장 많이 푼 문제 / 가장 적게 푼 문제
   - 주차별 진행 추이

4. **알림 기능**
   - 미션 종료 D-1 알림
   - 특정 멤버가 모든 문제를 완료했을 때 알림

---

## 🧪 테스트

Swagger UI에서 테스트할 수 있습니다:

```
http://localhost:8000/docs
```

"Groups & Missions" 섹션을 확인하세요!
