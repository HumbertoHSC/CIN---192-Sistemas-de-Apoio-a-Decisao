"""PROMETHEE II — ranking completo pelo fluxo líquido φ.

No PROMETHEE II todas as alternativas são comparáveis: a ordem é dada
diretamente pelo fluxo líquido ``φ(a) = φ⁺(a) − φ⁻(a)``, do maior para
o menor. Empates (mesmo φ) recebem a mesma posição.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .flows import CriterionSpec, FlowResult, compute_flows


@dataclass(frozen=True)
class AlternativeScore:
    """Pontuação de uma alternativa no ranking final."""

    name: str
    phi_plus: float
    phi_minus: float
    phi_net: float
    rank: int


@dataclass(frozen=True)
class PrometheeIIResult:
    """Saída completa do PROMETHEE II."""

    scores: list[AlternativeScore]   # ordenado por rank (1 = melhor)
    flows: FlowResult


def rank(
    matrix: np.ndarray,
    criteria: list[CriterionSpec],
    alternative_names: list[str],
) -> PrometheeIIResult:
    """Executa o PROMETHEE II e devolve o ranking completo."""
    n = np.asarray(matrix, dtype=float).shape[0]
    if len(alternative_names) != n:
        raise ValueError("Nº de nomes difere do nº de alternativas.")

    flows = compute_flows(matrix, criteria)
    phi = flows.phi_net

    # ordem decrescente de φ; ranks com empate compartilhado
    order = np.argsort(-phi, kind="stable")
    ranks = np.empty(n, dtype=int)
    current_rank = 0
    prev_value: float | None = None
    for position, idx in enumerate(order):
        value = float(phi[idx])
        if prev_value is None or not np.isclose(value, prev_value):
            current_rank = position + 1
            prev_value = value
        ranks[idx] = current_rank

    scores = [
        AlternativeScore(
            name=alternative_names[i],
            phi_plus=float(flows.phi_plus[i]),
            phi_minus=float(flows.phi_minus[i]),
            phi_net=float(flows.phi_net[i]),
            rank=int(ranks[i]),
        )
        for i in order
    ]

    return PrometheeIIResult(scores=scores, flows=flows)
