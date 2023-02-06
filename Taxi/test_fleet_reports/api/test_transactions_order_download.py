import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        mock_parks,
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

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_order_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    response = await web_app_client.post(
        '/reports-api/v1/transactions/order/download',
        headers=headers,
        json={
            'query': {
                'park': {
                    'order': {'ids': ['293a821804555a5fa7da56f8101d4ab9']},
                },
            },
        },
    )

    assert response.status == 200
