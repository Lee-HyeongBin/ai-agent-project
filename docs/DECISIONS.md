# Architecture Decision Records

비가역적 / 영향이 큰 결정은 여기에 누적. 신규 결정 추가 시 위에 추가 (역시간순).

---

## ADR-0004 — 룰북 SYSTEM_AFFINITY 를 회사 실제 시스템 자산으로 한정

**Date:** 2026-05-14
**Status:** Accepted

**Context:** 룰북 초안의 시스템 키워드(SAP / Oracle / MES / SCADA / Foundry / KMS / 그룹웨어 등)는 일반적인 엔터프라이즈 어휘. 회사가 실제 운영하는 자산이 아닌 항목이 다수라, 사용자가 입력할 가능성이 낮고 룰북이 헛돌 가능성. 사용자(전영환)가 회사 실제 시스템 8종을 명시해 매핑을 다시 짜라고 요청.

**Decision:** `SYSTEM_AFFINITY` 키워드를 다음 사내 자산으로 갈아엎음.

| 시스템 | 가중치 우위 플랫폼 | 근거 |
|---|---|---|
| UCube (사내 ERP) | Custom | Legacy 사내 운영 시스템, private VPC 어댑터 필요 |
| UCRM (사내 CRM) | Custom + Palantir | Legacy + 고객 데이터(분석 자산) 양면성 |
| 경영지원시스템 | Custom + ixi | 결재·인사 워크플로우 — ixi 강점이나 데이터 연동 깊으면 Custom |
| DataLake | Palantir | 대용량 분석 원천 자산 |
| KnowledgeLake | ixi | 사내 지식 저장소 — RAG/KMS 핵심 |
| AI헬프데스크 | ixi (+ Copilot 약간) | 사내 챗봇/티켓팅 |
| MS Teams | Copilot | M365 협업 핵심 |
| MS SharePoint | Copilot | M365 문서 핵심 |

기존 외부 일반 명칭(SAP/Oracle/MES/SCADA/Foundry/Ontology/KMS/그룹웨어/결재/온보딩/매뉴얼)은 제거.

**Consequences:**
- 회사 실제 워크로드 입력에 룰북이 즉시 반응 (헛돌지 않음).
- `docs/PLATFORMS.md` 사내 자산 사전 섹션 추가, `backend/app/prompts/router_system.md` LLM 시스템 프롬프트도 동기화.
- 향후 사내 시스템 추가/변경 시 본 ADR을 갱신하거나 신규 ADR 발행.
- 룰북 가중치 자체(시스템당 +10~+18점)는 추정값. 실측 케이스 누적 후 Phase 1 후반에 튜닝 예정.

**Alternatives considered:**
- 사내 자산을 별도 `docs/SYSTEMS.yaml` 로 외부화 (Tier 2 작업으로 미룸 — 본 ADR은 우선 코드 동기화에 집중).

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
