# Backend API

Base URL: `http://localhost:8000` (Docker 외부) / `http://backend:8000` (Docker 내부)

OpenAPI: `GET /docs` (Swagger UI), `GET /openapi.json`

---

## POST /api/route

라우팅만 수행 (DB 저장 안 함). UI에서 "분석하기" 클릭 시 호출.

**Request**
```json
{
  "purpose": "매일 오전 ERP에서 생산 데이터를 추출하여 이상값을 감지하고 담당자에게 알림",
  "domains": ["data", "legacy"],
  "systems": "SAP ERP, Oracle DB, Teams",
  "frequency": "daily",
  "security": "high",
  "scale": "department",
  "constraints": "private 네트워크 내에서만 실행"
}
```

**Response**
```json
{
  "primary": "custom",
  "confidence": 87,
  "verdict": "Custom Agent로 개발 권장",
  "verdict_sub": "Legacy 시스템 깊은 통합 + 보안 요건",
  "reasoning": "...",
  "scores": { "palantir": 64, "copilot": 28, "custom": 91, "ixi": 35 },
  "stack": ["LangGraph", "..."],
  "alternatives": ["Palantir AIP를 데이터 분석 부분만 분리 호출"],
  "warnings": ["개발·운영 비용이 가장 크다"],
  "rule_scores": { "palantir": 60, "copilot": 25, "custom": 88, "ixi": 30 },
  "model": "claude-sonnet-4-6"
}
```

---

## POST /api/tickets

라우팅 + DB 저장. 결정 확정 시 호출.

**Request**: `POST /api/route` 와 동일 + `title`, `requester`.

**Response**: 라우팅 결과 + `id`(ticket ID), `created_at`.

---

## GET /api/tickets

이력 조회.

Query:
- `limit` (default 50)
- `offset` (default 0)
- `platform` (필터)

---

## GET /api/tickets/{id}

단건 상세.

---

## GET /api/platforms

플랫폼 메타 (이름, 강점, 색상 등). UI 가이드 페이지용.

---

## GET /healthz

헬스체크.
