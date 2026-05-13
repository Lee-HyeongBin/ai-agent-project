"""API end-to-end 테스트 — httpx.AsyncClient + FastAPI ASGI in-process.

LLM 키 없는 상태(fallback 모드)에서 핵심 경로를 검증.
"""
from __future__ import annotations

import pytest


async def test_healthz(client):
    res = await client.get("/healthz")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    # 테스트는 항상 LLM 비활성 — conftest 에서 ANTHROPIC_API_KEY=""
    assert body["llm_enabled"] is False


async def test_platforms_endpoint(client):
    res = await client.get("/api/platforms")
    assert res.status_code == 200
    platforms = res.json()
    codes = {p["code"] for p in platforms}
    assert codes == {"palantir", "copilot", "custom", "ixi"}
    for p in platforms:
        assert p["name"] and p["one_liner"]
        assert isinstance(p["strengths"], list) and len(p["strengths"]) > 0


async def test_route_endpoint_returns_decision(client, sample_ticket_payload):
    # /api/route 는 ticket 저장 없이 결과만
    body = {k: v for k, v in sample_ticket_payload.items() if k not in ("title", "requester")}
    res = await client.post("/api/route", json=body)
    assert res.status_code == 200
    data = res.json()
    assert data["primary"] in {"palantir", "copilot", "custom", "ixi"}
    assert 0 <= data["confidence"] <= 100
    assert "reasoning" in data
    assert data["model"] == "rule-only"  # fallback


async def test_create_ticket_then_list(client, sample_ticket_payload):
    res = await client.post("/api/tickets", json=sample_ticket_payload)
    assert res.status_code == 201
    created = res.json()
    assert created["id"] == 1
    assert created["title"] == sample_ticket_payload["title"]
    assert created["decision"]["primary"] == "custom"  # UCube/legacy/high

    # GET list 에서 보임
    list_res = await client.get("/api/tickets")
    assert list_res.status_code == 200
    tickets = list_res.json()
    assert len(tickets) == 1
    assert tickets[0]["id"] == 1

    # GET by id
    detail = await client.get("/api/tickets/1")
    assert detail.status_code == 200
    assert detail.json()["decision"]["primary"] == "custom"


async def test_filter_by_platform(client, sample_ticket_payload, copilot_ticket_payload):
    await client.post("/api/tickets", json=sample_ticket_payload)
    await client.post("/api/tickets", json=copilot_ticket_payload)

    custom_only = await client.get("/api/tickets?platform=custom")
    assert custom_only.status_code == 200
    rows = custom_only.json()
    assert all(t["decision"]["primary"] == "custom" for t in rows)
    assert len(rows) == 1

    copilot_only = await client.get("/api/tickets?platform=copilot")
    rows = copilot_only.json()
    assert all(t["decision"]["primary"] == "copilot" for t in rows)
    assert len(rows) == 1


async def test_get_nonexistent_ticket_returns_404(client):
    res = await client.get("/api/tickets/9999")
    assert res.status_code == 404


async def test_route_rejects_short_purpose(client):
    res = await client.post(
        "/api/route",
        json={
            "purpose": "x",  # < 5 chars
            "domains": [],
        },
    )
    assert res.status_code == 422  # pydantic validation error


async def test_create_ticket_rejects_missing_title(client):
    res = await client.post(
        "/api/tickets",
        json={
            "purpose": "long enough purpose string for validation pass",
            "domains": [],
        },
    )
    assert res.status_code == 422
