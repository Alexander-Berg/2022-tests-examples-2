import aiohttp.web


async def test_success(
        web_app_client,
        mock_parks,
        mockserver,
        headers,
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

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/transactions/list')
    async def _list_drivers_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == stub['drivers']['parks_request']
        return aiohttp.web.json_response(stub['drivers']['parks_response'])

    response = await web_app_client.post(
        '/api/v1/reports/transactions/driver/download',
        headers=headers,
        json={
            'query': {
                'park': {
                    'driver_profile': {
                        'id': '769ce26febec46b0a16eee7a560d7eda',
                    },
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
