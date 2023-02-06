import aiohttp.web


async def test_success(
        web_app_client, headers, load_json, mock_fleet_payouts_py3,
):

    service_stub = load_json('service.json')

    @mock_fleet_payouts_py3('/v1/parks/payouts/status')
    async def _v1_parks_payouts_status(request):
        stub = load_json('fleet_payouts__v1_parks_payouts_status.json')
        assert request.query == stub['request']
        return aiohttp.web.json_response(stub['response'])

    response = await web_app_client.post(
        '/api/v1/reports/payouts/partner/balance', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
