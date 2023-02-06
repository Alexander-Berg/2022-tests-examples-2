# pylint:disable=no-member
# type: ignore
import pytest

from eventus_orchestrator.common import schemas

POLYGON_NAME_1 = 'zone1'
GROUP_1 = 'lavka'
GROUP_2 = 'yandex'
RECTANGLE = [[0.0, 0.0], [3.0, 6.0], [6.0, 1.0], [0.0, 0.0]]
#  end != start
WRONG_RECTANGLE = [[0.0, 0.0], [3.0, 6.0], [6.0, 1.0], [0.0, 10.0]]
#  self intersection
WRONG_RECTANGLE_2 = [
    [0.0, 0.0],
    [1.0, 1.0],
    [1.0, 3.0],
    [2.0, 3.0],
    [0.0, 1.0],
    [0.0, 0.0],
]
INNER_RECTANGLE = [[2.0, 2.0], [3.0, 3.0], [4.0, 2.0], [2.0, 2.0]]


async def test_base(web_app_client, mongo):
    response = await web_app_client.post(
        '/v1/polygon/modify', json={'groups': []},
    )
    assert response.status == 400

    response = await web_app_client.post(
        '/v1/polygon/modify', json={'name': POLYGON_NAME_1},
    )
    assert response.status == 200
    data = await mongo.eventus_polygons.find_one({})
    assert data
    assert data['name'] == POLYGON_NAME_1
    assert not data['enabled']


async def test_update(web_app_client, mongo):
    res = await web_app_client.post(
        '/v1/polygon/modify',
        json={
            'name': POLYGON_NAME_1,
            'groups': [GROUP_1],
            'coordinates': {'coordinates': [RECTANGLE], 'type': 'Polygon'},
        },
    )
    assert res.status == 200
    data = await mongo.eventus_polygons.find_one(
        {schemas.PolygonSchema.name: POLYGON_NAME_1},
    )
    assert data['groups'] == [GROUP_1]
    assert data['geo_object'] == {
        'type': 'Polygon',
        'coordinates': [RECTANGLE],
    }

    res = await web_app_client.post(
        '/v1/polygon/modify',
        json={
            'name': POLYGON_NAME_1,
            'coordinates': {
                'coordinates': [RECTANGLE, INNER_RECTANGLE],
                'type': 'Polygon',
            },
            'enabled': True,
        },
    )
    assert res.status == 200

    data = await mongo.eventus_polygons.find_one(
        {schemas.PolygonSchema.name: POLYGON_NAME_1},
    )
    assert data['groups'] == [GROUP_1]
    assert data['geo_object'] == {
        'type': 'Polygon',
        'coordinates': [RECTANGLE, INNER_RECTANGLE],
    }
    assert data['enabled']


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'polygon, expected_status',
    [(WRONG_RECTANGLE, 400), (WRONG_RECTANGLE_2, 400), (RECTANGLE, 200)],
)
async def test_polygon_modify_check(web_app_client, polygon, expected_status):
    data = {
        'name': POLYGON_NAME_1,
        'coordinates': {'coordinates': [polygon], 'type': 'Polygon'},
        'enabled': True,
    }
    response = await web_app_client.post('/v1/polygon/modify/check', json=data)
    assert response.status == expected_status

    if expected_status > 200:
        return

    response_data = await response.json()
    assert response_data['data'] == data
    assert response_data['diff'] == {
        'new': data,
        'current': {
            'coordinates': {
                'coordinates': [
                    [[-1.0, -1.0], [-1.0, 2.0], [1.0, -2.0], [-1.0, -1.0]],
                ],
                'type': 'Polygon',
            },
            'enabled': False,
            'groups': ['group1', 'group2'],
            'metadata': {},
            'name': 'zone1',
        },
    }
