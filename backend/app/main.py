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

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ResolveIQ API",
    description="ResolveIQ — Explainable Customer Support Ticket Triage CRM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
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
