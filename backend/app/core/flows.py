"""Cálculo dos fluxos de superação (outranking flows) do PROMETHEE.

Etapas (Brans & Vincke, 1986):

1. Para cada par de alternativas (a, b) e cada critério k, calcula-se o
   grau de preferência ``P_k(a, b)`` via função de preferência.
2. Índice de preferência agregado ``π(a, b) = Σ_k w_k · P_k(a, b)``
   (pesos normalizados para somar 1).
3. Fluxo de saída  ``φ⁺(a) = 1/(n-1) · Σ_b π(a, b)``.
4. Fluxo de entrada ``φ⁻(a) = 1/(n-1) · Σ_b π(b, a)``.
5. Fluxo líquido   ``φ(a)  = φ⁺(a) − φ⁻(a)``  (base do PROMETHEE II).

Também expõe os fluxos líquidos *unicritério* usados pelo plano GAIA.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .preference_functions import PreferenceType, apply_preference


@dataclass(frozen=True)
class CriterionSpec:
    """Configuração de um critério."""

    name: str
    weight: float
    maximize: bool = True
    preference: PreferenceType = PreferenceType.USUAL
    q: float | None = None
    p: float | None = None
    s: float | None = None


@dataclass(frozen=True)
class FlowResult:
    """Resultado completo do cálculo de fluxos."""

    phi_plus: np.ndarray          # (n,)  fluxo positivo
    phi_minus: np.ndarray         # (n,)  fluxo negativo
    phi_net: np.ndarray           # (n,)  fluxo líquido
    preference_index: np.ndarray  # (n, n) índice agregado π
    unicriterion_flows: np.ndarray  # (n, m) φ líquido por critério (GAIA)
    weights: np.ndarray           # (m,)  pesos normalizados


def _pairwise_diff(column: np.ndarray) -> np.ndarray:
    """Matriz (n, n) de diferenças d[i, j] = column[i] - column[j]."""
    return column[:, None] - column[None, :]


def compute_flows(
    matrix: np.ndarray,
    criteria: list[CriterionSpec],
) -> FlowResult:
    """Calcula todos os fluxos a partir da matriz de avaliação.

    Parameters
    ----------
    matrix : np.ndarray
        Matriz de avaliação ``(n alternativas, m critérios)``.
    criteria : list[CriterionSpec]
        Um spec por coluna de ``matrix``.

    Returns
    -------
    FlowResult
    """
    matrix = np.asarray(matrix, dtype=float)
    n, m = matrix.shape
    if n < 2:
        raise ValueError("São necessárias ao menos 2 alternativas.")
    if m != len(criteria):
        raise ValueError(
            f"Nº de critérios ({len(criteria)}) difere das colunas da matriz ({m})."
        )

    weights = np.array([c.weight for c in criteria], dtype=float)
    if np.any(weights < 0):
        raise ValueError("Pesos não podem ser negativos.")
    total = weights.sum()
    if total <= 0:
        raise ValueError("A soma dos pesos deve ser positiva.")
    weights = weights / total

    preference_index = np.zeros((n, n), dtype=float)
    unicriterion_flows = np.zeros((n, m), dtype=float)

    for k, spec in enumerate(criteria):
        column = matrix[:, k]
        diff = _pairwise_diff(column)
        if not spec.maximize:
            diff = -diff  # critério de minimização → inverte a orientação

        p_k = apply_preference(diff, spec.preference, q=spec.q, p=spec.p, s=spec.s)
        np.fill_diagonal(p_k, 0.0)

        preference_index += weights[k] * p_k

        # fluxo líquido unicritério (normalizado por n-1) para o GAIA
        uni = (p_k.sum(axis=1) - p_k.sum(axis=0)) / (n - 1)
        unicriterion_flows[:, k] = uni

    phi_plus = preference_index.sum(axis=1) / (n - 1)
    phi_minus = preference_index.sum(axis=0) / (n - 1)
    phi_net = phi_plus - phi_minus

    return FlowResult(
        phi_plus=phi_plus,
        phi_minus=phi_minus,
        phi_net=phi_net,
        preference_index=preference_index,
        unicriterion_flows=unicriterion_flows,
        weights=weights,
    )
