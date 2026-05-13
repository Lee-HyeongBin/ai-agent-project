# AgentPlatform — Claude 작업 가이드

이 파일은 Claude(또는 다른 AI agent)가 본 저장소에서 작업할 때 가장 먼저 읽어야 하는 문서다.
사람용 README는 `README.md`, 의사결정 이력은 `docs/DECISIONS.md` 를 참고한다.

---

## 1. 이 프로젝트가 무엇인가

회사가 도입한 **4개 Agent 플랫폼**(Palantir AIP / MS Copilot Studio / Custom AWS·GCP Agent / ixi-Enterprise) 중,
새로 들어오는 **Agent 과제를 어디서 개발해야 하는지를 라우팅·문서화·이력화**하는 사내 시스템.

### 매우 중요한 구분
- ❌ **자동 개발 시스템이 아니다.** 라우팅 결정만 내려준다.
- ✅ **전략·기획(문과) 직무가 쓰는 접수 창구**다. 개발자용 도구가 아니다.
- ✅ 결정의 **근거(reasoning)·대안·경고**가 항상 따라붙어야 한다. 점수만으로는 쓸모없다.

### 출생 배경 (정치 컨텍스트)
플랫폼 4개가 도입된 건 전략적 선택이 아니라 CEO의 즉흥 의사결정 누적의 결과다.
CTO 차원에서 이를 **사후적으로 정당화·운영화**하려는 시스템이라는 점이 본 도구의 진짜 목적 중 하나다.
→ 따라서 어느 플랫폼도 "절대 추천 안 함"으로 떨어지지 않도록, 각 플랫폼의 사용 명분이 살아있어야 한다.

---

## 2. 디렉토리 구조

```
ai-agent-project/
├── CLAUDE.md                  # 본 문서 — AI agent 작업 가이드
├── AGENTS.md                  # 동일 내용 심볼릭 (다른 agent 도구가 읽도록)
├── README.md                  # 사람용 시작 가이드
├── docker-compose.yml         # 3 services: db / backend / frontend
├── .env.example               # 환경변수 템플릿 (커밋 OK)
├── .env                       # 실제 키 (gitignore)
├── .gitignore
├── .dockerignore
│
├── docs/
│   ├── DECISIONS.md           # ADR — 모든 비가역적 결정 기록
│   ├── ROADMAP.md             # 단계별 작업 계획
│   ├── PLATFORMS.md           # 4개 플랫폼 라우팅 룰북 (LLM 시스템 프롬프트 원천)
│   └── API.md                 # 백엔드 엔드포인트 명세
│
├── backend/                   # FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── tickets.py
│   │   │   └── routing.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_router.py
│   │   │   ├── rule_router.py
│   │   │   └── platforms.py
│   │   └── prompts/
│   │       └── router_system.md
│   └── tests/
│
├── frontend/                  # Next.js 14 + TS + Tailwind
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.mjs
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # 메인 — 과제 접수 + 라우팅 결과
│   │   ├── tickets/page.tsx        # 이력
│   │   ├── platforms/page.tsx      # 플랫폼 가이드
│   │   └── globals.css
│   ├── components/
│   ├── lib/
│   │   └── api.ts                  # 백엔드 클라이언트
│   └── public/
│
└── ref/                       # 원본 시안 — 손대지 말 것
    ├── agent_router.html
    └── work_agent_4pillar.html
```

---

## 3. 기술 스택 (확정)

| Layer | 선택 | 비고 |
|---|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + TailwindCSS | ref/agent_router.html 다크/골드 무드 계승 |
| Backend | Python 3.11 + FastAPI + SQLAlchemy 2 (async) + asyncpg + Pydantic v2 | LLM 통합 자연스러움 |
| DB | PostgreSQL 16 | 라우팅 이력·감사 |
| LLM | Anthropic Claude (`claude-sonnet-4-6`) | 환경변수 `ANTHROPIC_API_KEY` |
| Orchestration | Docker Compose | 로컬 1-command 부팅 |

스택 변경 시 본 파일과 `docs/DECISIONS.md` 양쪽 갱신.

---

## 4. 핵심 도메인 모델

### Ticket (Agent 과제 접수)
- `id`, `title`, `purpose`, `domains[]`, `systems`, `frequency`, `security`, `scale`, `constraints`
- `requester`, `created_at`

### RoutingDecision (라우팅 결과)
- `id`, `ticket_id`, `primary_platform`, `scores{4}`, `confidence`, `verdict`, `verdict_sub`,
  `reasoning`, `stack[]`, `alternatives[]`, `warnings[]`
- `model_used`, `created_at`
- LLM 응답 원본 (`raw_response`) 도 보관 → 감사

### 플랫폼 enum
`palantir` / `copilot` / `custom` / `ixi`

---

## 5. 작업 원칙

1. **실제 동작 우선.** 문서나 그림보다 `docker compose up` 이 통과하는 코드.
2. **문과 사용자.** UI 카피, 에러 메시지, 가이드는 비개발자 기준. 약어는 풀어 쓰고 툴팁 제공.
3. **결정 = 근거 + 이력.** 라우팅 결과는 항상 근거·대안·경고를 동반하고, DB에 영속화한다.
4. **자율 진행.** 매 세션 끝에 `docs/ROADMAP.md`와 본 파일의 §7 진행 상태를 갱신.
5. **위임 + 통보.** 큰 기술 결정은 자율, 비가역 변경(파일 대량 삭제 / git push / 외부 호출)은 사용자 통보.

