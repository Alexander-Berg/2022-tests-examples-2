import pytest

from taxi_exp import util


@pytest.mark.parametrize(
    'source,expected',
    [
        ('2021-12-31T23:59:59+03:00', '2021-12-31T23:59:59+03:00'),
        ('2021-12-31T23:59:59+04:00', '2021-12-31T22:59:59+03:00'),
    ],
)
def test_date_transformation_flow(source, expected):
    assert (
        util.to_moscow_isoformat(util.parse_and_clean_datetime(source))
        == expected
    )
    assert util.history_isoformat(source) == expected
