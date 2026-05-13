import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routing as routing_api
from app.api import tickets as tickets_api
from app.config import get_settings
from app.db import init_db

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("agentplatform")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema…")
    await init_db()
    logger.info("LLM enabled: %s (model=%s)", settings.llm_enabled, settings.anthropic_model)
    yield


app = FastAPI(
    title="AgentPlatform API",
    description="4 Pillar Agent 플랫폼 라우팅 결정 시스템",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routing_api.router, prefix="/api", tags=["routing"])
app.include_router(tickets_api.router, prefix="/api/tickets", tags=["tickets"])


@app.get("/healthz", tags=["meta"])
async def health() -> dict:
    return {
        "status": "ok",
        "llm_enabled": settings.llm_enabled,
        "model": settings.anthropic_model if settings.llm_enabled else None,
    }


@app.get("/", tags=["meta"])
async def root() -> dict:
    return {
        "name": "AgentPlatform API",
        "version": "0.1.0",
        "docs": "/docs",
    }
