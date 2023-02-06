from aiohttp import web
import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import get_order_info
from order_notify.repositories.order_info import OrderData
from test_order_notify.util import get_bson_order_data

ORDERS_PROC = [
    {'_id': '2', 'code': 'fffff111'},
    {'_id': '4', 'code': 'wclon23t'},
]
ORDERS = [
    {'_id': '3', 'code': 'lkb23bhk'},
    {'_id': '4', 'code': 'wclon23t', 'nz': 'moscow'},
]


@pytest.fixture(name='mock_server')
def mock_server_fixture(mockserver, load_json):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    async def order_archive_handler(request):
        bson_order_proc = get_bson_order_data(db=ORDERS_PROC, request=request)
        if bson_order_proc:
            return mockserver.make_response(
                response=bson_order_proc,
                content_type='application/x-bson-binary',
            )
        return mockserver.make_response('Not Found', status=404)

    @mockserver.json_handler('/archive-api/archive/order')
    def archive_api_handler(request):
        bson_order = get_bson_order_data(db=ORDERS, request=request)
        if bson_order:
            return web.Response(
                body=bson_order, headers={'Content-Type': 'application/bson'},
            )
        return web.json_response({}, status=404)

    class Counter:
        def __init__(self):
            self.order_archive_handler = order_archive_handler
            self.archive_api_handler = archive_api_handler

    return Counter()


@pytest.mark.parametrize(
    'order_id, expected_order',
    [
        pytest.param('1', None, id='no_order_and_order_proc'),
        pytest.param('2', None, id='no_order_but_order_proc_exists'),
        pytest.param('3', None, id='order_exists_but_no_order_proc'),
        pytest.param(
            '4',
            OrderData(
                brand='yataxi',
                country='rus',
                order=ORDERS[1],
                order_proc=ORDERS_PROC[1],
            ),
            id='order_and_order_proc_exists',
        ),
    ],
)
async def test_get_order_info(
        stq3_context: stq_context.Context,
        mock_server,
        mock_tariff_zones,
        order_id,
        expected_order,
):
    order = await get_order_info(context=stq3_context, order_id=order_id)
    assert order == expected_order
