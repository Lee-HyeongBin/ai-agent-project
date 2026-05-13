"""LLM 라우터 — 룰북 점수를 컨텍스트로 받아 자연어 근거를 만든다.

ANTHROPIC_API_KEY 미설정 시 fallback 모드로 동작 (룰북 점수 기반 결정론 응답).
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from anthropic import AsyncAnthropic, APIError

from app.config import get_settings
from app.schemas import PlatformScores, RouteRequest, RouteResult

logger = logging.getLogger(__name__)
settings = get_settings()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "router_system.md"


def _load_system_prompt() -> str:
    try:
        return _PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("router_system.md not found at %s", _PROMPT_PATH)
        return "당신은 Agent 플랫폼 라우팅 전문가입니다. 순수 JSON으로만 응답하세요."


def _build_user_prompt(req: RouteRequest, rule_scores: PlatformScores) -> str:
    parts = [
        f"[Agent 목적]\n{req.purpose}",
        f"[도메인] {', '.join(req.domains) if req.domains else '(미선택)'}",
        f"[연동 시스템] {req.systems or '(미입력)'}",
        f"[실행 빈도] {req.frequency or '(미선택)'}",
        f"[보안 민감도] {req.security or '(미선택)'}",
        f"[사용자 규모] {req.scale or '(미선택)'}",
        f"[추가 요구사항] {req.constraints or '(없음)'}",
        "",
        f"[룰북 사전 점수] {rule_scores.model_dump()}",
    ]
    return "\n".join(parts)


def _extract_json(text: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("응답에서 JSON 객체를 찾을 수 없습니다.")
    return json.loads(match.group(0))


def _normalize_primary(value: str) -> str:
    v = (value or "").lower().strip()
    for code in ("palantir", "copilot", "custom", "ixi"):
        if code in v:
            return code
    raise ValueError(f"알 수 없는 플랫폼 값: {value}")


def _fallback_result(
    req: RouteRequest, rule_scores: PlatformScores
) -> RouteResult:
    """LLM 키 없거나 호출 실패 시 룰북 점수만으로 결과 구성."""
    scores_dict = rule_scores.model_dump()
    primary, top = max(scores_dict.items(), key=lambda kv: kv[1])
    second_top = sorted(scores_dict.values(), reverse=True)[1]
    margin = top - second_top
    confidence = min(98, max(50, top - 5 + margin // 2))

    name_map = {
        "palantir": "Palantir AIP",
        "copilot": "MS Copilot Studio",
        "custom": "Custom Agent",
        "ixi": "ixi-Enterprise",
    }

    return RouteResult(
        primary=primary,  # type: ignore[arg-type]
        confidence=confidence,
        verdict=f"{name_map[primary]} 권장",
        verdict_sub="룰북 가중치 기반 자동 판정 (LLM 비활성)",
        reasoning=(
            f"LLM 라우터가 비활성화되어 룰북 점수만으로 판정했습니다. "
            f"가장 높은 점수는 {name_map[primary]} ({top}점)이며, "
            f"두 번째 후보와의 격차는 {margin}점입니다. "
            f"운영자가 ANTHROPIC_API_KEY를 설정하면 자연어 근거가 자동 생성됩니다."
        ),
        scores=rule_scores,
        rule_scores=rule_scores,
        stack=["룰북 기반 판정 — 스택 추천은 LLM 활성 시 제공"],
        alternatives=[
            f"{name_map[c]} ({s}점)"
            for c, s in sorted(scores_dict.items(), key=lambda kv: -kv[1])
            if c != primary
        ],
        warnings=["LLM 라우터 비활성 — 자연어 근거 없음. .env에 API 키 설정 권장."],
        model="rule-only",
    )


async def route(req: RouteRequest, rule_scores: PlatformScores) -> RouteResult:
    if not settings.llm_enabled:
        logger.info("LLM disabled — falling back to rule-only routing")
        return _fallback_result(req, rule_scores)

    client = AsyncAnthropic(
        api_key=settings.anthropic_api_key,
        timeout=settings.anthropic_timeout_s,
    )

    try:
        msg = await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=settings.anthropic_max_tokens,
            system=_load_system_prompt(),
            messages=[{"role": "user", "content": _build_user_prompt(req, rule_scores)}],
        )
    except APIError as e:
        logger.exception("Anthropic API error: %s", e)
        result = _fallback_result(req, rule_scores)
        result.warnings.insert(0, f"LLM 호출 실패 → 룰북 fallback. ({e.__class__.__name__})")
        return result

    raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")

    try:
        data = _extract_json(raw)
        primary = _normalize_primary(data.get("primary", ""))
    except (ValueError, json.JSONDecodeError) as e:
        logger.warning("LLM 응답 파싱 실패: %s — fallback", e)
        result = _fallback_result(req, rule_scores)
        result.warnings.insert(0, "LLM 응답 파싱 실패 → 룰북 fallback")
        return result

    scores_raw = data.get("scores") or rule_scores.model_dump()
    scores = PlatformScores(
        palantir=int(scores_raw.get("palantir", rule_scores.palantir)),
        copilot=int(scores_raw.get("copilot", rule_scores.copilot)),
        custom=int(scores_raw.get("custom", rule_scores.custom)),
        ixi=int(scores_raw.get("ixi", rule_scores.ixi)),
    )

    return RouteResult(
        primary=primary,  # type: ignore[arg-type]
        confidence=int(data.get("confidence", 70)),
        verdict=str(data.get("verdict", ""))[:200],
        verdict_sub=str(data.get("verdict_sub", ""))[:200],
        reasoning=str(data.get("reasoning", "")),
        scores=scores,
        rule_scores=rule_scores,
        stack=[str(s) for s in (data.get("stack") or [])][:6],
        alternatives=[str(a) for a in (data.get("alternatives") or [])][:5],
        warnings=[str(w) for w in (data.get("warnings") or [])][:5],
        model=settings.anthropic_model,
    )
