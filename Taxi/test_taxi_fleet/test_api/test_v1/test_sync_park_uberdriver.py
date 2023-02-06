import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_synchronizer, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_synchronizer('/v1/sync/park')
    async def _sync_park(request):
        assert request.json == stub['api_request']
        return aiohttp.web.json_response(stub['api_response'])

    response = await web_app_client.post(
        '/api/v1/sync/park/uberdriver', headers=headers, json={},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_forbidden(
        web_app_client, headers, mock_fleet_synchronizer, load_json,
):

    stub = load_json('forbidden.json')

    @mock_fleet_synchronizer('/v1/sync/park')
    async def _sync_park(request):
        assert request.json == stub['api_request']
        return aiohttp.web.json_response(
            status=403,
            data=stub['api_response'],
            headers={'X-YaTaxi-Error-Code': 'forbidden'},
        )

    response = await web_app_client.post(
        '/api/v1/sync/park/uberdriver', headers=headers, json={},
    )

    assert response.status == 403

    data = await response.json()
    assert data == stub['service_response']
