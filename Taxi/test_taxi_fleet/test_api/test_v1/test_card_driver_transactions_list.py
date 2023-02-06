import aiohttp.web
import pytest

TRANSLATIONS = {
    'created_by.platform': {'ru': 'Platform'},
    'created_by.techsupport': {'ru': 'Tech-Support'},
    'created_by.fleet': {'ru': 'Fleet-Api, Key'},
    'created_by.dispatcher': {'ru': 'Dispatchecr'},
}


@pytest.mark.translations(backend_fleet_reports=TRANSLATIONS)
async def _test_func(
        stub_file_name,
        web_app_client,
        headers,
        mockserver,
        mock_billing_reports,
        mock_fleet_transactions_api,
        load_json,
        request_json,
):
    stub = load_json(stub_file_name)

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

    @mock_billing_reports('/v1/balances/select')
    async def _balances(request):
        assert request.json == stub['balances']['ba_request']
        return aiohttp.web.json_response(stub['balances']['ba_response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/transactions/list',
        headers=headers,
        json=request_json,
    )

    assert response.status == 200
    assert await response.json() == stub['service_response']


@pytest.mark.translations(backend_fleet_reports=TRANSLATIONS)
async def test_success(
        web_app_client,
        mock_parks,
        mock_territories_countries_list,
        headers,
        mockserver,
        mock_billing_reports,
        mock_fleet_transactions_api,
        load_json,
):
    await _test_func(
        'success.json',
        web_app_client,
        headers,
        mockserver,
        mock_billing_reports,
        mock_fleet_transactions_api,
        load_json,
        request_json={
            'query': {
                'park': {
                    'transaction': {
                        'event_at': {
                            'from': '2019-09-08T11:16:11+00:00',
                            'to': '2019-09-09T11:16:11+00:00',
                        },
                        'category_ids': ['card', 'platform_ride_fee'],
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


@pytest.mark.translations(backend_fleet_reports=TRANSLATIONS)
async def test_success_with_column_balance(
        web_app_client,
        mock_parks,
        mock_territories_countries_list,
        headers,
        mockserver,
        mock_billing_reports,
        mock_fleet_transactions_api,
        load_json,
):
    await _test_func(
        'success_column_balance.json',
        web_app_client,
        headers,
        mockserver,
        mock_billing_reports,
        mock_fleet_transactions_api,
        load_json,
        request_json={
            'query': {
                'park': {
                    'transaction': {
                        'event_at': {
                            'from': '2019-09-08T11:16:11+00:00',
                            'to': '2019-09-09T11:16:11+00:00',
                        },
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


@pytest.mark.translations(backend_fleet_reports=TRANSLATIONS)
async def test_success_with_zero_final_balance(
        web_app_client,
        mock_parks,
        mock_territories_countries_list,
        headers,
        mockserver,
        mock_billing_reports,
        mock_fleet_transactions_api,
        load_json,
):
    await _test_func(
        'success_zero_balance.json',
        web_app_client,
        headers,
        mockserver,
        mock_billing_reports,
        mock_fleet_transactions_api,
        load_json,
        request_json={
            'query': {
                'park': {
                    'transaction': {
                        'event_at': {
                            'from': '2019-09-08T11:16:11+00:00',
                            'to': '2019-09-09T11:16:11+00:00',
                        },
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
