import pytest

from taxi.util import decimal
from taxi.util import math_numbers


_NUM_DIGITS = 2


@pytest.fixture(params=range(10 ** _NUM_DIGITS))
def after_decimal_point(request):
    return request.param


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_from_float(after_decimal_point):
    # 0 -> '0.00'
    # 99 -> '0.99'
    as_str = '0.' + str(after_decimal_point).rjust(_NUM_DIGITS, '0')
    expected_decimal_value = decimal.Decimal(as_str)
    float_value = float(as_str)
    actual_decimal_value = math_numbers.from_float(float_value)
    assert actual_decimal_value == expected_decimal_value
