import datetime
import math
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from yandex.maps.proto.common2 import geo_object_pb2
from yandex.maps.proto.common2 import geometry_pb2
from yandex.maps.proto.common2 import metadata_pb2
from yandex.maps.proto.common2 import response_pb2
from yandex.maps.proto.driving import route_pb2

from rida import consts
from rida.logic.geo import google_maps_codec

Point = List[float]


def make_gmaps_point_response(results: List) -> Dict[str, Any]:
    if not results:
        return {'status': 'ZERO_RESULTS'}

    return {'status': 'OK', 'results': results}


def make_gmaps_distance_response(
        distance: float,
        duration: float,
        duration_in_traffic: Optional[float] = None,
) -> Dict[str, Any]:
    elements = {
        'elements': [
            {
                'status': 'OK',
                'distance': {'text': 'km', 'value': distance},
                'duration': {'text': 'ms', 'value': duration},
                'duration_in_traffic': {
                    'text': 'ms',
                    'value': duration_in_traffic or duration,
                },
            },
        ],
    }
    return {
        'status': 'OK',
        'rows': [elements],
        'destination_addresses': [],
        'origin_addresses': [],
    }


def validate_gmaps_request(
        mock_google_maps,
        retries_expected: bool,
        src_point: List,
        dst_point: List,
        now: datetime.datetime,
        traffic_model: str = 'best_guess',
):
    if retries_expected is None:
        assert mock_google_maps.times_called == 1
    else:
        assert mock_google_maps.times_called >= 1
    google_maps_request = mock_google_maps.next_call()['request']
    expected_request = {
        'origins': f'{src_point[1]},{src_point[0]}',
        'destinations': f'{dst_point[1]},{dst_point[0]}',
        'traffic_model': traffic_model,
        'language': 'en',
        'departure_time': str(int(now.timestamp())),
        'google_api_key': 'rida',
    }
    assert dict(google_maps_request.query) == expected_request


def round_all(coords, digits: int = 5):
    return [[round(x, digits) for x in y] for y in coords]


POLYLINE = round_all(
    [
        [40.517578125, 64.543719],
        [39.990234375, 64.41117678357296],
        [39.847412109375, 63.10966911470206],
        [39.15527343749999, 63.05495931065107],
        [39.166259765625, 62.6993490083977],
        [42.25341796875, 62.67918619685372],
        [42.1435546875, 63.11463763252091],
        [41.37451171875, 63.1196053006856],
        [41.27563476562499, 64.41592147626879],
        [40.58349609375, 64.54844014422517],
    ],
)


def _get_middle_point(x: List[float], y: List[float]) -> List[float]:
    return [round((x[0] + y[0]) / 2, 5), round((x[1] + y[1]) / 2, 5)]


def generate_polyline(
        points: List[List[float]], interpolate_polyline: bool,
) -> List[List[float]]:
    if not points:
        return []
    new_points = []
    for i in range(len(points) - 1):
        new_points.append(points[i])
        if interpolate_polyline:
            new_points.append(_get_middle_point(points[i], points[i + 1]))
    new_points.append(points[-1])
    return new_points


def generate_encoded_polyline(
        points: List[List[float]], interpolate_polyline: bool,
) -> str:
    if not points:
        return ''
    new_points = generate_polyline(points, interpolate_polyline)
    return google_maps_codec.encode(new_points, geojson=True)


def _dummy_text_value(value: float) -> Dict[str, Any]:
    return {'text': 'text', 'value': value}


def _geojson_to_json(geo_json: List[float]) -> Dict[str, float]:
    return {'lat': geo_json[1], 'lng': geo_json[0]}


def _generate_gmaps_steps(polyline: List[List[float]]) -> List[Dict[str, Any]]:
    steps = []
    for i in range(len(polyline) - 1):
        x = polyline[i]
        y = polyline[i + 1]
        distance = math.fabs(x[0] - y[0]) + math.fabs(x[1] - y[1])
        steps.append(
            {
                'duration': _dummy_text_value(distance / 10),
                'distance': _dummy_text_value(distance),
                'polyline': {
                    'points': generate_encoded_polyline([x, y], True),
                },
                'html_instruction': 'html_instruction',
                'start_location': _geojson_to_json(x),
                'end_location': _geojson_to_json(y),
                'travel_mode': 'DRIVING',
            },
        )
    return steps


def _url_to_list(url: str) -> List[str]:
    return list(sorted(re.split('[&?]', url)))


def make_gmaps_directions_response(
        polyline: List[List[float]],
        duration: float,
        expected_distance: float,
        duration_in_traffic: float,
        return_code: int,
        status: str,
        corrupt_response: bool,
        mockserver,
):
    leg = {
        'start_address': 'start_address',
        'start_location': 'start_location',
        'end_address': 'end_address',
        'end_location': 'end_location',
        'steps': _generate_gmaps_steps(polyline),
        'traffic_speed_entry': [],
        'via_waypoint': [],
        'duration': _dummy_text_value(duration),
        'distance': _dummy_text_value(expected_distance),
        'duration_in_traffic': _dummy_text_value(duration_in_traffic),
    }
    route = {
        'bounds': {
            'northeast': {'lat': 1, 'lng': 1},
            'southwest': {'lat': 2, 'lng': 2},
        },
        'copyrights': 'copyrights',
        'legs': [leg],
        'overview_polyline': {
            'points': generate_encoded_polyline(polyline, False),
        },
        'summary': 'summary',
        'warnings': [],
        'waypoint_order': [],
    }
    response = {'status': status, 'routes': [route]}
    if corrupt_response:
        response['routes'] = []
    return mockserver.make_response(status=return_code, json=response)


