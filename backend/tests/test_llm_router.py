"""LLM 라우터 테스트 — Anthropic SDK 호출은 mock.

검증 목표:
- LLM 비활성(키 없음) → 룰북 fallback + warning 메시지
- LLM 성공 응답 → 정상 파싱
- LLM 응답 깨짐 → 룰북 fallback + parsing warning
- Rate limit / timeout / connection error → 각각 다른 warning 메시지로 fallback
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from anthropic import (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
)

from app.schemas import PlatformScores, RouteRequest
from app.services import llm_router


def _req() -> RouteRequest:
    return RouteRequest(
        purpose="UCube 일일 발주 데이터 이상 감지 알림",
        domains=["data", "legacy"],
        systems="UCube, UCRM",
        frequency="daily",
        security="medium",
        scale="department",
        constraints="private vpc",
    )


def _scores() -> PlatformScores:
    return PlatformScores(palantir=80, copilot=40, custom=85, ixi=50)


def _mock_anthropic_response(text: str):
    """Anthropic SDK 의 messages.create() 반환값 모양 흉내."""
    block = type("Block", (), {"type": "text", "text": text})()
    msg = type("Message", (), {"content": [block]})()
    return msg


def _make_client_factory(messages_create_mock: AsyncMock):
    """`AsyncAnthropic(...)` 호출이 mock client 를 반환하도록.

    mock client 의 .messages.create 가 messages_create_mock 으로 동작.
    """
    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = messages_create_mock
    return MagicMock(return_value=mock_client)


async def test_fallback_when_llm_disabled():
    """ANTHROPIC_API_KEY 비어있으면 LLM 호출 자체 안 함 — conftest 가 이미 빈 키 강제."""
    result = await llm_router.route(_req(), _scores())

    assert result.model == "rule-only"
    assert result.primary == "custom"  # rule scores 1위
    assert any("LLM" in w for w in result.warnings)


async def test_llm_success_parses_response(monkeypatch):
    monkeypatch.setattr(llm_router.settings, "anthropic_api_key", "sk-ant-fake")

    fake_resp = _mock_anthropic_response(
        """{
            "primary": "custom",
            "confidence": 92,
            "verdict": "Custom Agent 권장",
            "verdict_sub": "Legacy 시스템 깊은 통합 필요",
            "reasoning": "UCube/UCRM 통합과 PII 보안 요구로 Custom 적합.",
            "scores": {"palantir": 80, "copilot": 40, "custom": 95, "ixi": 50},
            "stack": ["LangGraph", "AWS Lambda"],
            "alternatives": ["Palantir AIP 일부 통합"],
            "warnings": ["개발 비용 검토 필요"]
        }"""
    )

    factory = _make_client_factory(AsyncMock(return_value=fake_resp))
    with patch.object(llm_router, "AsyncAnthropic", factory):
        result = await llm_router.route(_req(), _scores())

    assert result.primary == "custom"
    assert result.confidence == 92
    assert result.model == llm_router.settings.anthropic_model
    assert "개발 비용" in result.warnings[0]


async def test_llm_garbled_response_falls_back(monkeypatch):
    monkeypatch.setattr(llm_router.settings, "anthropic_api_key", "sk-ant-fake")
    fake_resp = _mock_anthropic_response("not a json response at all")

    factory = _make_client_factory(AsyncMock(return_value=fake_resp))
    with patch.object(llm_router, "AsyncAnthropic", factory):
        result = await llm_router.route(_req(), _scores())

    assert result.model == "rule-only"
    assert any("파싱" in w for w in result.warnings)


async def test_llm_rate_limit_falls_back(monkeypatch):
    monkeypatch.setattr(llm_router.settings, "anthropic_api_key", "sk-ant-fake")

    response_obj = httpx.Response(429, request=httpx.Request("POST", "https://x"))
    err = RateLimitError("rate limited", response=response_obj, body=None)

    factory = _make_client_factory(AsyncMock(side_effect=err))
    with patch.object(llm_router, "AsyncAnthropic", factory):
        result = await llm_router.route(_req(), _scores())

    assert result.model == "rule-only"
    assert any("rate limit" in w.lower() for w in result.warnings)


async def test_llm_timeout_falls_back(monkeypatch):
    monkeypatch.setattr(llm_router.settings, "anthropic_api_key", "sk-ant-fake")

    err = APITimeoutError(request=httpx.Request("POST", "https://x"))
    factory = _make_client_factory(AsyncMock(side_effect=err))
    with patch.object(llm_router, "AsyncAnthropic", factory):
        result = await llm_router.route(_req(), _scores())

    assert result.model == "rule-only"
    assert any("타임아웃" in w or "Timeout" in w for w in result.warnings)


async def test_llm_connection_error_falls_back(monkeypatch):
    monkeypatch.setattr(llm_router.settings, "anthropic_api_key", "sk-ant-fake")

    err = APIConnectionError(request=httpx.Request("POST", "https://x"))
    factory = _make_client_factory(AsyncMock(side_effect=err))
    with patch.object(llm_router, "AsyncAnthropic", factory):
        result = await llm_router.route(_req(), _scores())

    assert result.model == "rule-only"
    assert any("네트워크" in w or "Connection" in w for w in result.warnings)
