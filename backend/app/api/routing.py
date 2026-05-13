from fastapi import APIRouter

from app.schemas import PlatformMeta, RouteRequest, RouteResult
from app.services import llm_router, rule_router
from app.services.platforms import get_platforms

router = APIRouter()


@router.post("/route", response_model=RouteResult)
async def route(req: RouteRequest) -> RouteResult:
    rule_scores = rule_router.compute_rule_scores(req)
    return await llm_router.route(req, rule_scores)


@router.get("/platforms", response_model=list[PlatformMeta])
async def platforms() -> list[PlatformMeta]:
    return get_platforms()
