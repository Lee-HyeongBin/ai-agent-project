"""룰북 라우터 단위 테스트.

핵심 분기 + 모든 플랫폼이 어느 한 입력에선 1위가 되는지(정치 컨텍스트 — CLAUDE.md §1)를 확인.
가중치 튜닝 시 이 파일이 회귀 방지선.
"""
from __future__ import annotations

from app.schemas import PlatformScores, RouteRequest
from app.services.rule_router import compute_rule_scores, pick_primary


def _req(**kw) -> RouteRequest:
    """Minimum-valid RouteRequest with overrides."""
    defaults = dict(
        purpose="purpose placeholder 5+chars",
        domains=[],
        systems=None,
        frequency=None,
        security=None,
        scale=None,
        constraints=None,
    )
    defaults.update(kw)
    return RouteRequest(**defaults)


def test_default_request_returns_balanced_scores():
    """입력 정보가 거의 없으면 4 플랫폼 점수가 비슷해야 (룰북이 한쪽으로 쏠리지 않음)."""
    scores = compute_rule_scores(_req())
    vals = list(scores.model_dump().values())
    assert all(0 <= v <= 100 for v in vals)
    # 격차 30 이내 — 입력 없는 상황에서 한 플랫폼이 압도적이면 안 됨
    assert max(vals) - min(vals) <= 30


def test_ucube_legacy_high_security_picks_custom():
    """UCube/UCRM (사내 운영 시스템) + legacy + high security + private = Custom Agent 1순위."""
    scores = compute_rule_scores(
        _req(
            domains=["data", "legacy"],
            systems="UCube, UCRM, 경영지원시스템",
            frequency="hourly",
            security="high",
            scale="department",
            constraints="private network only, PII 포함",
        )
    )
    assert pick_primary(scores) == "custom"
    assert scores.custom >= scores.copilot + 30  # copilot 과 명확히 격차


def test_teams_sharepoint_productivity_picks_copilot():
    """MS Teams/SharePoint + productivity + low security + 전사 = Copilot 1순위."""
    scores = compute_rule_scores(
        _req(
            domains=["productivity"],
            systems="MS Teams, MS SharePoint, Outlook",
            frequency="ondemand",
            security="low",
            scale="company",
            constraints="M365 계정으로 SSO",
        )
    )
    assert pick_primary(scores) == "copilot"


def test_datalake_data_picks_palantir():
    """DataLake + data + KPI 모니터링 = Palantir 1순위."""
    scores = compute_rule_scores(
        _req(
            domains=["data"],
            systems="DataLake, KPI 대시보드",
            frequency="hourly",
            security="medium",
            scale="department",
            constraints="DataLake 데이터 직접 분석",
        )
    )
    assert pick_primary(scores) == "palantir"


def test_knowledgelake_workflow_picks_ixi():
    """KnowledgeLake + AI헬프데스크 + workflow + knowledge = ixi-Enterprise 1순위."""
    scores = compute_rule_scores(
        _req(
            domains=["workflow", "knowledge"],
            systems="KnowledgeLake, AI헬프데스크",
            frequency="ondemand",
            security="medium",
            scale="department",
            constraints="사내 환경 only",
        )
    )
    assert pick_primary(scores) == "ixi"


def test_scores_are_clamped_to_0_100():
    """극단적 입력에서도 점수는 [0, 100] 범위."""
    scores = compute_rule_scores(
        _req(
            domains=["data", "legacy", "workflow"],  # 여러 도메인 누적
            systems="UCube, UCRM, DataLake, KnowledgeLake, MS Teams, MS SharePoint, 경영지원시스템",
            security="high",
            scale="company",
            constraints="private vpc 온프레 격리 PII 기밀",
        )
    )
    for v in scores.model_dump().values():
        assert 0 <= v <= 100


def test_every_platform_can_win_in_some_scenario():
    """CLAUDE.md §1 정치 컨텍스트: 어느 플랫폼도 '절대 추천 안 됨' 이 되면 안 됨.

    각 플랫폼이 1위로 뽑히는 입력이 정의되어 있는지 메타 검증.
    """
    winners = set()
    for req_kwargs in [
        dict(domains=["legacy"], systems="UCube", security="high"),
        dict(domains=["productivity"], systems="MS Teams, MS SharePoint"),
        dict(domains=["data"], systems="DataLake"),
        dict(domains=["workflow", "knowledge"], systems="KnowledgeLake, AI헬프데스크"),
    ]:
        scores = compute_rule_scores(_req(**req_kwargs))
        winners.add(pick_primary(scores))
    assert winners == {"custom", "copilot", "palantir", "ixi"}


def test_pick_primary_handles_tie():
    """동점일 때도 PLATFORM_CODES 순서대로 결정론적으로 한 플랫폼이 뽑혀야 (테스트 안정성)."""
    equal = PlatformScores(palantir=70, copilot=70, custom=70, ixi=70)
    primary = pick_primary(equal)
    # max() 의 정의상 첫 번째 동점이 뽑힘 — palantir
    assert primary == "palantir"
