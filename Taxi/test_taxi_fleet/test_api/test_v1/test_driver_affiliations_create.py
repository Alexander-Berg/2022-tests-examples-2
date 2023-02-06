import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_rent_py3, load_json,
):

    service_stub = load_json('service_success.json')
    fleet_rent_stub = load_json('fleet_rent_success.json')

    @mock_fleet_rent_py3('/v1/park/affiliations/')
    async def _v1_park_affiliations(request):
        assert request.json == fleet_rent_stub['request']
        return aiohttp.web.json_response(fleet_rent_stub['response'])

    response = await web_app_client.post(
        '/api/v1/driver-affiliations/create',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
