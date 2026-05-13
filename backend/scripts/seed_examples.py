"""사내 시스템 기반 예시 ticket 5건 시드.

기존 ticket·decision 을 모두 비우고, 4 플랫폼이 각각 winner 인 케이스를
구성해 demo·시연·라우팅 검증에 사용한다.

실행 (호스트):
    docker exec agentplatform-backend python -m scripts.seed_examples

또는 docker compose backend 컨테이너 안에서:
    python -m scripts.seed_examples
"""
from __future__ import annotations

import asyncio
import sys

from sqlalchemy import delete

from app.db import SessionLocal, init_db
from app.models import RoutingDecision, Ticket
from app.schemas import TicketCreate
from app.services import llm_router, rule_router


SEED_TICKETS: list[dict] = [
    {
        "title": "UCube 발주 이상 탐지",
        "purpose": "매일 새벽 UCube 발주 데이터를 받아 가격 급변·중복 발주·이상 수량 패턴을 탐지하고 구매팀 담당자에게 Teams 알림을 보냅니다. PII가 일부 포함되어 사내 VPC 내부에서만 실행되어야 합니다.",
        "domains": ["data", "legacy"],
        "systems": "UCube, UCRM, 경영지원시스템",
        "frequency": "daily",
        "security": "high",
        "scale": "department",
        "constraints": "private network only, PII 포함",
        "requester": "구매혁신팀 / 김 책임",
    },
    {
        "title": "DataLake KPI 일간 분석 + 코멘트",
        "purpose": "DataLake 의 일일 매출·재고·생산 KPI 를 분석해 전일 대비 이상 변동 항목에 자연어 코멘트를 자동 작성하고 경영지원시스템 일일보고에 첨부합니다.",
        "domains": ["data"],
        "systems": "DataLake, 경영지원시스템",
        "frequency": "daily",
        "security": "medium",
        "scale": "company",
        "constraints": "DataLake 직접 분석, 외부 이동 최소화",
        "requester": "데이터분석팀 / 이 매니저",
    },
    {
        "title": "Teams 회의록 요약 + SharePoint 보관",
        "purpose": "MS Teams 회의 종료 시 녹취록을 받아 요약본을 작성해 참석자에게 Outlook 으로 전송하고, MS SharePoint 회의록 폴더에 자동 보관합니다.",
        "domains": ["productivity"],
        "systems": "MS Teams, MS SharePoint, Outlook",
        "frequency": "ondemand",
        "security": "low",
        "scale": "company",
        "constraints": "M365 계정 SSO",
        "requester": "전사 / IT지원팀",
    },
    {
        "title": "KnowledgeLake 사내 규정 Q&A 챗봇",
        "purpose": "KnowledgeLake 에 저장된 사내 규정·매뉴얼·복리후생 문서를 RAG 로 검색해 임직원의 질문에 답변하는 챗봇. AI헬프데스크 1차 응대 채널로 연결합니다.",
        "domains": ["knowledge", "workflow"],
        "systems": "KnowledgeLake, AI헬프데스크",
        "frequency": "ondemand",
        "security": "medium",
        "scale": "company",
        "constraints": "사내 환경 only, 외부 노출 금지",
        "requester": "Personal Agent 기술팀 / 전영환",
    },
    {
        "title": "UCRM 고객 이탈 위험 스코어링",
        "purpose": "UCRM 의 고객 활동·청구·문의 이력을 종합해 이탈 위험 점수를 산출하고, 영업 담당자에게 상위 위험 고객 리스트를 매주 월요일 아침 제공합니다. 이탈 사유 자연어 요약 포함.",
        "domains": ["data", "legacy"],
        "systems": "UCRM, DataLake, MS Teams",
        "frequency": "weekly",
        "security": "high",
        "scale": "department",
        "constraints": "고객 식별정보 마스킹, 영업본부 외 접근 금지",
        "requester": "고객전략팀 / 박 책임",
    },
]


async def _wipe_existing(session) -> tuple[int, int]:
    # FK CASCADE on routing_decisions(ticket_id) → ticket 삭제 시 자동 정리.
    # 그래도 명시적으로 둘 다 삭제.
    d = await session.execute(delete(RoutingDecision))
    t = await session.execute(delete(Ticket))
    await session.commit()
    return t.rowcount or 0, d.rowcount or 0


async def _create(session, payload: dict) -> int:
    req = TicketCreate(**payload)
    rule_scores = rule_router.compute_rule_scores(req)
    result = await llm_router.route(req, rule_scores)

    ticket = Ticket(
        title=req.title,
        purpose=req.purpose,
        domains=req.domains,
        systems=req.systems,
        frequency=req.frequency,
        security=req.security,
        scale=req.scale,
        constraints=req.constraints,
        requester=req.requester or "anonymous",
    )
    ticket.decision = RoutingDecision(
        primary=result.primary,
        confidence=result.confidence,
        verdict=result.verdict,
        verdict_sub=result.verdict_sub,
        reasoning=result.reasoning,
        scores=result.scores.model_dump(),
        rule_scores=result.rule_scores.model_dump(),
        stack=result.stack,
        alternatives=result.alternatives,
        warnings=result.warnings,
        model_used=result.model,
    )
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket, attribute_names=["decision"])
    return ticket.id, result.primary, result.confidence


async def main() -> None:
    await init_db()
    async with SessionLocal() as session:
        wiped_t, wiped_d = await _wipe_existing(session)
        print(f"[wipe] tickets={wiped_t}, decisions={wiped_d}")

        for p in SEED_TICKETS:
            tid, primary, conf = await _create(session, p)
            print(f"[seed] #{tid} '{p['title']}' → {primary} ({conf}%)")

    print(f"\nDone. {len(SEED_TICKETS)} seed ticket(s) created.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(1)
