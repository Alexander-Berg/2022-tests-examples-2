import json

import pytest

from taxi.external import route_adjust


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_adjust_track(load, patch):
    stab = json.loads(load('%s.json' % test_adjust_track.__name__))
    stab = stab['response']

    @patch('taxi.external.route_adjust._make_request')
    def foo(*args, **kwargs):
        return stab

    track = yield route_adjust.adjust_track([])
    assert list(track) == [
        route_adjust.RouteSegment(
            length=51.13798057,
            current_distance=51.13798057,
            source_points=[
                ((37.57598053, 55.75216058), 0., 0.),
                ((37.57598053, 55.75216058), 0.0, 0.0),
                ((37.57679749, 55.75216293), 0.2226512197, 51.13798057),
            ],
            coordinates=[
                (37.57598053, 55.75216058),
                (37.57679749, 55.75216293)
            ]
        )
    ]


@pytest.mark.filldb(_fill=False)
def test_is_same_point():
    points = [
        ((37.57598053, 55.75216058), 0., 0.),
        ((37.57598053, 55.75216058), 0., 0.),
        ((37.57679749, 55.75216293), 0.2226512197, 51.13798057)
    ]
    assert route_adjust._is_same_point(points, 1, 0) is True
    assert route_adjust._is_same_point(points, 0, 1) is True
    assert route_adjust._is_same_point(points, 2, 1) is False


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_adjusted_point(load, patch):
    stab = json.loads(load('%s.json' % test_adjust_track.__name__))
    stab = stab['response']

    @patch('taxi.external.route_adjust._make_request')
    def foo(*args, **kwargs):
        return stab

    point = yield route_adjust.get_adjusted_point([])
    assert point[0] == (37.57679749, 55.75216293)
    assert isinstance(point[1], float)
