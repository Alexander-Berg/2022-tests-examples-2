import pytest

from tests_fleet_orders_manager import common

ENDPOINT = 'fleet/fleet-orders-manager/v1/client-profile'
REQUEST_BODY = {'phone': 'phone', 'name': 'name'}


@pytest.fixture(name='profile')
def _mock_profile(mockserver):
    @mockserver.json_handler('/integration-api/v1/profile')
    def _mock(request):
        return {'user_id': 'user_id', 'name': 'name'}

    return _mock


async def test_ok(
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        personal_phones_store,
        v1_profile,
        profile,
):
    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': 'user_id',
        'name': 'name',
        'phone_pd_id': 'id_phone',
    }

    assert profile.times_called == 1
    profile_request = profile.next_call()['request']
    assert profile_request.json == {
        'user': {'personal_phone_id': 'id_phone'},
        'name': 'name',
    }
    assert (
        profile_request.headers['User-Agent'] == 'whitelabel/superweb/label_id'
    )


async def test_invalid_phone(
        mockserver,
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_phones_store(request):
        return mockserver.make_response(
            json={'code': '400', 'message': '400'}, status=400,
        )

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_phone',
        'message': 'invalid_phone',
    }
