"""Rotas da API REST."""

from __future__ import annotations

from fastapi import APIRouter, Response

from ..schemas import SolveRequest, SolveResponse
from . import export, service

router = APIRouter(prefix="/api", tags=["promethee"])


@router.post("/solve", response_model=SolveResponse, summary="Resolver via PROMETHEE II")
def solve(request: SolveRequest) -> SolveResponse:
    """Executa o PROMETHEE II e devolve ranking, fluxos e plano GAIA."""
    return service.solve(request)


@router.post("/export/csv", summary="Exportar ranking em CSV")
def export_csv(request: SolveRequest) -> Response:
    result = service.solve(request)
    content = export.to_csv(result)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=promethee_ii.csv"},
    )


@router.post("/export/pdf", summary="Exportar ranking em PDF")
def export_pdf(request: SolveRequest) -> Response:
    result = service.solve(request)
    content = export.to_pdf(result)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=promethee_ii.pdf"},
    )
