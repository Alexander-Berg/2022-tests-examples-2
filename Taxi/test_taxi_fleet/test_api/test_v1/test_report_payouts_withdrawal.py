import aiohttp.web


async def test_success(
        web_app_client, headers, load_json, mock_fleet_payouts_py3,
):
    @mock_fleet_payouts_py3('/v1/parks/payouts/status')
    async def _v1_parks_payouts_status(request):
        stub = load_json('fleet_payouts__v1_parks_payouts_status.json')
        assert request.query == stub['request']
        return aiohttp.web.json_response(stub['response'])

    @mock_fleet_payouts_py3('/v1/parks/payouts/orders')
    async def _v1_parks_payouts_orders(request):
        stub = load_json('fleet_payouts__v1_parks_payouts_order_post.json')
        assert 'X-Idempotency-Token' in request.headers
        assert request.query == stub['request']['query']
        assert request.json == stub['request']['body']
        return aiohttp.web.json_response(stub['response'])

    response = await web_app_client.post(
        '/api/v1/reports/payouts/withdrawal',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4-e5-f6'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {}
