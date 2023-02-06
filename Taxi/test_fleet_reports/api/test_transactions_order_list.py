import datetime

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
        mock_api7,
        mock_fleet_transactions_api,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_order_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['drivers']['api7_request']
        return aiohttp.web.json_response(stub['drivers']['api7_response'])

    @patch('datetime.datetime.today')
    def _datetime_today():
        return datetime.datetime.fromisoformat('2019-12-10T20:00:00+03:00')

    response = await web_app_client.post(
        '/reports-api/v1/transactions/order/list',
        headers=headers,
        json={
            'query': {
                'park': {
                    'order': {'ids': ['aaq3bcras60d499f8ac57tc52aj8fs9p']},
                },
            },
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
