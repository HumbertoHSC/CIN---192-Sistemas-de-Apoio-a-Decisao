"""Funções de preferência (critérios generalizados) do PROMETHEE.

Referência: Brans, J.P. & Vincke, Ph. (1986). "A Preference Ranking
Organisation Method (The PROMETHEE Method for Multiple Criteria
Decision-Making)". Management Science, 31(6).

Cada função recebe a diferença ``d = g(a) - g(b)`` (já orientada para
maximização) e devolve o grau de preferência ``P(d) ∈ [0, 1]``.
Por convenção ``P(d) = 0`` para ``d <= 0``.

As implementações são vetorizadas: ``d`` pode ser um escalar ou um
``np.ndarray`` de qualquer forma.
"""

from __future__ import annotations

from enum import Enum

import numpy as np


class PreferenceType(str, Enum):
    """Os seis tipos de critério generalizado do artigo original."""

    USUAL = "usual"          # Tipo I
    U_SHAPE = "u_shape"      # Tipo II  (quase-critério) — usa q
    V_SHAPE = "v_shape"      # Tipo III (pseudo-critério) — usa p
    LEVEL = "level"          # Tipo IV  — usa q e p
    LINEAR = "linear"        # Tipo V   (com indiferença) — usa q e p
    GAUSSIAN = "gaussian"    # Tipo VI  — usa s (sigma)


def usual(d: np.ndarray) -> np.ndarray:
    """Tipo I — qualquer desvio positivo gera preferência total."""
    return np.where(d > 0, 1.0, 0.0)


def u_shape(d: np.ndarray, q: float) -> np.ndarray:
    """Tipo II — preferência total apenas acima do limiar de indiferença q."""
    return np.where(d > q, 1.0, 0.0)


def v_shape(d: np.ndarray, p: float) -> np.ndarray:
    """Tipo III — preferência cresce linearmente até o limiar p."""
    if p <= 0:
        raise ValueError("v_shape requer p > 0")
    out = np.clip(d / p, 0.0, 1.0)
    return np.where(d > 0, out, 0.0)


def level(d: np.ndarray, q: float, p: float) -> np.ndarray:
    """Tipo IV — patamar: 0, depois 0.5 entre q e p, depois 1."""
    if p < q:
        raise ValueError("level requer p >= q")
    return np.where(d > p, 1.0, np.where(d > q, 0.5, 0.0))


def linear(d: np.ndarray, q: float, p: float) -> np.ndarray:
    """Tipo V — linear com zona de indiferença q e de preferência p."""
    if p <= q:
        raise ValueError("linear requer p > q")
    out = (d - q) / (p - q)
    out = np.clip(out, 0.0, 1.0)
    return np.where(d > q, out, 0.0)


def gaussian(d: np.ndarray, s: float) -> np.ndarray:
    """Tipo VI — gaussiana, sem descontinuidades, parametrizada por s."""
    if s <= 0:
        raise ValueError("gaussian requer s > 0")
    out = 1.0 - np.exp(-(d ** 2) / (2.0 * s ** 2))
    return np.where(d > 0, out, 0.0)


def apply_preference(
    d: np.ndarray,
    ptype: PreferenceType,
    q: float | None = None,
    p: float | None = None,
    s: float | None = None,
) -> np.ndarray:
    """Despacha para a função de preferência correta.

    Parameters
    ----------
    d : np.ndarray
        Diferenças orientadas para maximização.
    ptype : PreferenceType
        Tipo de critério generalizado.
    q, p, s : float, opcional
        Limiares exigidos conforme o tipo (ver tabela do artigo).
    """
    d = np.asarray(d, dtype=float)

    if ptype == PreferenceType.USUAL:
        return usual(d)
    if ptype == PreferenceType.U_SHAPE:
        _require(q=q)
        return u_shape(d, q)  # type: ignore[arg-type]
    if ptype == PreferenceType.V_SHAPE:
        _require(p=p)
        return v_shape(d, p)  # type: ignore[arg-type]
    if ptype == PreferenceType.LEVEL:
        _require(q=q, p=p)
        return level(d, q, p)  # type: ignore[arg-type]
    if ptype == PreferenceType.LINEAR:
        _require(q=q, p=p)
        return linear(d, q, p)  # type: ignore[arg-type]
    if ptype == PreferenceType.GAUSSIAN:
        _require(s=s)
        return gaussian(d, s)  # type: ignore[arg-type]

    raise ValueError(f"Tipo de preferência desconhecido: {ptype}")


def _require(**params: float | None) -> None:
    """Garante que os parâmetros exigidos pelo tipo foram fornecidos."""
    missing = [name for name, value in params.items() if value is None]
    if missing:
        raise ValueError(f"Parâmetros obrigatórios ausentes: {', '.join(missing)}")
