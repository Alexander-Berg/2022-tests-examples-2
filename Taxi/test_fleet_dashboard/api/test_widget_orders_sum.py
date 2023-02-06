import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_transactions_api, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_transactions_api('/v1/parks/balances/list')
    async def _balances_groups_list(request):
        assert request.json == stub['balances']['request']
        return aiohttp.web.json_response(stub['balances']['response'])

    response = await web_app_client.post(
        '/dashboard-api/v1/widget/orders-sum',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