---

## 6. 로컬 실행

```bash
cp .env.example .env
# .env 에서 ANTHROPIC_API_KEY 설정
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (OpenAPI: /docs)
- Postgres: localhost:5432 (user: agent / pw: agent / db: agentplatform)

---

## 7. 진행 상태 (Claude가 직접 갱신)

### 완료
- [x] 프로젝트 컨텍스트 정리, CLAUDE.md / AGENTS.md / 메모리 작성
- [x] 디렉토리 구조 결정, 기술 스택 확정 (`docs/DECISIONS.md` ADR-0001)
- [x] Docker Compose (db / backend / frontend) 작성
- [x] Backend 구현 (FastAPI, Pydantic v2, SQLAlchemy 2 async, Anthropic SDK)
- [x] Rule Router (`backend/app/services/rule_router.py`) + LLM Router (`llm_router.py`) 하이브리드
- [x] LLM 키 없을 때 룰북 fallback 모드
- [x] Frontend 구현 (Next.js 14 App Router + TS + Tailwind)
- [x] 메인 라우팅 페이지 / 이력 페이지 / 이력 상세 / 플랫폼 가이드 페이지

### 검증 완료 (2026-05-13 세션 #2)
- [x] `docker compose up --build` 실제 빌드/실행 — 3 서비스 모두 healthy
- [x] 한 사이클 end-to-end — POST /api/tickets → DB → GET 리스트/상세/필터 모두 통과
- [x] 룰북 분기 동작 — SAP/legacy/high → Custom(100), Teams/M365 → Copilot(100)
- [x] Frontend SSR — `/`, `/tickets`, `/tickets/{id}`, `/platforms` 200 + 라우팅 결과 렌더링
- [x] LLM fallback 모드 — API 키 없을 때 룰북만으로 결과 + 경고 메시지 정상
- [x] **Anthropic API 실제 호출 + 응답 파싱** — `claude-sonnet-4-6` 호출 성공, JSON 파싱 안정, reasoning/stack/alternatives/warnings 모두 자연어 정상 생성, 문과 사용자용 괄호 풀이까지 자동 포함

### Tier 0~1 완료 (2026-05-14 세션 #3 — Phase 1 진입 점검)
- [x] **시크릿 hook**: `.pre-commit-config.yaml` 도입(gitleaks + pre-commit-hooks). 2026-05-13 인시던트(.env.example 키 노출) 재발 방지
- [x] **`.env.example` 안전 강화** + `verify_env.ps1` 에 placeholder 검사 추가
- [x] **README/SETUP 보안 섹션** — `.env` vs `.env.example` 차이, pre-commit 설치 가이드
- [x] **Frontend 접근성**: `ink-dim #8A8A8A → #5B5B5B` (WCAG AAA 통과), `focus-visible` ring 도입
- [x] **TypeScript 타입 안전**: `catch (e: any)` → `e: unknown` + `instanceof Error` 전면 교체
- [x] **플랫폼 컬러 중앙화**: `frontend/lib/api.ts` 에 `PLATFORM_DARK` `PLATFORM_TINT` 추가, 3개 페이지 import 정리
- [x] **LLM 견고성**: `max_retries=2` + `RateLimitError`·`APITimeoutError`·`APIConnectionError`·`APIStatusError` 별도 처리 + `request_id` 로그
- [x] **pytest 테스트 기반**: `backend/tests/` — `conftest.py`(in-memory aiosqlite), `test_rule_router.py` 8 cases, `test_llm_router.py` 6 cases (anthropic mock), `test_api.py` 8 cases (httpx ASGI)
- [x] **문서 동기화**: `AGENTS.md` 보강, `docs/API.md` 실제 엔드포인트와 동기화

### 다음 (Phase 1 본격, Tier 2)
- [ ] Alembic 마이그레이션 도입 (현재 `Base.metadata.create_all` 만)
- [ ] DB 인덱스 (`Ticket.created_at desc`, `RoutingDecision.primary`)
- [ ] 이력 페이지네이션·필터·검색 (backend cursor + frontend UI)
- [ ] LLM 응답 캐싱 (입력 해시 → 결과, Redis 또는 SQLite)
- [ ] 룰북 가중치 yaml 분리 (실측 케이스 보면서 튜닝)
- [ ] Backend Pydantic → frontend TS 자동 생성 (`openapi-typescript`)
- [ ] GitHub Actions CI — lint(ruff/eslint) + type(mypy/tsc) + pytest + trufflehog + docker build

### Tier 3 (Phase 2, 운영 강화)
- [ ] Production Dockerfile 분리 (멀티스테이지, 비-root, `--reload` 제거)
- [ ] 인증 (Bearer → SSO)
- [ ] CORS 화이트리스트 명시 (현재 `*`)
- [ ] 구조화 로깅 + audit log 분리
- [ ] Prometheus 메트릭

마지막 갱신: 2026-05-14 (세션 #3 — Tier 0·1 종료, Phase 1 본격 진입 가능)
