# pylint:disable=no-member
# type: ignore
import datetime

import pytest

from eventus_orchestrator_fbs.fbs.v1_polygon_values_response import (
    PolygonValuesResponse,
)

ResponseClass = PolygonValuesResponse.PolygonValuesResponse
TIMESTAMP = datetime.datetime(2020, 5, 10, 10, 30)
NEXT_HOUR = TIMESTAMP + datetime.timedelta(minutes=40)
FIRST_POLYGON = [
    {'coordinates': [-1.0, -2.0]},
    {'coordinates': [-1.0, 2.0]},
    {'coordinates': [1.0, -2.0]},
    {'coordinates': [-1.0, -2.0]},
]
SECOND_POLYGON = [
    {'coordinates': [0.0, 4.0]},
    {'coordinates': [3.0, 4.0]},
    {'coordinates': [3.0, 2.0]},
    {'coordinates': [0.0, 4.0]},
]


async def parse_response(response):
    res = {}
    data = ResponseClass.GetRootAsPolygonValuesResponse(
        bytearray(await response.read()), 0,
    )
    res['cursor'] = data.Cursor().decode('utf-8')
    polygons_length = data.PolygonsLength()
    polygons = []
    for i in range(polygons_length):
        polygon_binary = data.Polygons(i)
        coordinates_length = polygon_binary.CoordinatesLength()
        coordinates = []
        for j in range(coordinates_length):
            points = []
            coordinate_binary = polygon_binary.Coordinates(j)
            points_length = coordinate_binary.PointsLength()
            for k in range(points_length):
                point_binary = coordinate_binary.Points(k)
                point = {'lon': point_binary.Lon(), 'lat': point_binary.Lat()}
                points.append(point)
            coordinates.append({'points': points})
        groups_length = polygon_binary.GroupsLength()
        groups = []
        for j in range(groups_length):
            groups.append(polygon_binary.Groups(j).decode('utf-8'))
        polygons.append(
            {
                'id': polygon_binary.PolygonId().decode('utf-8'),
                'enabled': polygon_binary.Enabled(),
                'groups': groups,
                'coordinates': coordinates,
                'metadata': polygon_binary.Metadata(),
            },
        )
    res['polygons'] = polygons
    return res


@pytest.mark.filldb()
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    EVENTUS_ORCHESTRATOR_POLYGONS_SOURCE={'source': 'mongo'},
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EVENTUS_ORCHESTRATOR_POLYGONS_SOURCE={'source': 'config'},
                ),
            ],
        ),
    ],
)
async def test_base(web_app_client):
    response = await web_app_client.post(
        '/v1/polygon/values', json={'groups': []},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/polygon/values', json={'groups': ['group1']},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/polygon/values', json={'groups': [], 'cursor': 'asd'},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/polygon/values', json={'cursor': 'asd'},
    )
    assert response.status == 400


@pytest.mark.filldb()
@pytest.mark.config(
    ORDER_EVENTS_PRODUCER_POLYGONS=[
        {
            'name': 'zone1',
            'groups': ['group1', 'group2'],
            'points': FIRST_POLYGON,
        },
        {
            'name': 'zone2',
            'enabled': False,
            'groups': ['group2', 'group3'],
            'points': SECOND_POLYGON,
        },
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    EVENTUS_ORCHESTRATOR_POLYGONS_SOURCE={'source': 'mongo'},
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EVENTUS_ORCHESTRATOR_POLYGONS_SOURCE={'source': 'config'},
                ),
            ],
        ),
    ],
)
async def test_filter(web_app_client, taxi_config):
    response = await web_app_client.post(
        '/v1/polygon/values', json={'groups': []},
    )
    assert response.status == 200
    assert response.content_type == 'application/flatbuffer'
    data = await parse_response(response)
    assert data['cursor']
    polygons_length = len(data['polygons'])
    assert polygons_length == 2
    cfg = taxi_config.get('ORDER_EVENTS_PRODUCER_POLYGONS')
    for i in range(polygons_length):
        assert data['polygons'][i]['enabled'] == cfg[i].get('enabled', True)
        assert data['polygons'][i]['id'] == cfg[i].get('name', str(i))

    response = await web_app_client.post(
        '/v1/polygon/values', json={'groups': ['group2']},
    )
    data = await parse_response(response)
    polygons_length = len(data['polygons'])
    assert polygons_length == 2

    response = await web_app_client.post(
        '/v1/polygon/values', json={'groups': ['group1', 'group3']},
    )
    data = ResponseClass.GetRootAsPolygonValuesResponse(
        bytearray(await response.read()), 0,
    )
    polygons_length = data.PolygonsLength()
    assert polygons_length == 2

    response = await web_app_client.post(
        '/v1/polygon/values', json={'groups': ['group1']},
    )
    data = await parse_response(response)
    polygons_length = len(data['polygons'])
    assert polygons_length == 1
    coordinates = data['polygons'][0]['coordinates']
    assert len(coordinates) == 1
    points = data['polygons'][0]['coordinates'][0]['points']
    assert len(points) == 4
    assert points[0]['lat'] == -2.0
    assert points[0]['lon'] == -1.0


