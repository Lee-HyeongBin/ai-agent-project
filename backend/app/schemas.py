from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

PlatformCode = Literal["palantir", "copilot", "custom", "ixi"]
SecurityLevel = Literal["low", "medium", "high"]
ScaleLevel = Literal["individual", "team", "department", "company"]
Frequency = Literal["realtime", "hourly", "daily", "weekly", "ondemand"]


class RouteRequest(BaseModel):
    purpose: str = Field(min_length=5, max_length=2000)
    domains: list[str] = Field(default_factory=list)
    systems: str | None = None
    frequency: Frequency | None = None
    security: SecurityLevel | None = None
    scale: ScaleLevel | None = None
    constraints: str | None = None


class TicketCreate(RouteRequest):
    title: str = Field(min_length=2, max_length=200)
    requester: str = Field(default="anonymous", max_length=120)


class PlatformScores(BaseModel):
    palantir: int
    copilot: int
    custom: int
    ixi: int


class RouteResult(BaseModel):
    primary: PlatformCode
    confidence: int
    verdict: str
    verdict_sub: str
    reasoning: str
    scores: PlatformScores
    rule_scores: PlatformScores
    stack: list[str]
    alternatives: list[str]
    warnings: list[str]
    model: str


class TicketOut(BaseModel):
    id: int
    title: str
    purpose: str
    domains: list[str]
    systems: str | None
    frequency: str | None
    security: str | None
    scale: str | None
    constraints: str | None
    requester: str
    created_at: datetime

    decision: RouteResult | None = None

    class Config:
        from_attributes = True


class PlatformMeta(BaseModel):
    code: PlatformCode
    name: str
    tag: str
    one_liner: str
    strengths: list[str]
    weaknesses: list[str]
    color: str
