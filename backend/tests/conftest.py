"""Pytest fixtures — in-memory SQLite로 빠른 격리 테스트.

운영 환경은 Postgres + asyncpg, 테스트는 SQLite + aiosqlite. 모델 정의는 SQLAlchemy 2 비동기
스타일이라 둘 다 작동. JSON 컬럼은 SQLite도 지원하며 Pydantic 직렬화는 동일.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure `import app.*` 가능하도록 backend/ 를 sys.path 에 추가
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

# settings 가 lru_cache 로 캐시되기 전에 env 주입 (강제 덮어쓰기 — 컨테이너에 .env로
# 이미 키가 주입된 상태라도 테스트는 항상 LLM 비활성 fallback 모드여야 함)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# settings 객체는 module-level singleton — env 변경 후에도 이미 초기화된 인스턴스의
# 속성을 직접 비워서 import 순서 무관하게 LLM 비활성 보장.
from app.config import get_settings  # noqa: E402

_settings = get_settings()
_settings.anthropic_api_key = ""
_settings.database_url = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    """매 테스트마다 새 in-memory DB. shared cache 가 아닌 isolated session."""
    from app.db import Base
    from app import models  # noqa: F401  ensure models registered

    eng = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as s:
        yield s


@pytest_asyncio.fixture
async def client(engine):
    """FastAPI ASGI client — DB dependency 를 test engine 으로 override."""
    from app.db import get_session
    from app.main import app

    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def _override_session():
        async with SessionLocal() as s:
            yield s

    app.dependency_overrides[get_session] = _override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_ticket_payload() -> dict:
    return {
        "title": "UCube 발주 이상 탐지",
        "purpose": "UCube/UCRM 데이터에서 이상 패턴(가격 급변·중복 발주 등)을 탐지해 담당자에게 알림.",
        "domains": ["data", "legacy"],
        "systems": "UCube, UCRM, 경영지원시스템",
        "frequency": "hourly",
        "security": "high",
        "scale": "department",
        "constraints": "private network only, PII 포함",
        "requester": "tester",
    }


@pytest.fixture
def copilot_ticket_payload() -> dict:
    return {
        "title": "Teams 회의록 요약",
        "purpose": "MS Teams 회의 녹취록을 요약해 Outlook으로 전송하고 SharePoint에 저장.",
        "domains": ["productivity"],
        "systems": "MS Teams, MS SharePoint, Outlook",
        "frequency": "ondemand",
        "security": "low",
        "scale": "company",
        "constraints": "M365 계정으로 SSO",
        "requester": "tester",
    }
