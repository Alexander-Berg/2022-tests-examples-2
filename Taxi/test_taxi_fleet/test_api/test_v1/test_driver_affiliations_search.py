import aiohttp.web

from taxi.clients import personal
from testsuite.utils import http


async def test_success(
        web_app_client,
        headers,
        load_json,
        patch,
        mockserver,
        mock_unique_drivers,
        mock_driver_profiles,
        mock_fleet_parks,
):

    service_stub = load_json('service_success.json')
    unique_drivers_stub = load_json('unique_drivers_success.json')
    driver_profiles_stub = load_json('driver_profiles_success.json')
    fleet_parks_stub = load_json('fleet_parks_success.json')
    parks_stub = load_json('parks_success.json')

    @patch('taxi.clients.personal.PersonalApiClient.find')
    async def _find_pd_id(data_type, request_value, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES
        assert request_value == '00АА997949'
        return {
            'id': 'a9854e910c2d4c459c8f5b2e274694a0',
            'license': '00АА997949',
        }

    @mock_unique_drivers('/v1/driver/profiles/retrieve_by_license_pd_ids')
    async def _v1_driver_profiles_retrieve_by_license_pd_ids(
            request: http.Request,
    ):
        assert request.query == unique_drivers_stub['request']['query']
        assert request.json == unique_drivers_stub['request']['body']
        return aiohttp.web.json_response(unique_drivers_stub['response'])

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request: http.Request):
        assert request.query == driver_profiles_stub['request']['query']
        assert request.json == driver_profiles_stub['request']['body']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request: http.Request):
        assert request.json == fleet_parks_stub['request']['body']
        return aiohttp.web.json_response(fleet_parks_stub['response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == parks_stub['request']
        return aiohttp.web.json_response(parks_stub['response'])

    response = await web_app_client.post(
        '/api/v1/driver-affiliations/search-by-dl',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
