# pylint: disable=protected-access,undefined-variable
import datetime as dt
import decimal

import pytest

from replication_core.mapping import exceptions


@pytest.mark.skip('TAXIDATA-1370')
@pytest.mark.parametrize(
    'value, expected, error',
    [
        (decimal.Decimal('0'), 0, None),
        (decimal.Decimal('0.000000000000000'), 0, None),
        (decimal.Decimal('0.0001'), 100, None),
        (decimal.Decimal('1000.000001'), 1000000001, None),
        (decimal.Decimal('1000.0000001'), None, exceptions.CastError),
        # (
        #     decimal.Decimal(cast.MAX_INT), cast.MAX_INT, None,
        # ),
        # (
        #     decimal.Decimal(cast.MAX_INT + 10), cast.MAX_INT, None,
        # ),
        # (
        #     decimal.Decimal(cast.MIN_INT - 1), cast.MIN_INT, None,
        # ),
        (decimal.Decimal('NaN'), None, None),
        # (
        #     decimal.Decimal('inf'), cast.MAX_INT, None,
        # ),
        # (
        #     decimal.Decimal('-inf'), cast.MAX_INT, None,
        # ),
        (123, None, exceptions.CastError),
        (None, None, None),
    ],
)
@pytest.mark.nofilldb()
def test_decimal_to_increased_int(value, expected, error):
    caster = cast._get_decimal_to_increased_int(6)  # noqa: F821

    if error is not None:
        with pytest.raises(error):
            caster(value)
    else:
        assert caster(value) == expected


@pytest.mark.skip('TAXIDATA-1370')
@pytest.mark.parametrize(
    'value, expected, error',
    [
        (None, None, None),
        (
            dt.datetime(2019, 4, 20, 14, 3, 59, 399),
            '2019-04-20T14:03:59.000399',
            None,
        ),
        (dt.datetime(2019, 4, 20), '2019-04-20T00:00:00', None),
        (
            dt.datetime(2019, 4, 20, 14, 3, 59, 399, tzinfo=dt.timezone.utc),
            '2019-04-20T14:03:59.000399+00:00',
            None,
        ),
        (
            dt.datetime(
                2019,
                4,
                20,
                14,
                3,
                59,
                399,
                tzinfo=dt.timezone(dt.timedelta(hours=4)),
            ),
            '2019-04-20T14:03:59.000399+04:00',
            None,
        ),
        (123, None, exceptions.CastError),
        (None, None, None),
    ],
)
@pytest.mark.nofilldb()
def test_datetime_to_iso_string(value, expected, error):
    if error is not None:
        with pytest.raises(error):
            cast.datetime_to_iso_string(value)  # noqa: F821
    else:
        assert cast.datetime_to_iso_string(value) == expected  # noqa: F821
