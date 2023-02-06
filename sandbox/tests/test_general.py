import random
import sys

import pytest

from sandbox.projects.yabs.qa.utils.general import (
    diff_dict,
    issubset_dict,
    random_seed,
)


def test_random_seed_context():
    seed = 42
    a = -sys.maxint - 1
    b = sys.maxint
    current_state = random.getstate()
    with random_seed(seed):
        first = random.randint(a, b)
    with random_seed(seed):
        second = random.randint(a, b)
    assert first == second
    assert random.getstate() == current_state


@pytest.mark.parametrize(('dict_', 'other_', 'result'), [
    ({'k': 'v'}, {'k': 'v'}, True),
    ({'one': 1}, {'one': 1}, True),
    ({'k': ['v', 'w']}, {'k': ['v', 'w']}, True),
    ({'k': 'v', 'a': 'b'}, {'k': 'v', 'a': 'b', 'x': 'y'}, True),
    ({'k': 'v'}, {'k': 'v', 'a': 'b'}, True),
    ({}, {'k': 'v'}, True),
    ({'k': 'v'}, {'k': 'z'}, False),
    ({'k': 'v'}, {}, False),
])
def test_issubset_dict(dict_, other_, result):
    assert issubset_dict(dict_, other_) == result


@pytest.mark.parametrize(("dict_", "other_", "diff_str"), [
    (
        {"k1": 1, "k2": 2, "k3": 3},
        {"k2": 2, "k3": 4, "k0": 0},
        "- k1: 1\n- k3: 3\n+ k3: 4\n+ k0: 0\n"
    ),
    (
        {"k1": 1, "k2": 2, "k3": 3},
        {"k3": 3, "k1": 1, "k2": 2},
        ""
    )
])
def test_diff_dict(dict_, other_, diff_str):
    assert diff_dict(dict_, other_) == diff_str
