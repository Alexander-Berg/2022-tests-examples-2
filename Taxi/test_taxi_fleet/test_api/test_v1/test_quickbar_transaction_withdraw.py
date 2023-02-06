import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_transactions_api, load_json,
):
    fleet_transactions_api_stub = load_json('fleet_transactions_api.json')
    service_stub = load_json('service.json')

    @mock_fleet_transactions_api(
        '/v1/parks/driver-profiles/transactions/by-user',
    )
    async def _v1_parks_driver_profiles_transactions_by_user(request):
        assert request.json == fleet_transactions_api_stub['request']
        return aiohttp.web.json_response(
            fleet_transactions_api_stub['response'],
        )

    response = await web_app_client.post(
        '/api/v1/quickbar/transaction/withdraw',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4-e5-f6'},
        json=service_stub['request'],
    )

    assert response.status == 200


async def test_amount_zero(web_app_client, headers, load_json):
    service_stub = load_json('service.json')
    service_stub['request']['amount'] = '0'

    response = await web_app_client.post(
        '/api/v1/quickbar/transaction/withdraw',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4-e5-f6'},
        json=service_stub['request'],
    )

    assert response.status == 400
