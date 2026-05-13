# Backend API

Base URL: `http://localhost:8000` (Docker 외부) / `http://backend:8000` (Docker 내부)

OpenAPI: `GET /docs` (Swagger UI), `GET /openapi.json`

LLM 비활성(=`ANTHROPIC_API_KEY` 미설정) 시 모든 라우팅 응답의 `model` 필드는 `"rule-only"`이며, `warnings`에 fallback 사유가 들어갑니다. LLM 활성 시 `model`은 `claude-sonnet-4-6`(또는 `.env`의 `ANTHROPIC_MODEL`)이 들어갑니다.

---

## POST /api/route

라우팅만 수행 (DB 저장 안 함). UI에서 "최적 플랫폼 분석" 클릭 시 호출.

**Request**
```json
{
  "purpose": "매일 오전 UCube에서 발주 데이터를 추출해 이상치를 감지하고 담당자에게 알림",
  "domains": ["data", "legacy"],
  "systems": "UCube, UCRM, MS Teams",
  "frequency": "daily",
  "security": "high",
  "scale": "department",
  "constraints": "private 네트워크 내에서만 실행"
}
```

**Validation**
- `purpose`: 5–2000자 필수
- `domains`: optional list — `data | productivity | legacy | workflow | knowledge | crossplatform`
- `frequency`: `realtime | hourly | daily | weekly | ondemand` (optional)
- `security`: `low | medium | high` (optional)
- `scale`: `individual | team | department | company` (optional)
- 검증 실패 시 **422 Unprocessable Entity**

**Response (200)**
```json
{
  "primary": "custom",
  "confidence": 87,
  "verdict": "Custom Agent 권장",
  "verdict_sub": "Legacy 시스템 깊은 통합 + 보안 요건",
  "reasoning": "...",
  "scores":      { "palantir": 64, "copilot": 28, "custom": 91, "ixi": 35 },
  "rule_scores": { "palantir": 60, "copilot": 25, "custom": 88, "ixi": 30 },
  "stack":        ["LangGraph", "AWS Lambda"],
  "alternatives": ["Palantir AIP를 데이터 분석 부분만 분리 호출"],
  "warnings":     ["개발·운영 비용이 가장 크다"],
  "model": "claude-sonnet-4-6"
}
```

---

## POST /api/tickets

라우팅 + DB 영속화. "이력으로 저장" 클릭 시 호출.

**Request**: `POST /api/route` body + `title` (2–200자, 필수), `requester` (≤120자, default `"anonymous"`).

**Response (201 Created)**:
```json
{
  "id": 1,
  "title": "...",
  "purpose": "...",
  "domains": [...],
  "systems": "...",
  "frequency": "...",
  "security": "...",
  "scale": "...",
  "constraints": "...",
  "requester": "...",
  "created_at": "2026-05-13T12:55:54.120420Z",
  "decision": { ...RouteResult 구조 동일... }
}
```

---

## GET /api/tickets

이력 목록 조회 (created_at desc).

**Query**
- `limit` (default 50, 1–200)
- `offset` (default 0)
- `platform` (`palantir | copilot | custom | ixi`) — 결과의 primary 플랫폼으로 필터

**Response (200)**: `TicketOut[]` (위 POST 응답 구조)

---

## GET /api/tickets/{id}

단건 상세. 존재하지 않으면 **404 Not Found**.

---

## GET /api/platforms

플랫폼 메타 (UI 가이드 페이지·범례용).

**Response (200)**
```json
[
  {
    "code": "palantir",
    "name": "Palantir AIP",
    "tag": "데이터·운영 분석",
    "one_liner": "Ontology 기반 비즈니스 데이터 의사결정. DataLake·KPI 이상감지·예측.",
    "strengths": ["대규모 데이터 파이프라인", "..."],
    "weaknesses": ["M365 협업/문서 작업", "..."],
    "color": "#0E9B7F"
  },
  ...
]
```

---

## GET /healthz

헬스체크.

**Response (200)**
```json
{
  "status": "ok",
  "llm_enabled": true,
  "model": "claude-sonnet-4-6"   // llm_enabled=false 면 null
}
```

---

## GET /

루트 메타데이터.

**Response (200)**
```json
{ "name": "AgentPlatform API", "version": "0.1.0", "docs": "/docs" }
```
