# ROADMAP

본 프로젝트는 단일 세션에서 완성되지 않는다. 단계별 진행 상태를 여기에 기록한다.

## Phase 0 — Bootstrap (DONE 2026-05-13)
- [x] CLAUDE.md / AGENTS.md / docs/ 기초 작성
- [x] 메모리 (~/.claude/...) 컨텍스트 저장
- [x] 디렉토리 구조 + Docker Compose
- [x] Backend 골격 (FastAPI + Postgres + 라우팅 API)
- [x] Frontend 골격 (Next.js + 접수 폼 + 결과)
- [x] 한 사이클 end-to-end 동작 (`docker compose up`) — 3 서비스 healthy, 룰북 fallback 검증

## Phase 1 — MVP (next)
- [ ] 룰북 (PLATFORMS.md) 작성 + Rule Router 정교화
- [ ] LLM 응답 캐싱·재시도·타임아웃
- [ ] 이력 페이지 페이지네이션·필터
- [ ] 플랫폼 가이드 페이지 (사용자가 결정 근거를 사후 검토 가능하게)
- [ ] 기본 인증 (사내 SSO 연동 전, 사용자명 + 부서명 입력)

## Phase 2 — Beta
- [ ] 관리자 대시보드 (라우팅 분포·트렌드·플랫폼별 워크로드)
- [ ] 룰북 편집 UI (운영팀이 가중치 조절)
- [ ] Slack/Teams 알림 (라우팅 완료 시 담당 플랫폼 채널로)
- [ ] CSV/Excel export
- [ ] 결정 피드백 루프 (실제로 그 플랫폼에서 개발이 진행되었는지 추적)

## Phase 3 — Production
- [ ] 사내 SSO (Azure AD / Okta) 연동
- [ ] 감사 로그 분리 저장
- [ ] PII 마스킹 (입력 텍스트에 고객명/계좌번호 등)
- [ ] OpenTelemetry + Grafana
- [ ] 멀티-환경 (dev/stage/prod) 배포 파이프라인
- [ ] 백업·DR

## Phase 4 — 확장
- [ ] 룰북 자동 튜닝 (과거 결정 데이터로 가중치 학습)
- [ ] RAG 기반 플랫폼 가이드 (`pgvector`)
- [ ] 멀티 LLM 비교 (Claude / GPT / Gemini A-B 라우팅)

---

## 다음 세션을 위한 메모

**마지막 작업: 2026-05-13 (세션 #2).**

Phase 0 완전 종료. 3 서비스(db/backend/frontend) Docker 빌드·부팅 + end-to-end 사이클 + LLM 실제 호출까지 모두 통과.

검증 시나리오:
- (룰북) SAP/legacy/high → Custom 100점
- (룰북) Teams/M365/productivity → Copilot 100점
- (LLM) Foundry/Ontology/data → Palantir 100점, reasoning에 도메인 지식 + 문과용 괄호 풀이 자동 생성

Phase 1 진입 가능.

### 다음 세션 시작 시 체크리스트

1. **컨테이너 상태 확인**
   - `docker compose ps` — 3개 모두 healthy인지
   - 안 떠있으면 `docker compose up -d`
   - `.env` 변경했으면 `docker compose up -d backend` (restart는 env 재로드 안 함)
2. **이슈 트러블슈팅**
   - 한글 본문 curl 호출 시 `--data-binary @file.json` 사용 (직접 inline은 인코딩 깨짐)
   - LLM API 오류는 backend 로그(`docker compose logs backend`)에서 확인 — fallback 모드로 자동 전환되도록 구현됨

### Phase 1 즉시 진행 후보

- 룰북 가중치 튜닝 (실제 결정 케이스 모아 보면서 조정)
- 이력 페이지 페이지네이션·필터·검색
- 단위 테스트 (`backend/tests/test_rule_router.py`)
- 응답 캐싱 (동일 입력 → 동일 결과 캐시)
