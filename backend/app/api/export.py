"""Exportação dos resultados em CSV e PDF."""

from __future__ import annotations

import csv
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Paragraph,
)

from ..schemas import SolveResponse

_HEADERS = ["Rank", "Alternativa", "Phi+", "Phi-", "Phi (líquido)"]


def _rows(result: SolveResponse) -> list[list[str]]:
    ordered = sorted(result.scores, key=lambda s: s.rank)
    return [
        [str(s.rank), s.name, f"{s.phi_plus:.4f}", f"{s.phi_minus:.4f}", f"{s.phi_net:.4f}"]
        for s in ordered
    ]


def to_csv(result: SolveResponse) -> bytes:
    """Gera um CSV com o ranking completo."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_HEADERS)
    writer.writerows(_rows(result))
    return buffer.getvalue().encode("utf-8-sig")  # BOM p/ Excel abrir acentos


def to_pdf(result: SolveResponse) -> bytes:
    """Gera um PDF com o ranking PROMETHEE II."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Resultado PROMETHEE II")
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("Resultado — PROMETHEE II", styles["Title"]),
        Spacer(1, 12),
    ]
    if result.gaia is not None:
        elements.append(
            Paragraph(
                f"Qualidade do plano GAIA (δ): {result.gaia.quality:.2%}", styles["Normal"]
            )
        )
        elements.append(Spacer(1, 12))

    data = [_HEADERS] + _rows(result)
    table = Table(data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()