def validate_mapbox_request(
        mock_maps, retries_expected: bool, src_point: List, dst_point: List,
):
    if retries_expected is None:
        assert mock_maps.times_called == 1
    else:
        assert mock_maps.times_called >= 1
    mapbox_maps_request = mock_maps.next_call()['request']
    expected_request = {
        'path': f'{src_point[0]},{src_point[1]};{dst_point[0]},{dst_point[1]}',
        'geometries': 'polyline',
        'alternatives': 'false',
        'mode': 'driving',
        'steps': 'false',
        'mapbox_api_key': 'rida',
    }
    assert dict(mapbox_maps_request.query) == expected_request


def _generate_mapbox_steps(
        polyline: List[List[float]],
) -> List[Dict[str, Any]]:
    steps = []
    for i in range(len(polyline) - 1):
        x = polyline[i]
        y = polyline[i + 1]
        distance = math.fabs(x[0] - y[0]) + math.fabs(x[1] - y[1])
        steps.append(
            {
                'duration': distance / 10,
                'distance': distance,
                'geometry': generate_encoded_polyline([x, y], True),
            },
        )
    return steps


def make_mapbox_directions_response(
        polyline: List[List[float]],
        duration: float,
        expected_distance: float,
        return_code: int,
        status: str,
        corrupt_response: bool,
        mockserver,
):
    leg = {
        'duration': duration,
        'distance': expected_distance,
        'steps': _generate_mapbox_steps(polyline),
    }
    route = {
        'duration': duration,
        'distance': expected_distance,
        'legs': [leg],
        'geometry': generate_encoded_polyline(polyline, False),
    }
    response = {'code': status, 'routes': [route], 'waypoints': []}
    if corrupt_response:
        response['routes'] = []
    return mockserver.make_response(status=return_code, json=response)


def make_gmaps_suggest_response(
        predictions: List[Dict[str, Any]],
        status: Optional[str] = consts.EXTERNAL_GEO_OK_STATUS,
) -> Dict[str, Any]:
    result = {
        'status': status,
        'predictions': [
            {
                'place_id': prediction['place_id'],
                'description': prediction['description'],
                'types': [],
                'structured_formatting': {
                    'main_text': 'main',
                    'secondary': 'secondary',
                },
            }
            for prediction in predictions
        ],
    }

    return result


def _intify_coordinates(coords: List[float]) -> List[int]:
    return [int(x * 1000000 + 0.5) for x in coords]


def _make_geo_object_by_points(
        first: List[int], second: List[int], third: List[int],
) -> geo_object_pb2.GeoObject:
    return geo_object_pb2.GeoObject(
        geometry=[
            geometry_pb2.Geometry(
                polyline=geometry_pb2.Polyline(
                    lons=geometry_pb2.CoordSequence(
                        first=first[0],
                        deltas=[second[0] - first[0], third[0] - second[0]],
                    ),
                    lats=geometry_pb2.CoordSequence(
                        first=first[1],
                        deltas=[second[1] - first[1], third[1] - second[1]],
                    ),
                ),
            ),
        ],
    )


def _make_yamaps_routes_response():
    metadata = metadata_pb2.Metadata()
    route = metadata.Extensions[  # pylint: disable=E1101
        route_pb2.ROUTE_METADATA
    ]
    route.flags.blocked = False
    route.weight.time.value = 5
    route.weight.time.text = 'min'
    route.weight.time_with_traffic.value = 7
    route.weight.time_with_traffic.text = 'min'
    route.weight.distance.value = 10
    route.weight.distance.text = 'km'

    polyline = round_all(generate_polyline(POLYLINE, True))
    geo_objects = [
        _make_geo_object_by_points(
            _intify_coordinates(a),
            _intify_coordinates(b),
            _intify_coordinates(c),
        )
        for a, b, c in zip(polyline[::2], polyline[1::2], polyline[2::2])
    ]

    return response_pb2.Response(
        reply=geo_object_pb2.GeoObject(
            geo_object=[
                geo_object_pb2.GeoObject(
                    geo_object=geo_objects, metadata=[metadata],
                ),
            ],
        ),
    )


def mock_yamaps(request, empty_response: bool, mockserver):
    assert request.query == {
        'rll': (
            f'{POLYLINE[0][0]},{POLYLINE[0][1]}~'
            f'{POLYLINE[-1][0]},{POLYLINE[-1][1]}'
        ),
        'mode': 'best',
    }
    body = ''
    if not empty_response:
        body = _make_yamaps_routes_response().SerializeToString()
    return mockserver.make_response(
        body, content_type='application/x-protobuf', status=200,
    )
