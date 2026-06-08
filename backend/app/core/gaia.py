"""Plano GAIA — visualização geométrica do problema de decisão.

O GAIA (Geometrical Analysis for Interactive Aid) projeta a matriz de
fluxos líquidos unicritério ``Φ (n alternativas × m critérios)`` num
plano 2D via PCA (decomposição em valores singulares):

* cada **alternativa** vira um ponto;
* cada **critério** vira um eixo (vetor);
* o **eixo de decisão π** é a projeção do vetor de pesos — aponta para
  o "melhor compromisso" segundo os pesos escolhidos.

A qualidade ``δ`` indica quanto da informação (variância) é preservada
no plano; valores acima de ~0.6 já são considerados confiáveis.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class GaiaResult:
    """Coordenadas do plano GAIA."""

    alternatives: np.ndarray  # (n, 2) pontos das alternativas
    criteria: np.ndarray      # (m, 2) vetores dos critérios
    decision_axis: np.ndarray  # (2,)  eixo de decisão π
    quality: float            # δ ∈ [0, 1] qualidade da representação


def compute_gaia(
    unicriterion_flows: np.ndarray,
    weights: np.ndarray,
) -> GaiaResult:
    """Projeta os fluxos unicritério no plano GAIA.

    Parameters
    ----------
    unicriterion_flows : np.ndarray
        Matriz ``(n, m)`` de fluxos líquidos por critério (de ``FlowResult``).
    weights : np.ndarray
        Pesos normalizados ``(m,)``.
    """
    phi = np.asarray(unicriterion_flows, dtype=float)
    n, m = phi.shape
    if m < 2:
        raise ValueError("O plano GAIA requer ao menos 2 critérios.")

    # As colunas de Φ já têm média ~0; centramos por garantia.
    centered = phi - phi.mean(axis=0, keepdims=True)

    # PCA via SVD: linhas de Vt são as componentes principais.
    _, singular, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt[:2]  # (2, m) — dois primeiros eixos principais

    alternatives = centered @ components.T          # (n, 2)
    criteria = components.T                          # (m, 2): projeção de cada e_k
    decision_axis = np.asarray(weights, dtype=float) @ components.T  # (2,)

    variance = singular ** 2
    total = variance.sum()
    quality = float(variance[:2].sum() / total) if total > 0 else 0.0

    return GaiaResult(
        alternatives=alternatives,
        criteria=criteria,
        decision_axis=decision_axis,
        quality=quality,
    )
