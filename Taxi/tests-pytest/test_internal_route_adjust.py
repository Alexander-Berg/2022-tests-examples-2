import datetime
import json

import pytest

from taxi.internal import geo_position
from taxi.internal import route_adjust
from taxi.util import geometry
from taxi.util import itertools_ext


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_adjust_track(patch, load):
    source = [
        (37.56818, 55.677505),
        (37.5686883333, 55.677725),
        (37.568885, 55.67788),
        (37.5689116667, 55.6777233333),
        (37.568785, 55.68005),
        (37.5691433333, 55.6820133333),
        (37.5694516667, 55.6826416667),
        (37.56969, 55.6826083333),
        (37.569905, 55.6846183333),
        (37.5702733333, 55.6862466667),
        (37.5703766667, 55.686605),
        (37.570425, 55.6864666667),
        (37.5709366667, 55.6866733333),
        (37.5709366667, 55.6866733333),
        (37.5709366667, 55.6866733333),
        (37.5709366667, 55.6866733333),
        (37.5709366667, 55.6866733333),
        (37.5709366667, 55.6866733333),
        (37.5709366667, 55.6866733333),
        (37.5709366667, 55.6866733333),
        (37.5709366667, 55.6866733333),
        (37.57319, 55.69511),
        (37.57319, 55.69511),
        (37.57319, 55.69511),
        (37.57319, 55.69511)
    ]

    @patch('taxi.external.route_adjust._make_request')
    def make_request(*args, **kwargs):
        x = json.loads(load('maps_response.json'))
        return x['response']

    track = [
        geo_position.DriverTrackPoint(
            lon, lat, datetime.datetime.utcnow(), speed=i,
        ) for (i, (lon, lat)) in enumerate(source)
    ]
    dist, route = yield route_adjust.adjust_track(track)
    assert dist == 3740.740047
    assert isinstance(route, list)
    assert len(route) > 1
    points = [p.point for p in route]

    pairs = itertools_ext.pairwise(points)
    calc_dist = sum(geometry.approx_distance(a, b) for a, b in pairs)
    assert abs(calc_dist - dist) < 10

    speed_seq = itertools_ext.pairwise(p.speed for p in route)
    assert all(a < b + 1 for (a, b) in speed_seq)

    time_seq = itertools_ext.pairwise(p.geotime for p in route)
    assert all(a <= b for (a, b) in time_seq)


def first_request():
    return [
        (37.5107616667, 55.6639683333),
        (37.5110716667, 55.6641733333),
        (37.51139, 55.664385),
        (37.5116333333, 55.6645783333),
        (37.5115616667, 55.6648166667),
        (37.5116916667, 55.665055),
        (37.5124983333, 55.6656283333),
        (37.5136416667, 55.6663833333),
        (37.5150516667, 55.667385),
        (37.5165766667, 55.6684333333),
        (37.5178083333, 55.66933),
        (37.5182416667, 55.6696633333),
        (37.5187416667, 55.6700233333),
        (37.5192916667, 55.6704116667),
        (37.5194133333, 55.6705066667)
    ]


def second_request():
    return [
        (37.5110716667, 55.6641733333),
        (37.51139, 55.664385),
        (37.5116333333, 55.6645783333),
        (37.5115616667, 55.6648166667),
        (37.5116916667, 55.665055),
        (37.5124983333, 55.6656283333),
        (37.5136416667, 55.6663833333),
        (37.5150516667, 55.667385),
        (37.5165766667, 55.6684333333),
        (37.5178083333, 55.66933),
        (37.5182416667, 55.6696633333),
        (37.5187416667, 55.6700233333),
        (37.5192916667, 55.6704116667),
        (37.5194133333, 55.6705066667),
        (37.5194133333, 55.6705066667)
    ]


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(_fill=False)
@pytest.mark.now('2016-11-16 15:00:00 +03')
@pytest.inline_callbacks
def test_jumps(patch, load):
    older = first_request()
    newer = second_request()
    now = datetime.datetime.utcnow()

    first_track = [
        geo_position.DriverTrackPoint(
            lon, lat, now + datetime.timedelta(minutes=i), speed=i,
        ) for (i, (lon, lat)) in enumerate(older)
    ]
    second_track = [
        geo_position.DriverTrackPoint(
            lon, lat, now + datetime.timedelta(minutes=i + 1), speed=i,
        ) for (i, (lon, lat)) in enumerate(newer)
    ]

    @patch('taxi.external.route_adjust._make_request')
    def newer_response(*args, **kwargs):
        x = json.loads(load('jumps_first.json'))
        return x['response']

    dist, route = yield route_adjust.adjust_track(first_track)
    assert isinstance(route, list)
    assert len(route) > 1

    @patch('taxi.external.route_adjust._make_request')
    def older_response(*args, **kwargs):
        x = json.loads(load('jumps_second.json'))
        return x['response']

    second_dist, second_route = yield route_adjust.adjust_track(second_track)
    assert isinstance(second_route, list)
    assert len(second_route) > 1

    assert second_route[0].geotime != route[0].geotime
    assert second_route[-3].geotime == route[-3].geotime
    assert second_route[-2].geotime == route[-2].geotime
    assert second_route[-1].geotime == route[-1].geotime
