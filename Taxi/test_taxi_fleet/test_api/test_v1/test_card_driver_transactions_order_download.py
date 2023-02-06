import aiohttp.web


async def test_success(
        web_app_client,
        mock_parks,
        headers,
        mockserver,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success.json')

    @mock_fleet_transactions_api(
        '/v1/parks/transactions/categories/list/by-user',
    )
    async def _list_transaction_categories(request):
        assert request.json == stub['categories']['request']
        return aiohttp.web.json_response(stub['categories']['response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == stub['drivers']['parks_request']
        return aiohttp.web.json_response(stub['drivers']['parks_response'])

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_orders_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/transactions/order/download',
        headers=headers,
        json={
            'query': {
                'park': {
                    'order': {'id': '293a821804555a5fa7da56f8101d4ab9'},
                    'driver_profile': {
                        'id': 'baw9fja3bran0l99fjac27tct2hjbfs1p',
                    },
                },
            },
        },
    )

    assert response.status == 200
