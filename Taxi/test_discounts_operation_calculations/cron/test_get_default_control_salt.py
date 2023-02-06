# pylint: disable=W0212
import pytest

from discounts_operation_calculations.internals import tags_calculator


@pytest.mark.now('2020-09-14 10:00:00')
async def test_default_control_salt():
    default_salt = tags_calculator.TagsCalculator._get_default_control_salt()
    assert default_salt == '2020-09-14-kt2'
