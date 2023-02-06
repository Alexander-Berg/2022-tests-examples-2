# flake8: noqa
import aiohttp.web
import pytest

from fleet_reports.stq import orders_download

TRANSLATIONS = {
    header['tanker_key']: {'ru': header['key'] + ' поле'}
    for header in orders_download.HEADERS
}


@pytest.mark.translations(opteum_card_driver=TRANSLATIONS)
async def test_success_csv(stq_runner, mockserver, testpoint, load):
    orders_stub = load('orders.csv')

    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        assert (
            request.get_data().decode(encoding='utf-8').replace('\r\n', '\n')
            == orders_stub
        )
        return None

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def _mock_do(request):
        return aiohttp.web.json_response(
            {
                'orders': [
                    {
                        'id': 'order_id_0',
                        'short_id': 123,
                        'status': 'complete',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'booked_at': '2020-01-01T00:00:00+00:00',
                        'provider': 'platform',
                        'address_from': {
                            'address': 'Street hail: Russia, Moscow, Troparyovsky Forest Park',
                            'lat': 55.734803,
                            'lon': 37.643132,
                        },
                        'amenities': [],
                        'events': [],
                        'route_points': [],
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
        )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    async def _mock_fta_transactions(request):
        return aiohttp.web.json_response(
            {
                'transactions': [
                    {
                        'amount': '268.0000',
                        'category_id': 'cash_collected',
                        'category_name': 'cash_collected',
                        'created_by': {'identity': 'platform'},
                        'currency_code': 'RUB',
                        'description': 'text',
                        'event_at': '2019-01-02T00:00:05+03:00',
                        'id': '120932b5a48b4dtca707fa9abfh66jab',
                        'order_id': 'd343a742c14f415db7bab9210b5cb837',
                    },
                ],
            },
        )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/transactions/categories/list/by-fleet-api',
    )
    async def _mock_fta_categories(request):
        return aiohttp.web.json_response(
            {
                'categories': [
                    {
                        'id': '120932b5a48b4dtca707fa9abfh66jab',
                        'name': 'category_name_0',
                        'group_id': 'd343a742c14f415db7bab9210b5cb837',
                        'group_name': 'group_name_0',
                        'is_affecting_driver_balance': True,
                        'is_creatable': True,
                        'is_editable': True,
                        'is_enabled': True,
                    },
                ],
            },
        )

    await stq_runner.fleet_reports_orders_download.call(
        task_id='1',
        args=(),
        kwargs={
            'request_data': {
                'date_type': 'ended_at',
                'date_from': '2020-01-01T00:00:00+00:00',
                'date_to': '2020-01-02T00:00:00+00:00',
            },
            'park_id': 'park_id_0',
            'park_timezone': 3,
            'accept_language': 'ru',
            'operation_id': 'base_operation_00000000000000001',
            'log_extra': {},
            'file_format': 'csv',
            'charset': 'utf-8',
        },
    )

    assert _mock_frs.times_called == 1
    assert _mock_do.times_called == 1
    assert _mock_fta_transactions.times_called == 1
    assert _mock_fta_categories.times_called == 1


async def test_success_xls(stq_runner, mockserver, testpoint):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def _mock_do(request):
        return aiohttp.web.json_response(
            {
                'orders': [
                    {
                        'id': 'order_id_0',
                        'short_id': 123,
                        'status': 'complete',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'booked_at': '2020-01-01T00:00:00+00:00',
                        'provider': 'platform',
                        'address_from': {
                            'address': 'Street hail: Russia, Moscow, Troparyovsky Forest Park',
                            'lat': 55.734803,
                            'lon': 37.643132,
                        },
                        'amenities': [],
                        'events': [],
                        'route_points': [],
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
        )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    async def _mock_fta_transactions(request):
        return aiohttp.web.json_response(
            {
                'transactions': [
                    {
                        'amount': '268.0000',
                        'category_id': 'cash_collected',
                        'category_name': 'cash_collected',
                        'created_by': {'identity': 'platform'},
                        'currency_code': 'RUB',
                        'description': 'text',
                        'event_at': '2019-01-02T00:00:05+03:00',
                        'id': '120932b5a48b4dtca707fa9abfh66jab',
                        'order_id': 'd343a742c14f415db7bab9210b5cb837',
                    },
                ],
            },
        )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/transactions/categories/list/by-fleet-api',
    )
    async def _mock_fta_categories(request):
        return aiohttp.web.json_response(
            {
                'categories': [
                    {
                        'id': '120932b5a48b4dtca707fa9abfh66jab',
                        'name': 'category_name_0',
                        'group_id': 'd343a742c14f415db7bab9210b5cb837',
                        'group_name': 'group_name_0',
                        'is_affecting_driver_balance': True,
                        'is_creatable': True,
                        'is_editable': True,
                        'is_enabled': True,
                    },
                ],
            },
        )

    await stq_runner.fleet_reports_orders_download.call(
        task_id='1',
        args=(),
        kwargs={
            'request_data': {
                'date_type': 'ended_at',
                'date_from': '2020-01-01T00:00:00+00:00',
                'date_to': '2020-01-02T00:00:00+00:00',
            },
            'park_id': 'park_id_0',
            'park_timezone': 3,
            'accept_language': 'ru',
            'operation_id': 'base_operation_00000000000000001',
            'log_extra': {},
            'file_format': 'xls',
            'charset': 'utf-8',
        },
    )

    assert _mock_frs.times_called == 1
    assert _mock_do.times_called == 1
    assert _mock_fta_transactions.times_called == 1
    assert _mock_fta_categories.times_called == 1
