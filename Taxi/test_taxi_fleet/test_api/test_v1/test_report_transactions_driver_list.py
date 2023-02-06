import aiohttp.web
import pytest

TRANSLATIONS = {
    'created_by.platform': {'ru': 'Platform'},
    'created_by.techsupport': {'ru': 'Tech-Support'},
    'created_by.fleet': {'ru': 'Fleet-Api, Key'},
    'created_by.dispatcher': {'ru': 'Dispatchecr'},
}


@pytest.mark.translations(backend_fleet_reports=TRANSLATIONS)
async def test_success(
        web_app_client,
        headers,
        mockserver,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success.json')

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/transactions/list')
    async def _list_drivers_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == stub['drivers']['parks_request']
        return aiohttp.web.json_response(stub['drivers']['parks_response'])

    response = await web_app_client.post(
        '/api/v1/reports/transactions/driver/list',
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
                    'driver_profile': {
                        'id': 'aab36cr7560d499f8acbe2c52a7j7n9p',
                    },
                },
            },
            'limit': 2,
            'cursor': 'asd',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
