import json

import pytest


ENDPOINT = '/driver/profile-view/v1/drivers/child-chairs'
CHILD_CHAIRS_ENDPOINT = '/fleet-vehicles/v1/vehicles/driver/child-chairs'
HEADERS = {
    'X-Driver-Session': 'session1',
    'User-Agent': 'Taximeter 8.80 (562)',
    'Accept-Language': 'ru',
}


@pytest.mark.experiments3(filename='experiments3_dvpbs_default.json')
@pytest.mark.parametrize(
    'db_id, boosters_count, child_chairs_code, child_chairs_response, '
    'expected_code',
    [
        ('db_id41', 1, 200, {}, 403),
        pytest.param(
            'db_id42',
            1,
            200,
            {},
            403,
            marks=pytest.mark.driver_tags_match(
                dbid='db_id42', uuid='uuid1', tags=['selfemployed'],
            ),
        ),
        ('db_id42', 1, 200, {}, 200),
        (
            'db_id42',
            2,
            200,
            {
                'code': 'BAD_REQUEST',
                'message': 'Wrong limits: chairs: 1, boosters: 1',
            },
            400,
        ),
        (
            'db_id42',
            1,
            404,
            {'code': 'NOT_FOUND', 'message': 'Vehicle is not found'},
            404,
        ),
        (
            'db_id42',
            1,
            400,
            {'code': 'BAD_REQUEST', 'message': 'Wrong request parameters'},
            500,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_CHILD_CHAIRS_SETTINGS={
        'brand': 'Other',
        'categories': [0, 1, 2, 3],
        'isofix': False,
    },
)
async def test_driver_child_chairs_put(
        taxi_driver_profile_view,
        mockserver,
        driver_authorizer,
        fleet_parks,
        mock_fleet_parks_list,
        db_id,
        boosters_count,
        child_chairs_code,
        child_chairs_response,
        expected_code,
):
    driver_authorizer.set_session(db_id, 'session1', 'uuid1')

    @mockserver.json_handler(CHILD_CHAIRS_ENDPOINT)
    def _mock_child_chairs(request):
        assert request.args == {
            'park_id': 'db_id42',
            'driver_profile_id': 'uuid1',
            'vehicle_id': 'car1',
        }
        assert request.json == {
            'author': {
                'consumer': 'driver-profile-view',
                'identity': {'type': 'driver', 'driver_profile_id': 'uuid1'},
            },
            'child_chairs': {
                'boosters_count': boosters_count,
                'chairs': [
                    {
                        'brand': 'Other',
                        'categories': [0, 1, 2, 3],
                        'isofix': False,
                    },
                ],
            },
        }
        return mockserver.make_response(
            json.dumps(child_chairs_response), child_chairs_code,
        )

    response = await taxi_driver_profile_view.put(
        ENDPOINT,
        headers=HEADERS,
        params={'park_id': db_id, 'vehicle_id': 'car1'},
        json={'boosters_count': boosters_count, 'chairs_count': 1},
    )

    assert response.status_code == expected_code
