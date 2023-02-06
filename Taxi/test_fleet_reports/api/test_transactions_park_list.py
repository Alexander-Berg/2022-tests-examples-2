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
        mock_parks,
        mock_api7,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success.json')

    @mock_fleet_transactions_api('/v1/parks/transactions/list')
    async def _list_parks_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['drivers']['api7_request']
        return aiohttp.web.json_response(stub['drivers']['api7_response'])

    response = await web_app_client.post(
        '/reports-api/v1/transactions/park/list',
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
            'limit': 1,
            'cursor': 'asd',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
