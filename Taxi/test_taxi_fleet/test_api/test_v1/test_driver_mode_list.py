import aiohttp.web
import pytest


@pytest.mark.config(
    TAXI_FLEET_DRIVER_MODE_TARIFF_ZONES={
        '7ad36bc7560449998acbe2c57a75c293': ['zone_1', 'zone_2'],
    },
)
async def test_success(
        web_app_client,
        headers,
        load_json,
        mock_driver_mode_subscription,
        mock_driver_profiles,
):
    stub = load_json('success.json')

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == stub['driver_profiles']['request']['query']
        assert request.json == stub['driver_profiles']['request']['body']
        return aiohttp.web.json_response(stub['driver_profiles']['response'])

    @mock_driver_mode_subscription('/v1/fleet/offers-list')
    async def _offers_list(request):
        assert request.json == stub['driver_mode']['request']
        return aiohttp.web.json_response(stub['driver_mode']['response'])

    response = await web_app_client.post(
        '/api/v1/driver-mode/list',
        headers=headers,
        json={'driver_id': 'driver_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']


@pytest.mark.config(
    TAXI_FLEET_DRIVER_MODE_TARIFF_ZONES={
        '7ad36bc7560449998acbe2c57a75c293': ['zone_1', 'zone_2'],
    },
)
async def test_bad_request(
        web_app_client, headers, load_json, mock_driver_profiles,
):

    stub = load_json('bad_request.json')

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == stub['driver_profiles']['request']['query']
        assert request.json == stub['driver_profiles']['request']['body']
        return aiohttp.web.json_response(stub['driver_profiles']['response'])

    response = await web_app_client.post(
        '/api/v1/driver-mode/list',
        headers=headers,
        json={'driver_id': 'driver_id'},
    )

    assert response.status == 400

    data = await response.json()
    data_keys = data.keys()
    assert 'code' in data_keys
    assert 'message' in data_keys
