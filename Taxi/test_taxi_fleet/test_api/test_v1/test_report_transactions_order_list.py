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
        mockserver,
        mock_fleet_transactions_api,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_order_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == stub['drivers']['parks_request']
        return aiohttp.web.json_response(stub['drivers']['parks_response'])

    @patch('datetime.datetime.today')
    def _datetime_today():
        return datetime.datetime.fromisoformat('2019-12-10T20:00:00+03:00')

    response = await web_app_client.post(
        '/api/v1/reports/transactions/order/list',
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
