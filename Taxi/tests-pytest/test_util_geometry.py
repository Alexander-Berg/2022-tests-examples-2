import pytest

from taxi.util import geometry


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('end_point,direction', [
    ((37.617910, 55.755836), 90),
    ((37.617642, 55.755679), 180),
    ((37.617224, 55.755812), 270),
    ((37.617631, 55.756008), 360),

    ((37.617841, 55.755957), 45)
])
def test_get_bearing(end_point, direction):
    start_point = (37.617633, 55.755817)
    assert abs(geometry.get_bearing(start_point, end_point) - direction) < 10
