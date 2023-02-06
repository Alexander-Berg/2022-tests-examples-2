import datetime

import pytest

from taxi.internal import geo_position


LON, LAT, DATE = 37.587658, 55.733629, datetime.datetime(2015, 1, 1, 7, 25, 15)


@pytest.fixture
def position():
    return geo_position.Position(lon=LON, lat=LAT, geotime=DATE)


@pytest.mark.filldb(_fill=False)
def test_point(position):
    assert position.point == (LON, LAT)


@pytest.mark.filldb(_fill=False)
def test_str(position):
    assert str(position) == '(37.588, 55.734)'


@pytest.mark.filldb(_fill=False)
def test_repr(position):
    expexted = ('Position(37.587658, 55.733629, '
                'datetime.datetime(2015, 1, 1, 7, 25, 15))')
    assert repr(position) == expexted


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'lon, lat, date, expected',
    [
        (LON, LAT, datetime.datetime.utcnow(), False),
        (LAT, LON, DATE, False),
        (LON, LAT, DATE, True),
    ]
)
def test_eq(position, lon, lat, date, expected):
    result = position == geo_position.Position(lon, lat, date)
    assert result is expected


@pytest.mark.filldb(_fill=False)
def test_from_coordinate(position):
    coordinate = [LON, LAT]

    result = geo_position.Position.from_coordinate(coordinate, geotime=DATE)

    assert result == position
