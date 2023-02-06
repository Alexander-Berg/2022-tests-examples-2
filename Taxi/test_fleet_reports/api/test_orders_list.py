import aiohttp.web
import pytest


async def _test_func(
        web_app_client,
        headers,
        mock_driver_orders,
        mock_fleet_transactions_api,
        stub,
):
    @mock_driver_orders('/v1/parks/orders/list')
    async def _list_orders(request):
        orders = stub['orders']
        assert request.json == orders['driver_orders_request']
        return aiohttp.web.json_response(orders['driver_orders_response'])

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_order_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    @mock_fleet_transactions_api(
        '/v1/parks/transactions/categories/list/by-user',
    )
    async def _list_transaction_categories(request):
        assert request.json == stub['transaction-categories']['request']
        return aiohttp.web.json_response(
            stub['transaction-categories']['response'],
        )

    response = await web_app_client.post(
        '/reports-api/v1/orders/list',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == stub['service']['response_code']

    data = await response.json()
    assert data == stub['service']['response']


@pytest.mark.parametrize(
    'stub_file_name', ['success.json', 'date_validation.json'],
)
async def test_by_stubs(
        web_app_client,
        headers,
        mock_driver_orders,
        mock_fleet_transactions_api,
        load_json,
        stub_file_name,
):
    stub = load_json(stub_file_name)

    await _test_func(
        web_app_client,
        headers,
        mock_driver_orders,
        mock_fleet_transactions_api,
        stub,
    )


CANCELLATION_DESCRIPTION_KEYS = {'user': 'user'}


@pytest.mark.config(
    DRIVER_ORDERS_CANCELLATION_DESCRIPTION_KEYS=CANCELLATION_DESCRIPTION_KEYS,
)
@pytest.mark.parametrize(
    'is_support, stub_file_name',
    [
        (False, 'success_cancellation_description.json'),
        (True, 'success_cancellation_description_support.json'),
    ],
)
async def test_cancellation_description(
        web_app_client,
        headers,
        headers_support,
        mock_driver_orders,
        mock_fleet_transactions_api,
        load_json,
        is_support,
        stub_file_name,
):
    test_headers = headers_support if is_support else headers
    stub = load_json(stub_file_name)

    await _test_func(
        web_app_client,
        test_headers,
        mock_driver_orders,
        mock_fleet_transactions_api,
        stub,
    )
