# AgentPlatform — Agent 과제 라우팅 시스템

회사가 도입한 4개 Agent 플랫폼 중 **새로 들어오는 Agent 과제를 어디서 개발해야 하는지** 라우팅·문서화·이력화하는 사내 시스템.

- Palantir AIP · MS Copilot Studio · Custom Agent (AWS/GCP) · ixi-Enterprise
- 사용자: 전략·기획 직무 (비개발자)
- 결정: LLM 라우팅 + 룰북 가중치 하이브리드, 모든 결정 DB 영속화

상세 컨텍스트는 [`CLAUDE.md`](./CLAUDE.md) 참고.

---

## 빠른 실행

전제: Docker Desktop 설치, 빈 8000/3000/5432 포트.

```bash
cp .env.example .env
# .env 의 ANTHROPIC_API_KEY 를 본인 키로 교체
docker compose up --build
```

- 메인: http://localhost:3000
- API: http://localhost:8000/docs (Swagger)
- DB: localhost:5432 (agent / agent / agentplatform)

종료: `Ctrl+C` → `docker compose down`
DB까지 초기화: `docker compose down -v`

---

## 디렉토리

| 경로 | 설명 |
|---|---|
| `CLAUDE.md` / `AGENTS.md` | AI agent 작업 가이드 |
| `docs/DECISIONS.md` | ADR (의사결정 이력) |
| `docs/ROADMAP.md` | 단계별 로드맵 |
| `docs/PLATFORMS.md` | 4개 플랫폼 라우팅 룰북 |
| `docs/API.md` | 백엔드 API 명세 |
| `backend/` | FastAPI 백엔드 |
| `frontend/` | Next.js 프론트엔드 |
| `ref/` | 원본 시안 (참고용, 손대지 않음) |

---

## 개발

자세한 가이드는 `CLAUDE.md` §7 "진행 상태" 와 `docs/ROADMAP.md` 참고.

### 백엔드만 따로

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 프론트엔드만 따로

```bash
cd frontend
npm install
npm run dev
```

---

## 라이선스

내부용. 외부 공개 금지.
