import datetime as dt

import pytest

from taxi_billing_subventions.eye import common


@pytest.mark.nofilldb()
def test_convert_detail_value():
    datetime = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
    # pylint: disable=protected-access
    actual = common._convert_detail_value(frozenset([datetime]))
    assert actual == ['2020-01-01T00:00:00.000000+00:00']
