import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_transactions_api, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_transactions_api(
        '/v1/parks/transactions/categories/list/by-user',
    )
    async def _list_transaction_categories(request):
        assert request.json == stub['request']
        return aiohttp.web.json_response(stub['response'])

    response = await web_app_client.post(
        '/api/v1/transactions/categories/items',
        headers=headers,
        json={'is_enabled': True, 'is_editable': False},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
