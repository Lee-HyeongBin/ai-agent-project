# Architecture Decision Records

비가역적 / 영향이 큰 결정은 여기에 누적. 신규 결정 추가 시 위에 추가 (역시간순).

---

## ADR-0003 — 라우팅을 LLM 단독이 아닌 룰북+LLM 하이브리드로

**Date:** 2026-05-13
**Status:** Accepted

**Context:** ref/agent_router.html 초안은 100% LLM 단독 판단. 보안·규모·실행빈도 같은 **결정론적 제약**(예: 보안=high + private 네트워크 → custom 강제)을 LLM이 무시할 위험.

**Decision:** 라우팅을 두 단계로 분리.
1. **Rule Router** — 결정론적 가중치·하드 제약 (룰북: `docs/PLATFORMS.md`).
2. **LLM Router** — 룰북 결과를 입력으로 받아 자연어 근거·대안·경고 생성.

룰북의 출력이 LLM의 입력 컨텍스트로 들어가므로, LLM은 결정을 *설명·보완·반박* 할 수 있다.

**Consequences:**
- 정치적 정당화(설명가능성) ↑
- 룰북 유지보수 비용 발생 → `docs/PLATFORMS.md` 가 진실의 원천
- 향후 룰북 편집을 UI에서 가능하게 만들면 운영팀 자율성 ↑

---

## ADR-0002 — 데이터베이스를 라우팅 시스템의 1차 시민으로

**Date:** 2026-05-13
**Status:** Accepted

**Context:** ref/agent_router.html은 무상태. 결과가 화면에만 뜨고 사라짐.

**Decision:** Ticket / RoutingDecision 모델을 만들어 모든 접수·결정을 영속화. LLM 원본 응답도 보관.

**Consequences:**
- 감사·재현·정치적 정당화 가능
- 향후 결정 데이터셋으로 룰북 튜닝·평가 가능

---

## ADR-0001 — 풀스택을 Next.js + FastAPI + Postgres 로

**Date:** 2026-05-13
**Status:** Accepted

**Context:** 사용자가 "UI/UX부터 프론트엔드, 백엔드 코드 그리고 클라우드 엔지니어링과 AX, 마지막으로 Agent와 AI Engineering과 Data Scientist 등 모든 영역에서 완벽한 플랫폼"을 요구. Docker Compose 로 띄울 수 있어야 함.

**Decision:**
- Frontend: Next.js 14 (App Router) + TS + Tailwind
- Backend: FastAPI + SQLAlchemy 2 (async) + Pydantic v2
- DB: Postgres 16
- LLM: Anthropic Claude (Sonnet)

**Alternatives considered:**
- Remix / SvelteKit (프론트): 팀 합류 시 러닝커브, Next 보편성으로 기각
- Node 백엔드 (NestJS): Python LLM 생태계·향후 Data Scientist 영역 통합 손실로 기각
- SQLite: 멀티 인스턴스·동시성 한계로 기각

**Consequences:**
- 풀스택 합류 인원이 표준 도구로 즉시 작업 가능
- Python ↔ TS 두 언어 유지 비용 발생 (수용)
