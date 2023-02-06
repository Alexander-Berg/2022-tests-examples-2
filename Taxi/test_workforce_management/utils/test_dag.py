import pytest

from workforce_management.common.utils import dag


@pytest.mark.parametrize(
    'tst_values, expected_result',
    [
        pytest.param([(3, 4), (4, 5)], True),
        pytest.param([(0, 1), (1, 2), (2, 3), (3, 1)], False),
    ],
)
async def test_is_directed_acyclic_graph(tst_values, expected_result):
    assert dag.DiGraph(tst_values).is_acyclic() == expected_result
