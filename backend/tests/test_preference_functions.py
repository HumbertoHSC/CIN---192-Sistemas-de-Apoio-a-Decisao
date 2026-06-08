"""Testes das 6 funções de preferência (Brans & Vincke, 1986)."""

import numpy as np
import pytest

from app.core.preference_functions import (
    PreferenceType,
    apply_preference,
    gaussian,
    level,
    linear,
    u_shape,
    usual,
    v_shape,
)


def test_usual():
    assert usual(np.array(-1.0)) == 0.0
    assert usual(np.array(0.0)) == 0.0
    assert usual(np.array(0.5)) == 1.0


def test_u_shape():
    assert u_shape(np.array(0.5), q=1.0) == 0.0
    assert u_shape(np.array(1.0), q=1.0) == 0.0  # estritamente maior que q
    assert u_shape(np.array(2.0), q=1.0) == 1.0


def test_v_shape():
    assert v_shape(np.array(1.0), p=2.0) == pytest.approx(0.5)
    assert v_shape(np.array(3.0), p=2.0) == 1.0
    assert v_shape(np.array(-1.0), p=2.0) == 0.0


def test_level():
    assert level(np.array(0.0), q=1.0, p=3.0) == 0.0
    assert level(np.array(2.0), q=1.0, p=3.0) == 0.5
    assert level(np.array(4.0), q=1.0, p=3.0) == 1.0


def test_linear():
    assert linear(np.array(0.5), q=1.0, p=3.0) == 0.0
    assert linear(np.array(2.0), q=1.0, p=3.0) == pytest.approx(0.5)
    assert linear(np.array(4.0), q=1.0, p=3.0) == 1.0


def test_gaussian():
    assert gaussian(np.array(1.0), s=1.0) == pytest.approx(1 - np.exp(-0.5))
    assert gaussian(np.array(-1.0), s=1.0) == 0.0


def test_apply_dispatch_and_validation():
    assert apply_preference(np.array(2.0), PreferenceType.USUAL) == 1.0
    with pytest.raises(ValueError):
        apply_preference(np.array(2.0), PreferenceType.LINEAR)  # faltam q, p


def test_vectorized():
    d = np.array([-1.0, 0.0, 1.0, 5.0])
    out = apply_preference(d, PreferenceType.V_SHAPE, p=2.0)
    np.testing.assert_allclose(out, [0.0, 0.0, 0.5, 1.0])
