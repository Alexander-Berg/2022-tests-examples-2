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
RECTANGLE = [[0.0, 1.0], [1.0, 0.0]]
RECTANGLE_2 = [[1.0, 2.0], [2.0, 1.0]]
RECTANGLE_3 = [[0.0, 3.0], [3.0, 0.0]]


@pytest.mark.parametrize(
    'data, expected_status',
    [
        ({'groups': []}, 400),
        ({'names': []}, 200),
        ({'bounding_box': [[2.0], [3.1]]}, 400),
        ({'bounding_box': [[2.0], [3.1]]}, 400),
        ({'bounding_box': RECTANGLE}, 200),
    ],
)
async def test_base(web_app_client, data, expected_status):
    response = await web_app_client.post(
        '/v1/service/polygon/values', json=data,
    )
    assert response.status == expected_status


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'bounding_box, groups, expected_response_length',
    [
        (RECTANGLE, [], 1),
        (RECTANGLE_2, [], 0),
        (RECTANGLE_3, [], 2),
        (RECTANGLE_3, ['group1'], 1),
    ],
)
async def test_handle(
        web_app_client, bounding_box, groups, expected_response_length,
):
    response = await web_app_client.post(
        '/v1/service/polygon/values',
        json={'bounding_box': bounding_box, 'groups': groups},
    )
    data = await response.json()
    assert response.status == 200
    assert len(data['items']) == expected_response_length


@pytest.mark.filldb()
@pytest.mark.parametrize('enabled', [True, False])
async def test_filter(web_app_client, enabled):
    expected_response_length = 1 if enabled is not None else 2
    response = await web_app_client.post(
        '/v1/service/polygon/values',
        json={'bounding_box': RECTANGLE_3, 'enabled': enabled},
    )
    data = await response.json()
    assert response.status == 200
    assert len(data['items']) == expected_response_length


@pytest.mark.filldb()
async def test_name(web_app_client):
    response = await web_app_client.post(
        '/v1/service/polygon/values', json={'names': ['zone1']},
    )
    data = await response.json()
    assert response.status == 200
    assert len(data['items']) == 1
    assert data['items'][0] == {
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
    }
