import pytest
from yandex.maps import geolib3
from sandbox.projects.masstransit.MapsMasstransitJumpCounter import count_jumps


def test_pos_in_polyline():
    points = [
        geolib3.Point2(0, 0),
        geolib3.Point2(0, 1),
        geolib3.Point2(1, 1),
        geolib3.Point2(1, 2),
    ]
    line = geolib3.Polyline2()
    for point in points:
        line.add(point)
    distances = [0.]
    for segment in line.segments():
        distances.append(distances[-1] + segment.geolength())

    # Check segment ends
    for point, distance in zip(points, distances):
        assert count_jumps.pos_in_polyline(line, distance / distances[-1]) == point

    # Check inside a segment
    a = geolib3.Point2(
        points[0].x * 2 / 3. + points[1].x / 3,
        points[0].y * 2 / 3. + points[1].y / 3,
    )
    t = distances[1] / 3 / distances[-1]
    assert count_jumps.pos_in_polyline(line, t) == a

    # Check outside a polyline
    with pytest.raises(AssertionError):
        count_jumps.pos_in_polyline(line, -0.1)

    with pytest.raises(AssertionError):
        count_jumps.pos_in_polyline(line, 1.1)
