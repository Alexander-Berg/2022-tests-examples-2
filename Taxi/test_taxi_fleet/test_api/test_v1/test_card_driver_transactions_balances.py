import aiohttp.web


async def test_success_driver(
        web_app_client,
        mock_parks,
        headers,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success_driver.json')

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _balances_list(request):
        assert request.json == stub['balances']['request']
        return aiohttp.web.json_response(stub['balances']['response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/transactions/balances',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']


async def test_success_driver_and_categories(
        web_app_client,
        mock_parks,
        headers,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success_driver_and_categories.json')

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _driver_balances_list(request):
        req = request.json

        balances = req['query']['balance']

        if balances.get('category_ids'):
            assert req == stub['balances_driver_categories']['request']
            return aiohttp.web.json_response(
                stub['balances_driver_categories']['response'],
            )

        assert req == stub['balances_driver']['request']
        return aiohttp.web.json_response(stub['balances_driver']['response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/transactions/balances',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
