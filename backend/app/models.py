from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    purpose: Mapped[str] = mapped_column(Text)
    domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    systems: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(40), nullable=True)
    security: Mapped[str | None] = mapped_column(String(20), nullable=True)
    scale: Mapped[str | None] = mapped_column(String(40), nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)

    requester: Mapped[str] = mapped_column(String(120), default="anonymous")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    decision: Mapped["RoutingDecision | None"] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", uselist=False
    )


class RoutingDecision(Base):
    __tablename__ = "routing_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"), unique=True
    )

    primary: Mapped[str] = mapped_column(String(20))  # palantir/copilot/custom/ixi
    confidence: Mapped[int] = mapped_column(Integer)
    verdict: Mapped[str] = mapped_column(String(200))
    verdict_sub: Mapped[str] = mapped_column(String(200))
    reasoning: Mapped[str] = mapped_column(Text)

    scores: Mapped[dict[str, int]] = mapped_column(JSON)
    rule_scores: Mapped[dict[str, int]] = mapped_column(JSON)
    stack: Mapped[list[str]] = mapped_column(JSON, default=list)
    alternatives: Mapped[list[str]] = mapped_column(JSON, default=list)
    warnings: Mapped[list[str]] = mapped_column(JSON, default=list)

    model_used: Mapped[str] = mapped_column(String(80))
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ticket: Mapped[Ticket] = relationship(back_populates="decision")
