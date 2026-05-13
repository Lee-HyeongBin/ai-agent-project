from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import RoutingDecision, Ticket
from app.schemas import RouteResult, TicketCreate, TicketOut
from app.services import llm_router, rule_router

router = APIRouter()


def _to_route_result(d: RoutingDecision) -> RouteResult:
    return RouteResult(
        primary=d.primary,  # type: ignore[arg-type]
        confidence=d.confidence,
        verdict=d.verdict,
        verdict_sub=d.verdict_sub,
        reasoning=d.reasoning,
        scores=d.scores,  # type: ignore[arg-type]
        rule_scores=d.rule_scores,  # type: ignore[arg-type]
        stack=d.stack,
        alternatives=d.alternatives,
        warnings=d.warnings,
        model=d.model_used,
    )


def _to_ticket_out(t: Ticket) -> TicketOut:
    return TicketOut(
        id=t.id,
        title=t.title,
        purpose=t.purpose,
        domains=t.domains,
        systems=t.systems,
        frequency=t.frequency,
        security=t.security,
        scale=t.scale,
        constraints=t.constraints,
        requester=t.requester,
        created_at=t.created_at,
        decision=_to_route_result(t.decision) if t.decision else None,
    )


@router.post("", response_model=TicketOut, status_code=201)
async def create_ticket(
    payload: TicketCreate,
    session: AsyncSession = Depends(get_session),
) -> TicketOut:
    rule_scores = rule_router.compute_rule_scores(payload)
    result = await llm_router.route(payload, rule_scores)

    ticket = Ticket(
        title=payload.title,
        purpose=payload.purpose,
        domains=payload.domains,
        systems=payload.systems,
        frequency=payload.frequency,
        security=payload.security,
        scale=payload.scale,
        constraints=payload.constraints,
        requester=payload.requester or "anonymous",
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
    return _to_ticket_out(ticket)


@router.get("", response_model=list[TicketOut])
async def list_tickets(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    platform: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[TicketOut]:
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.decision))
        .order_by(Ticket.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if platform:
        stmt = stmt.join(Ticket.decision).where(RoutingDecision.primary == platform)

    res = await session.execute(stmt)
    return [_to_ticket_out(t) for t in res.scalars().all()]


@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: int,
    session: AsyncSession = Depends(get_session),
) -> TicketOut:
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.decision))
        .where(Ticket.id == ticket_id)
    )
    res = await session.execute(stmt)
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return _to_ticket_out(ticket)
