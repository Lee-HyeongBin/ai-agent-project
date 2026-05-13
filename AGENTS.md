# AGENTS.md

본 파일은 다양한 AI 코딩 agent (Cursor, Claude Code, Aider 등) 가 동일하게 따르도록 만든 진입 문서다.

**CLAUDE.md 와 동일한 규칙을 따른다. 첫 작업 전에 반드시 `CLAUDE.md` 를 먼저 읽어라.**

핵심 요약:
- 이건 회사의 4 Pillar Agent 플랫폼 (Palantir AIP / MS Copilot Studio / Custom AWS·GCP / ixi-Enterprise) 라우팅 결정 시스템이다.
- 자동 개발이 아니라 **전략·기획 직무가 쓰는 접수 창구**.
- 결정에는 항상 **근거·대안·경고**가 따라붙고 DB에 영속화된다.
- 실제 `docker compose up`이 동작해야 한다. 문서가 아니라 코드 우선.
- 어느 플랫폼도 "절대 추천 안 됨" 으로 떨어지지 않게 — 정치 컨텍스트(`CLAUDE.md` §1).

시크릿 규칙 (2026-05-13 인시던트 후 강화):
- 실제 API 키는 `.env` 에만. `.env.example` 에는 placeholder (`sk-ant-your-key-here`) 만.
- commit 전 `pre-commit run --all-files` 자동 시크릿 스캔(`gitleaks`) 통과 필수.
- hook 우회 (`--no-verify`) 금지. false positive 면 사용자(전영환)에게 보고.

세부 가이드: `CLAUDE.md` / `docs/DECISIONS.md` / `docs/ROADMAP.md` / `SETUP.md` §3·§9.
