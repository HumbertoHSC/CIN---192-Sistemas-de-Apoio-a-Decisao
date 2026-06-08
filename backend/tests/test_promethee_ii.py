"""Testes do PROMETHEE II com exemplo verificável analiticamente.

Caso de 1 critério (maximizar, função usual), valores A=10, B=20, C=30:

* φ⁺ = (0, 0.5, 1.0)   φ⁻ = (1.0, 0.5, 0)   φ = (-1, 0, +1)
* ranking: C (1º), B (2º), A (3º)
"""

import numpy as np
import pytest

from app.core.flows import CriterionSpec, compute_flows
from app.core.preference_functions import PreferenceType
from app.core.promethee_ii import rank


def _single_criterion():
    matrix = np.array([[10.0], [20.0], [30.0]])
    criteria = [CriterionSpec(name="g1", weight=1.0, maximize=True, preference=PreferenceType.USUAL)]
    names = ["A", "B", "C"]
    return matrix, criteria, names


def test_flows_single_criterion():
    matrix, criteria, _ = _single_criterion()
    flows = compute_flows(matrix, criteria)
    np.testing.assert_allclose(flows.phi_plus, [0.0, 0.5, 1.0])
    np.testing.assert_allclose(flows.phi_minus, [1.0, 0.5, 0.0])
    np.testing.assert_allclose(flows.phi_net, [-1.0, 0.0, 1.0])


def test_net_flow_sums_to_zero():
    matrix, criteria, _ = _single_criterion()
    flows = compute_flows(matrix, criteria)
    assert flows.phi_net.sum() == pytest.approx(0.0)


def test_ranking_order():
    matrix, criteria, names = _single_criterion()
    result = rank(matrix, criteria, names)
    by_rank = {s.rank: s.name for s in result.scores}
    assert by_rank == {1: "C", 2: "B", 3: "A"}


def test_minimize_inverts_preference():
    # Mesmos valores, mas agora menor é melhor → A vira o melhor.
    matrix = np.array([[10.0], [20.0], [30.0]])
    criteria = [CriterionSpec(name="g1", weight=1.0, maximize=False, preference=PreferenceType.USUAL)]
    result = rank(matrix, criteria, ["A", "B", "C"])
    by_rank = {s.rank: s.name for s in result.scores}
    assert by_rank == {1: "A", 2: "B", 3: "C"}


def test_weights_are_normalized():
    matrix = np.array([[10.0, 1.0], [20.0, 2.0]])
    criteria = [
        CriterionSpec(name="g1", weight=3.0, preference=PreferenceType.USUAL),
        CriterionSpec(name="g2", weight=1.0, preference=PreferenceType.USUAL),
    ]
    flows = compute_flows(matrix, criteria)
    np.testing.assert_allclose(flows.weights, [0.75, 0.25])


def test_dimension_mismatch_raises():
    with pytest.raises(ValueError):
        compute_flows(
            np.array([[1.0, 2.0]]),
            [CriterionSpec(name="only_one", weight=1.0)],
        )
