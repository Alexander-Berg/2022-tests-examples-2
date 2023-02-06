import json
import math

import pytest


_EARTH_RADIUS = 6372795
_AVG_SPEED = 8.0
_CORRECTION_FACTOR = 1.5


def approx_distance(p1, p2):
    lat1, lng1 = math.radians(p1[1]), math.radians(p1[0])
    lat2, lng2 = math.radians(p2[1]), math.radians(p2[0])

    sin_lat1, cos_lat1 = math.sin(lat1), math.cos(lat1)
    sin_lat2, cos_lat2 = math.sin(lat2), math.cos(lat2)

    delta_lng = lng2 - lng1
    cos_delta_lng, sin_delta_lng = math.cos(delta_lng), math.sin(delta_lng)

    d = math.atan2(
        math.sqrt(
            (cos_lat2 * sin_delta_lng) ** 2
            + (cos_lat1 * sin_lat2 - sin_lat1 * cos_lat2 * cos_delta_lng) ** 2,
        ),
        sin_lat1 * sin_lat2 + cos_lat1 * cos_lat2 * cos_delta_lng,
    )

    return _EARTH_RADIUS * d


def _approx_path(
        from_pos, to_pos, start_distance, start_time, part_distance, part_time,
):
    cnt = int(part_distance)
    if cnt <= 1:
        return []

    d_lon = (from_pos[0] - to_pos[0]) / cnt
    d_lat = (from_pos[1] - to_pos[1]) / cnt
    d_distance = part_distance / cnt
    d_time = part_time / cnt

    res = []
    for i in range(1, cnt):
        res.append(
            {
                'position': [from_pos[0] + d_lon * i, from_pos[1] + d_lat * i],
                'length': start_distance + d_distance * i,
                'duration': start_time + d_time * i,
            },
        )
    return res


@pytest.fixture
def tigraph(mockserver, load):
    @mockserver.json_handler('/tigraph-router//route')
    def router(request):
        data = json.loads(request.get_data())
        path = data['route']
        detailed_info = data['detailed_info']

        # calculate
        total_distance = 0
        total_time = 0
        path_info = [
            {
                'position': path[0],
                'length': 0,
                'duration': 0,
                'is_route_point': True,
            },
        ]
        for i in range(1, len(path)):
            from_pos = path[i - 1]
            to_pos = path[i]

            part_distance = (
                approx_distance(from_pos, to_pos) * _CORRECTION_FACTOR
            )
            part_time = part_distance / _AVG_SPEED

            path_info.extend(
                _approx_path(
                    from_pos,
                    to_pos,
                    total_distance,
                    total_time,
                    part_distance,
                    part_time,
                ),
            )

            total_distance += part_distance
            total_time += part_time

            path_info.append(
                {
                    'position': to_pos,
                    'length': total_distance,
                    'duration': total_time,
                    'is_route_point': True,
                },
            )

        # format
        resp = {'summary': {'duration': total_time, 'length': total_time}}
        if detailed_info:
            resp['path_info'] = path_info

        return mockserver.make_response(json.dumps(resp))

    return router
