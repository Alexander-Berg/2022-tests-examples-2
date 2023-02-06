import json

import pytest


ENDPOINT = '/driver/profile-view/v1/vehicles/branding'
BRANDING_ENDPOINT = '/fleet-vehicles/v1/vehicles/branding'
HEADERS = {
    'X-Driver-Session': 'session1',
    'User-Agent': 'Taximeter 8.80 (562)',
    'Accept-Language': 'ru',
}


@pytest.mark.experiments3(filename='experiments3_dvpbs_default.json')
@pytest.mark.parametrize(
    'db_id, branding_code, branding_response, expected_code',
    [
        ('db_id41', 200, {}, 403),
        pytest.param(
            'db_id42',
            200,
            {},
            403,
            marks=pytest.mark.driver_tags_match(
                dbid='db_id42', uuid='uuid1', tags=['selfemployed'],
            ),
        ),
        ('db_id42', 200, {}, 200),
        (
            'db_id42',
            404,
            {'code': 'NOT_FOUND', 'message': 'Vehicle is not found'},
            404,
        ),
        (
            'db_id42',
            400,
            {'code': 'BAD_REQUEST', 'message': 'Wrong request parameters'},
            500,
        ),
    ],
)
async def test_driver_vehicles_branding_put(
        taxi_driver_profile_view,
        mockserver,
        driver_authorizer,
        mock_fleet_parks_list,
        db_id,
        branding_code,
        branding_response,
        expected_code,
):
    driver_authorizer.set_session(db_id, 'session1', 'uuid1')

    @mockserver.json_handler(BRANDING_ENDPOINT)
    def _mock_branding(request):
        assert request.args == {'park_id': 'db_id42', 'vehicle_id': 'car1'}
        assert request.json == {
            'author': {
                'consumer': 'driver-profile-view',
                'identity': {'type': 'driver', 'driver_profile_id': 'uuid1'},
            },
            'branding': {'sticker': True, 'lightbox': False},
        }
        return mockserver.make_response(
            json.dumps(branding_response), branding_code,
        )

    response = await taxi_driver_profile_view.put(
        ENDPOINT,
        headers=HEADERS,
        params={'park_id': db_id, 'vehicle_id': 'car1'},
        data=json.dumps({'sticker': True, 'lightbox': False}),
    )

    assert response.status_code == expected_code