@pytest.mark.filldb()
@pytest.mark.config(
    ORDER_EVENTS_PRODUCER_POLYGONS=[
        {
            'name': 'zone1',
            'groups': ['group1', 'group2'],
            'points': FIRST_POLYGON,
        },
        {
            'name': 'zone2',
            'enabled': False,
            'groups': ['group2', 'group3'],
            'points': SECOND_POLYGON,
        },
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    EVENTUS_ORCHESTRATOR_POLYGONS_SOURCE={'source': 'mongo'},
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EVENTUS_ORCHESTRATOR_POLYGONS_SOURCE={'source': 'config'},
                ),
            ],
        ),
    ],
)
async def test_update(taxi_eventus_orchestrator_web, taxi_config, mongo):
    source_mongo = (
        taxi_config.get('EVENTUS_ORCHESTRATOR_POLYGONS_SOURCE')['source']
        == 'mongo'
    )
    await taxi_eventus_orchestrator_web.post(
        '/tests/control', json={'now': TIMESTAMP.isoformat()},
    )
    res = await taxi_eventus_orchestrator_web.post(
        '/v1/polygon/values', json={'groups': ['group2']},
    )
    data = await parse_response(res)
    assert data['cursor']
    cursor = data['cursor']
    assert len(data['polygons']) == 2

    res = await taxi_eventus_orchestrator_web.post(
        '/v1/polygon/values', json={'groups': ['group2'], 'cursor': cursor},
    )
    data = await parse_response(res)
    assert data['cursor'] == cursor
    assert not data['polygons']
    if source_mongo:
        data_to_insert = {
            'name': 'zone3',
            'groups': ['group2', 'group3', 'group4'],
            'coordinates': {
                'type': 'Polygon',
                'coordinates': [
                    [points['coordinates'] for points in SECOND_POLYGON],
                ],
            },
        }
        res = await taxi_eventus_orchestrator_web.post(
            '/v1/polygon/modify', json=data_to_insert,
        )
        assert res.status == 200
    else:
        taxi_config.set_values(
            {
                'ORDER_EVENTS_PRODUCER_POLYGONS': [
                    {
                        'groups': ['group1', 'group2'],
                        'points': [{'coordinates': [22.0, 23.0]}],
                    },
                    {
                        'groups': ['group2', 'group3'],
                        'points': [{'coordinates': [122.0, 123.0]}],
                    },
                    {
                        'groups': ['group3', 'group4'],
                        'points': [{'coordinates': [22.0, 23.0]}],
                    },
                ],
            },
        )
    await taxi_eventus_orchestrator_web.tests_control(True)

    res = await taxi_eventus_orchestrator_web.post(
        '/v1/polygon/values', json={'groups': ['group2'], 'cursor': cursor},
    )
    data = await parse_response(res)
    assert data['cursor'] != cursor
    new_cursor = data['cursor']
    if source_mongo:
        assert len(data['polygons']) == 1
    else:
        assert len(data['polygons']) == 2

    res = await taxi_eventus_orchestrator_web.post(
        '/v1/polygon/values',
        json={'groups': ['group1'], 'cursor': new_cursor},
    )
    data = await parse_response(res)
    assert data['cursor'] != new_cursor
    assert len(data['polygons']) == 1
