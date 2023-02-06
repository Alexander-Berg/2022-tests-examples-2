import decimal

import pytest
from shapely import geometry

from rida.models import zone as zone_models


def make_zone(polygon):
    default_value = decimal.Decimal('0.0')
    return zone_models.Zone(
        id=0,
        time_coefficient=None,
        distance_coefficient=None,
        suggest_price_constant=default_value,
        min_offer_amount=default_value,
        fix_price=default_value,
        bid_step=default_value,
        polygons={'0': [geometry.Polygon(polygon)]},
    )


DEFAULT_ZONE = make_zone([[0, 0], [0, 1], [1, 1], [1, 0]])


@pytest.mark.parametrize(
    ['zone', 'point', 'expected_contains'],
    [
        pytest.param(DEFAULT_ZONE, [0.5, 0.5], True),
        pytest.param(DEFAULT_ZONE, [0.0001, 0.5], True),
        pytest.param(DEFAULT_ZONE, [0.5, 0.0001], True),
        pytest.param(DEFAULT_ZONE, [0.5, 0.999], True),
        pytest.param(DEFAULT_ZONE, [0.999, 0.5], True),
        pytest.param(DEFAULT_ZONE, [0.999, 0.999], True),
        pytest.param(DEFAULT_ZONE, [1, 1], False),
        pytest.param(DEFAULT_ZONE, [0, 0], False),
        pytest.param(DEFAULT_ZONE, [1, -1], False),
    ],
)
def test_contains(zone, point, expected_contains):
    for _, polygons in zone.polygons.items():
        for polygon in polygons:
            assert polygon.is_valid
    result = zone.contains(point)
    assert result == expected_contains
