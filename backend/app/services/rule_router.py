"""결정론적 룰북 기반 가중치 라우터.

docs/PLATFORMS.md 의 룰북을 코드로 옮긴 것. 룰북이 바뀌면 본 모듈도 같이 갱신.
"""
from __future__ import annotations

from app.schemas import PlatformScores, RouteRequest

PLATFORM_CODES = ("palantir", "copilot", "custom", "ixi")

# 도메인 토큰 → 플랫폼별 가산점
DOMAIN_AFFINITY: dict[str, dict[str, int]] = {
    "data": {"palantir": 18, "copilot": -4, "custom": 4, "ixi": -4},
    "productivity": {"palantir": -6, "copilot": 22, "custom": -2, "ixi": 4},
    "legacy": {"palantir": 0, "copilot": -10, "custom": 22, "ixi": -2},
    "workflow": {"palantir": 0, "copilot": 8, "custom": 4, "ixi": 18},
    "knowledge": {"palantir": -2, "copilot": 6, "custom": -2, "ixi": 20},
    "crossplatform": {"palantir": 6, "copilot": 8, "custom": 8, "ixi": 0},
}

# 시스템 키워드 → 가산점 (소문자 매칭).
# 회사 실제 시스템 매핑 — 변경 시 docs/PLATFORMS.md, docs/DECISIONS.md(ADR-0003) 함께 갱신.
SYSTEM_AFFINITY: dict[str, dict[str, int]] = {
    # ── 사내 운영/Legacy ERP·CRM → Custom Agent (private VPC + 깊은 통합)
    "ucube":            {"custom": 16, "palantir": 4},
    "ucrm":             {"custom": 14, "palantir": 6},
    "경영지원시스템":   {"custom": 10, "ixi": 8},
    "경영지원":         {"custom": 10, "ixi": 8},

    # ── 데이터·KPI 분석 자산 → Palantir AIP
    "datalake":         {"palantir": 18, "custom": 4},
    "data lake":        {"palantir": 18, "custom": 4},
    "데이터레이크":     {"palantir": 18, "custom": 4},
    "kpi":              {"palantir": 10},

    # ── 사내 지식·문서 RAG → ixi-Enterprise
    "knowledgelake":    {"ixi": 18, "custom": 2},
    "knowledge lake":   {"ixi": 18, "custom": 2},
    "지식레이크":       {"ixi": 18, "custom": 2},
    "kms":              {"ixi": 14},

    # ── 사내 챗봇/티켓팅 → ixi(지식·워크플로우) + Copilot 약간(Teams 연동 시)
    "ai헬프데스크":     {"ixi": 14, "copilot": 4},
    "ai 헬프데스크":    {"ixi": 14, "copilot": 4},
    "헬프데스크":       {"ixi": 12},
    "ai helpdesk":      {"ixi": 14, "copilot": 4},
    "helpdesk":         {"ixi": 12},

    # ── M365 → Copilot Studio
    "ms teams":         {"copilot": 14},
    "teams":            {"copilot": 14},
    "ms sharepoint":    {"copilot": 12},
    "sharepoint":       {"copilot": 12},
    "outlook":          {"copilot": 14},
    "onedrive":         {"copilot": 10},
    "m365":             {"copilot": 12},
    "office":           {"copilot": 8},
}

FREQUENCY_FIT: dict[str, dict[str, int]] = {
    "realtime": {"palantir": 8, "custom": 6, "copilot": -4, "ixi": -6},
    "hourly":   {"palantir": 8, "custom": 4, "copilot": 0,  "ixi": -2},
    "daily":    {"palantir": 6, "custom": 4, "copilot": 2,  "ixi": 2},
    "weekly":   {"palantir": 2, "custom": 2, "copilot": 4,  "ixi": 4},
    "ondemand": {"palantir": -2,"custom": 0, "copilot": 10, "ixi": 10},
}

SECURITY_FIT: dict[str, dict[str, int]] = {
    "low":    {"copilot": 4, "palantir": 2, "ixi": 2, "custom": -2},
    "medium": {"palantir": 4, "copilot": 2, "ixi": 4, "custom": 4},
    "high":   {"custom": 14, "ixi": 8, "palantir": 4, "copilot": -10},
}

SCALE_FIT: dict[str, dict[str, int]] = {
    "individual": {"copilot": 6, "ixi": 4, "palantir": -4, "custom": -6},
    "team":       {"copilot": 6, "ixi": 6, "palantir": 2, "custom": 0},
    "department": {"palantir": 8, "ixi": 8, "copilot": 6, "custom": 4},
    "company":    {"copilot": 12, "palantir": 8, "ixi": 6, "custom": 2},
}

# Constraints 키워드 기반 보너스/페널티
CONSTRAINT_HINTS: dict[str, dict[str, int]] = {
    "private": {"custom": 12, "copilot": -10},
    "vpc":     {"custom": 10},
    "온프레": {"custom": 10, "copilot": -8},
    "격리":   {"custom": 10, "copilot": -6},
    "m365 계정": {"copilot": 12},
    "azure ad": {"copilot": 8},
    "pii":    {"custom": 8, "copilot": -6},
    "기밀":   {"custom": 8, "copilot": -6},
}


def _clamp(v: int) -> int:
    return max(0, min(100, v))


def _scale_score(raw: dict[str, int]) -> dict[str, int]:
    return {k: _clamp(v) for k, v in raw.items()}


def compute_rule_scores(req: RouteRequest) -> PlatformScores:
    score = {p: 50 for p in PLATFORM_CODES}

    for d in req.domains:
        d_lower = d.lower()
        weights = DOMAIN_AFFINITY.get(d_lower)
        if not weights:
            continue
        for p, w in weights.items():
            score[p] += w

    systems_l = (req.systems or "").lower()
    for kw, weights in SYSTEM_AFFINITY.items():
        if kw in systems_l:
            for p, w in weights.items():
                score[p] += w

    if req.frequency and (fits := FREQUENCY_FIT.get(req.frequency)):
        for p, w in fits.items():
            score[p] += w

    if req.security and (fits := SECURITY_FIT.get(req.security)):
        for p, w in fits.items():
            score[p] += w

    if req.scale and (fits := SCALE_FIT.get(req.scale)):
        for p, w in fits.items():
            score[p] += w

    cons_l = (req.constraints or "").lower()
    for kw, weights in CONSTRAINT_HINTS.items():
        if kw in cons_l:
            for p, w in weights.items():
                score[p] += w

    return PlatformScores(**_scale_score(score))


def pick_primary(scores: PlatformScores) -> str:
    return max(scores.model_dump().items(), key=lambda kv: kv[1])[0]
