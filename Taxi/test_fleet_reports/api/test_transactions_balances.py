import aiohttp.web
import pytest


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS={
        'chunk_size': 12,
        'concurrency': 2,
        'truncated_to_hours_offset': 168,
    },
)
async def test_success_driver(
        web_app_client, headers, mock_fleet_transactions_api, load_json,
):
    stub = load_json('success_driver.json')

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _balances_list(request):
        assert request.json == stub['balances']['request']
        return aiohttp.web.json_response(stub['balances']['response'])

    response = await web_app_client.post(
        '/reports-api/v1/transactions/balances',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS={
        'chunk_size': 12,
        'concurrency': 2,
        'truncated_to_hours_offset': 168,
    },
)
async def test_success_driver_and_categories(
        web_app_client, headers, mock_fleet_transactions_api, load_json,
):

    stub = load_json('success_driver_and_categories.json')

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _driver_balances_list(request):
        req = request.json

        balances = req['query']['balance']

        if balances.get('category_ids'):
            assert req == stub['balances_driver_categories']['request']
            return aiohttp.web.json_response(
                stub['balances_driver_categories']['response'],
            )  # noqa

        assert req == stub['balances_driver']['request']
        return aiohttp.web.json_response(stub['balances_driver']['response'])

    response = await web_app_client.post(
        '/reports-api/v1/transactions/balances',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS={
        'chunk_size': 12,
        'concurrency': 2,
        'truncated_to_hours_offset': 168,
    },
)
async def test_success_categories(
        web_app_client, headers, mock_fleet_transactions_api, load_json,
):

    stub = load_json('success_categories.json')

    @mock_fleet_transactions_api('/v1/parks/balances/list')
    async def _park_balances_list(request):
        assert request.json == stub['balances_categories']['request']
        return aiohttp.web.json_response(
            stub['balances_categories']['response'],
        )

    response = await web_app_client.post(
        '/reports-api/v1/transactions/balances',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS={
        'chunk_size': 12,
        'concurrency': 2,
        'truncated_to_hours_offset': 168,
    },
)
async def test_400(
        web_app_client, headers, mock_fleet_transactions_api, load_json,
):
    response = await web_app_client.post(
        '/reports-api/v1/transactions/balances',
        headers=headers,
        json={
            'accrued_at': [
                '2019-09-23T00:12:00+03:00',
                '2019-09-24T23:00:00+03:00',
            ],
            'driver_id': 'aab36cr7560d499f8acbe2c52a7j7n9p',
        },
    )

    assert response.status == 400
    assert await response.json() == {
        'code': 'BAD_REQUEST',
        'message': 'date 2019-09-22 21:12:00 must be truncated to hours',
    }
