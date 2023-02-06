import aiohttp.web

from taxi.clients import personal


async def test_success(
        web_app_client,
        headers,
        load_json,
        patch,
        mock_fleet_rent_py3,
        mock_driver_profiles,
        mock_fleet_parks,
):

    service_stub = load_json('service_success.json')
    fleet_rent_stub = load_json('fleet_rent_success.json')
    driver_profiles_stub = load_json('driver_profiles_success.json')
    personal_stub = load_json('personal_success.json')
    fleet_parks_stub = load_json('fleet_parks_success.json')

    @mock_fleet_rent_py3('/v1/park/affiliations/list')
    async def _v1_park_affiliations(request):
        assert request.query == fleet_rent_stub['request']['query']
        assert request.json == fleet_rent_stub['request']['body']
        return aiohttp.web.json_response(fleet_rent_stub['response'])

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == driver_profiles_stub['request']['query']
        assert request.json == driver_profiles_stub['request']['body']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    @patch('taxi.clients.personal.PersonalApiClient.bulk_retrieve')
    async def _bulk_retrieve(data_type, request_ids, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES
        assert sorted(request_ids) == sorted(personal_stub['request'])
        return personal_stub['response']

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert request.json == fleet_parks_stub['request']
        return aiohttp.web.json_response(fleet_parks_stub['response'])

    response = await web_app_client.post(
        '/api/v1/driver-affiliations/list',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
