import pytest

from abt.logic import calc as calc_logic


@pytest.mark.parametrize(
    'control_value,test_value,abs_expected,relative_expected',
    [
        pytest.param(10, 20, 10, 100, id='positive digits'),
        pytest.param(-10, -20, -10, 100, id='negative digits'),
        pytest.param(20, 10, -10, -50, id='negative abs'),
        pytest.param(-20, -10, 10, -50, id='negative relative'),
        pytest.param(
            0, 10, 10, None, id='control is zero -> relative is zero',
        ),
        pytest.param(10, 0, -10, -100, id='test is zero'),
        pytest.param(
            123, 321, 198, 160.9756, id='relative diff if float and > 100',
        ),
    ],
)
def test_diff(control_value, test_value, abs_expected, relative_expected):
    diff = calc_logic.diff(control_value, test_value)
    assert round(diff.abs, 4) == abs_expected
    assert (
        round(diff.relative, 4)
        if relative_expected is not None
        else diff.relative
    ) == relative_expected
