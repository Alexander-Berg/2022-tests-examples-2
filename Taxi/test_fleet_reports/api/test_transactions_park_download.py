import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        mock_parks,
        mock_api7,
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

    @mock_fleet_transactions_api('/v1/parks/transactions/list')
    async def _list_parks_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['drivers']['api7_request']
        return aiohttp.web.json_response(stub['drivers']['api7_response'])

    response = await web_app_client.post(
        '/reports-api/v1/transactions/park/download',
        headers=headers,
        json={
            'query': {
                'park': {
                    'transaction': {
                        'event_at': {
                            'from': '2019-09-08T11:16:11+00:00',
                            'to': '2019-09-09T11:16:11+00:00',
                        },
                        'category_ids': [
                            'fleet_ride_fee',
                            'platform_ride_fee',
                        ],
                    },
                },
            },
        },
    )

    assert response.status == 200
