import aiohttp.web


async def test_success(
        web_app_client, headers, load_json, mock_fleet_rent_py3,
):

    service_stub = load_json('service_success.json')
    fleet_rent_stub = load_json('fleet_rent_success.json')

    @mock_fleet_rent_py3('/v1/park/rents/transactions/list')
    async def _v1_park_rents_transactions_list(request):
        assert request.query == fleet_rent_stub['request']['query']
        assert request.json == fleet_rent_stub['request']['body']
        return aiohttp.web.json_response(fleet_rent_stub['response'])

    response = await web_app_client.post(
        '/api/v1/regular-charges/details',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
