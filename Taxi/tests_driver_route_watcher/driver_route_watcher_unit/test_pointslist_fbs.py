# pylint: disable=import-error
import tests_driver_route_watcher.points_list_fbs as PointslistFbs


def test_points_list():
    orig = [
        {
            'point': [11, 22],
            'order_id': 'aaaa',
            'point_id': 'bbbb',
            'wait_time': 1111,
            'park_time': 0,
        },
        {
            'point': [33.56, 44.66],
            'order_id': 'cccc',
            'point_id': 'dddd',
            'wait_time': 2222,
            'park_time': 0,
        },
    ]
    data = PointslistFbs.serialize_pointslist(orig)
    points = PointslistFbs.deserialize_pointslist(data)
    assert points == orig


def test_points_list_without_properties():
    orig = PointslistFbs.to_point_list([[11, 22], [33.56, 44.66]])
    data = PointslistFbs.serialize_pointslist(orig)
    points = PointslistFbs.deserialize_pointslist(data)
    assert points == orig
