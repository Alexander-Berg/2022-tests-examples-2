from typing import Any

import pytest

from noc.grad.grad.lib.test_functions import get_testdata
from noc.grad.grad.user_functions.linux_transceiver import parse_transceiver

CASES = [
    ["linux_transceiver_case1.txt", None],
    ["linux_transceiver_case2.txt", (-10, 3.4, [-0.63, -0.62, -0.78, -0.96], [0.19, 0.31, 0.19, 0.5], 27.61)],
]


@pytest.mark.parametrize("test_filename, expected", CASES)
def test_parse_transceiver(test_filename: str, expected: Any):
    res = parse_transceiver(get_testdata(test_filename).decode(), {})
    assert res == expected
