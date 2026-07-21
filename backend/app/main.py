from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app import models
from backend.app.database import Base, engine
from backend.app.routes import tickets

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_FRONTEND_URL = "http://localhost:5173"
FRONTEND_URL = os.getenv("FRONTEND_URL", "").strip() or DEFAULT_FRONTEND_URL
ALLOWED_ORIGINS = list(
    dict.fromkeys(
        origin
        for origin in (
            FRONTEND_URL,
            DEFAULT_FRONTEND_URL,
            "http://127.0.0.1:5173",
        )
        if origin
    )
)

# FRONTEND_URL supplies the exact production origin; this restricted regex
# supports only ResolveIQ previews under this project's Vercel scope.
VERCEL_PREVIEW_ORIGIN_REGEX = (
    r"^https://resolve-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    r"-yogesh10023-7158s-projects\.vercel\.app$"
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ResolveIQ API",
    description="ResolveIQ — Explainable Customer Support Ticket Triage CRM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=VERCEL_PREVIEW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)


class RootResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/", response_model=RootResponse)
def root() -> RootResponse:
    return RootResponse(message="Welcome to ResolveIQ API")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="healthy", service="ResolveIQ API")
