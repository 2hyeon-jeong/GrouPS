#!/bin/bash
# 백준 문제 동기화 테스트 스크립트

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 백준 문제 동기화 테스트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

BASE_URL="http://localhost:8000"

echo "1️⃣  현재 동기화 상태 조회..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s -X GET "${BASE_URL}/admin/sync/status" | python3 -m json.tool
echo ""
echo ""

echo "2️⃣  백준 문제 동기화 실행 (백그라운드)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s -X POST "${BASE_URL}/admin/sync/problems" | python3 -m json.tool
echo ""
echo ""

echo "✅ 동기화가 백그라운드에서 실행 중입니다."
echo "📋 진행 상황을 확인하려면 다음 명령어를 실행하세요:"
echo ""
echo "   docker logs -f boj_soma_api"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
