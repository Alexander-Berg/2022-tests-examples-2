# pylint: disable=redefined-outer-name

import functools
import math
import random
import typing as tp

import pytest

from workforce_management.common.utils import fenwicktree


def random_uniform(
        low: int = -100, high: int = 100000, size: tp.Optional[int] = None,
) -> tp.Union[tp.List[float], float]:
    """
    Return a random number or a list of `size` numbers
    in the range [low, high) or [low, high] depending on rounding.
    """
    dist = functools.partial(random.uniform, low, high)
    return dist() if size is None else [dist() for _ in range(size)]


QUERIES_COUNT = 5000

LEAF_COUNTS = [0, 1, int(24 * 60 * 30.5 * 12)]


def test_sum(leaves, tree):
    # step size to perform the desired number of queries
    step = max(len(leaves) // QUERIES_COUNT, 1)
    expected = 0
    k_idx = 0
    for index in range(0, len(leaves), step):
        while k_idx != index + 1:
            expected += leaves[k_idx]
            k_idx += 1
        assert math.isclose(tree.sum(index), expected)


def test_update(leaves, tree):
    delta = random_uniform()
    # step size to perform the desired number of queries
    step = max(len(leaves) // QUERIES_COUNT, 1)
    expected = 0
    k_idx = 0
    for index in range(0, len(leaves), step):
        tree.update(index, delta)
        leaves[index] += delta
        while k_idx != index + 1:
            expected += leaves[k_idx]
            k_idx += 1
        assert math.isclose(tree.sum(index), expected)


@pytest.fixture
def tree(leaves):
    return fenwicktree.FenwickTree(leaves)


@pytest.fixture(
    params=[pytest.param(size, id=f'size_{size}') for size in LEAF_COUNTS],
)
def leaves(request):
    return list(random_uniform(size=request.param))
