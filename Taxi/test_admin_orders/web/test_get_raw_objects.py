import json
import os

import aiohttp.web
import bson
import pytest

RESPONSES_DIR = os.path.join(
    os.path.dirname(__file__), 'static', 'test_get_raw_objects', 'responses',
)


@pytest.fixture
def taxi_admin_orders_mocks(mockserver, load_json, order_archive_mock):
    """Put your mocks here"""
    cache = {}
    for object_name in ['order', 'order_proc']:
        doc = load_json(
            f'responses/archive-api_archive_{object_name}.bson.json',
        )
        cache[object_name] = doc
        if object_name == 'order_proc':
            order_archive_mock.set_order_proc(doc['doc'])

    cache['setcar'] = load_json('responses/order-misc-api_setcars.json')
    cache['order_core_get_order_proc'] = load_json(
        'responses/order_core_get_order_proc.bson.json',
    )
    cache['invoices_archive_get_order'] = load_json(
        'responses/invoices_archive_get_order.bson.json',
    )

    @mockserver.handler('/archive-api/archive/', prefix=True)
    def _get_archive_order(request):
        object_name = request.path_qs[len('/archive-api/archive/') :]
        response = bson.BSON.encode(cache[object_name])
        return aiohttp.web.Response(
            body=response, headers={'Content-Type': 'application/bson'},
        )

    @mockserver.handler(
        '/driver-order-misc/internal/driver-order-misc/v1/fetch-setcar',
        prefix=True,
    )  # noqa: E501
    def _get_setcars(request):
        return mockserver.make_response(json=cache['setcar'])

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-order',
    )
    def _order_core_get_order_proc(request):
        response_body = cache['order_core_get_order_proc']
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_body),
        )

    @mockserver.handler('/invoices-archive/v1/orders/get-order')
    def _invoices_archive_get_order(request):
        response_body = cache['invoices_archive_get_order']
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_body),
        )


@pytest.mark.config(TVM_RULES=[{'dst': 'archive-api', 'src': 'admin-orders'}])
@pytest.mark.usefixtures('taxi_admin_orders_mocks')
async def test_get_raw_objects(taxi_admin_orders_web, load_json):

    expected_filename = os.path.join(
        RESPONSES_DIR, 'admin_orders_v1_raw_objects_get.json',
    )
    with open(expected_filename) as f_obj:
        expected_response = json.load(f_obj)

    response = await taxi_admin_orders_web.get(
        '/v1/raw_objects/get/?order_id=0fc10c193bbb32fa97ea5fc7cca95455'
        '&objects=order,order_proc,setcars',
    )
    content = await response.json()
    assert content == expected_response


@pytest.mark.config(TVM_RULES=[{'dst': 'archive-api', 'src': 'admin-orders'}])
@pytest.mark.usefixtures('taxi_admin_orders_mocks')
async def test_get_raw_objects_anonimyzed(taxi_admin_orders_web, load_json):

    expected_filename = os.path.join(
        RESPONSES_DIR, 'admin_orders_v1_raw_objects_get_anonymized.json',
    )
    with open(expected_filename) as f_obj:
        expected_response = json.load(f_obj)

    response = await taxi_admin_orders_web.get(
        '/v1/raw_objects/get/?order_id=0fc10c193bbb32fa97ea5fc7cca95455'
        '&objects=order,order_proc,setcars&deanonymize=true',
    )
    content = await response.json()
    assert content == expected_response
