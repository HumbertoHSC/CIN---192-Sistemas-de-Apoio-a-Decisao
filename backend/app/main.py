"""Aplicação FastAPI — PROMETHEE II + GAIA.

Documentação interativa (Swagger/OpenAPI) disponível em ``/docs``.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router

app = FastAPI(
    title="PROMETHEE II API",
    description=(
        "Apoio à decisão multicritério (MCDM) com o método PROMETHEE II "
        "e visualização GAIA. Baseado em Brans & Vincke (1986)."
    ),
    version="0.1.0",
)

# CORS — origens de produção via env (ex.: a URL do frontend na Vercel).
# Um CORS_ORIGINS vazio/ausente NÃO deve zerar as origens permitidas, por
# isso só usamos o env quando ele traz valores reais.
_env = os.getenv("CORS_ORIGINS", "")
_origins = [o.strip() for o in _env.split(",") if o.strip()]

# Em desenvolvimento, libera localhost/127.0.0.1 em qualquer porta.
_dev_origin_regex = r"https?://(localhost|127\.0\.0\.1)(:\d+)?"

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=_dev_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health", tags=["meta"], summary="Healthcheck")
def health() -> dict[str, str]:
    return {"status": "ok"}
