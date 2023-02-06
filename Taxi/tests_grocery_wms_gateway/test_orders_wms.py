import copy
import json


import pytest

from tests_grocery_wms_gateway import consts

ORDER_REVISION = '1'


@pytest.mark.parametrize(
    'suffix, price_type, count',
    [['', 'store', 4], [':st-md', 'markdown', 4], [':st-pa', None, 1]],
)
async def test_create(
        taxi_grocery_wms_gateway,
        mockserver,
        suffix,
        price_type,
        count,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )
    short_id = 'short-id'

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/create')
    def mock_wms(request):
        item = {
            'product_id': 'item_id',
            'count': count,
            'price': '137',
            'price_unit': 1,
            'price_type': price_type,
        }
        if suffix == ':st-pa':
            item = {'item_id': 'item_id', 'count': 1}
        assert request.json == {
            'store_id': consts.DEFAULT_WMS_DEPOT_ID,
            'required': [item],
            'timeout_approving': 1800,
            'total_price': '73591',
            'external_id': 'external_order_id',
            'client_id': 'customer_id',
            'client_comment': 'Spanish inquisition',
            'client_phone_id': 'peronal_phone_id',
            'approved': True,
            'editable': True,
            'doc_number': short_id,
            'delivery_promise': 15,
            'client_address': {
                'fullname': 'Over the rainbow',
                'lat': 12.3,
                'lon': 31.2,
            },
            'external_order_revision': ORDER_REVISION,
            'maybe_rover': True,
            'client_tags': ['test_tag'],
            'logistic_tags': ['logistic_tag'],
        }

        return {
            'order': {
                'order_id': 'wms_order_id',
                'external_id': 'external_order_id',
                'status': 'reserving',
                'store_id': consts.DEFAULT_WMS_DEPOT_ID,
            },
        }

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/add',
        json={
            'organization': 'depot_id',
            'customer': {
                'id': 'customer_id',
                'comment': 'Spanish inquisition',
                'personal_phone_id': 'peronal_phone_id',
            },
            'order': {
                'id': 'external_order_id',
                'short_id': short_id,
                'date': 'date string',
                'fullSum': '73591.00',
                'items': [
                    {
                        'id': 'item_id' + suffix,
                        'name': 'name',
                        'amount': str(count),
                        'sum': '137.00',
                    },
                ],
                'delivery_eta': 15,
                'delivery_address': {
                    'full_address': 'Over the rainbow',
                    'lat': 12.3,
                    'lon': 31.2,
                },
                'maybe_rover': True,
                'client_tags': ['test_tag'],
                'logistic_tags': ['logistic_tag'],
            },
            'order_revision': ORDER_REVISION,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'success': 1,
        'data': {
            'createdObjects': [],
            'updatedObjects': [],
            'orderInfo': {
                'orderId': 'external_order_id',
                'customer': {'id': 'customer_id'},
                'organization': consts.DEFAULT_DEPOT_ID,
                'sum': 0,
                'status': 'New',
                'items': [
                    {
                        'id': 'item_id' + suffix,
                        'name': 'name',
                        'amount': str(count),
                        'sum': '137',
                    },
                ],
            },
        },
    }

    assert mock_wms.times_called == 1


@pytest.mark.parametrize(
    'error_code, want_code',
    [(None, 500), (400, 400), (403, 500), (404, 500), (500, 500), (410, 409)],
)
async def test_create_wms_error(
        taxi_grocery_wms_gateway,
        mockserver,
        error_code,
        want_code,
        grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=consts.DEFAULT_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/create')
    def mock_wms(request):
        if not error_code:
            raise mockserver.NetworkError()
        elif error_code in (400, 410):
            return mockserver.make_response(
                '{"code": "bug", "message" :"fix your bugs"}', error_code,
            )
        else:
            return mockserver.make_response('{}', error_code)

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/add',
        json={
            'organization': consts.DEFAULT_DEPOT_ID,
            'customer': {'id': 'customer_id'},
            'order': {
                'id': 'external_order_id',
                'date': 'date string',
                'fullSum': '73591.00',
                'items': [
                    {
                        'id': 'item_id',
                        'name': 'name',
                        'amount': '4',
                        'sum': '137.00',
                    },
                ],
            },
        },
    )

    assert response.status_code == want_code
    assert mock_wms.times_called >= 1


async def test_create_wms_parcel_not_one(
        taxi_grocery_wms_gateway, mockserver, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=consts.DEFAULT_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/create')
    def mock_wms(request):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/add',
        json={
            'organization': consts.DEFAULT_DEPOT_ID,
            'customer': {'id': 'customer_id'},
            'order': {
                'id': 'external_order_id',
                'date': 'date string',
                'fullSum': '73591.00',
                'items': [
                    {
                        'id': 'item_id:st-pa',
                        'name': 'name',
                        'amount': '4',
                        'sum': '137.00',
                    },
                ],
            },
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'PARCEL_COUNT_NOT_ONE',
        'message': 'Count for parcel item_id should be 1, not 4',
    }
    assert mock_wms.times_called == 0


async def test_info(taxi_grocery_wms_gateway, mockserver, grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=consts.DEFAULT_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/get_status')
    def mock_wms(request):
        return {
            'order': {
                'order_id': 'wms_order_id',
                'external_id': 'external_order_id',
                'status': 'processing',
                'store_id': consts.DEFAULT_WMS_DEPOT_ID,
            },
        }

    await taxi_grocery_wms_gateway.invalidate_caches()

    uri = '/v1/orders/info'
    response = await taxi_grocery_wms_gateway.post(
        uri
        + '?organization={}&order=external_order_id'.format(
            consts.DEFAULT_DEPOT_ID,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {
        'success': 1,
        'data': {
            'createdObjects': [],
            'updatedObjects': [],
            'orderInfo': {
                'orderId': 'external_order_id',
                'customer': {'id': ''},
                'organization': consts.DEFAULT_DEPOT_ID,
                'sum': 0,
                'status': 'In progress',
                'items': [],
            },
        },
    }

    assert mock_wms.times_called == 1


async def test_info_wms_error(
        taxi_grocery_wms_gateway, mockserver, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=consts.DEFAULT_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/get_status')
    def mock_wms(request):
        raise mockserver.NetworkError()

    await taxi_grocery_wms_gateway.invalidate_caches()

    uri = '/v1/orders/info'
    response = await taxi_grocery_wms_gateway.post(
        uri
        + '?organization={}&order=external_order_id'.format(
            consts.DEFAULT_DEPOT_ID,
        ),
    )

    assert response.status_code == 500
    assert mock_wms.times_called >= 1


async def test_delete(taxi_grocery_wms_gateway, mockserver, grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=consts.DEFAULT_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/status')
    def mock_wms(request):
        return {
            'order': {
                'order_id': 'wms_order_id',
                'external_id': 'external_order_id',
                'status': 'cancelled',
                'store_id': 'wms_depot_id',
            },
        }

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.delete(
        '/v1/order/order_id?organization={}'.format(consts.DEFAULT_DEPOT_ID),
    )

    assert response.status_code == 200
    assert response.json() == {'success': 1, 'result': 'OK'}

    assert mock_wms.times_called == 1


@pytest.mark.parametrize('error_code', [400, 403, 404, 409])
async def test_delete_wms_error(
        taxi_grocery_wms_gateway, mockserver, error_code, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=consts.DEFAULT_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/status')
    def mock_wms(request):
        return mockserver.make_response(
            json.dumps({'code': 'ERROR_CODE', 'message': 'Error message'}),
            status=error_code,
        )

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.delete(
        '/v1/order/order_id?organization={}'.format(consts.DEFAULT_DEPOT_ID),
    )

    assert response.status_code == error_code
    assert mock_wms.times_called >= 1


async def test_reserve(taxi_grocery_wms_gateway, mockserver, grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/create')
    def mock_wms(request):
        assert request.json == {
            'store_id': consts.DEFAULT_WMS_DEPOT_ID,
            'required': [
                {
                    'product_id': 'item_id',
                    'count': 4,
                    'price': '137',
                    'price_unit': 1,
                    'price_type': 'store',
                },
            ],
            'total_price': '73591',
            'timeout_approving': 1800,
            'external_id': 'external_order_id',
            'client_id': 'customer_id',
            'approved': False,
            'editable': True,
        }

        return {
            'order': {
                'order_id': 'wms_order_id',
                'external_id': 'external_order_id',
                'status': 'reserving',
                'store_id': consts.DEFAULT_WMS_DEPOT_ID,
            },
        }

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/add',
        json={
            'organization': consts.DEFAULT_DEPOT_ID,
            'customer': {'id': 'customer_id'},
            'order': {
                'id': 'external_order_id',
                'date': 'date string',
                'fullSum': '73591.00',
                'items': [
                    {
                        'id': 'item_id',
                        'name': 'name',
                        'amount': '4',
                        'sum': '137.00',
                    },
                ],
                'type': 'reserve',
            },
        },
    )

    assert response.json() == {
        'success': 1,
        'data': {
            'createdObjects': [],
            'updatedObjects': [],
            'orderInfo': {
                'orderId': 'external_order_id',
                'customer': {'id': 'customer_id'},
                'organization': 'depot_id',
                'sum': 0,
                'status': 'New',
                'items': [
                    {
                        'id': 'item_id',
                        'name': 'name',
                        'amount': '4',
                        'sum': '137',
                    },
                ],
            },
        },
    }

    assert mock_wms.times_called == 1


async def test_reserve_with_discount_vat(
        taxi_grocery_wms_gateway, mockserver, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/create')
    def mock_wms(request):
        required = request.json['required']
        assert required[0]['discount'] == '13'
        assert required[0]['vat'] == '20'

        return {
            'order': {
                'order_id': 'wms_order_id',
                'external_id': 'external_order_id',
                'status': 'reserving',
                'store_id': consts.DEFAULT_WMS_DEPOT_ID,
            },
        }

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/add',
        json={
            'organization': consts.DEFAULT_DEPOT_ID,
            'customer': {'id': 'customer_id'},
            'order': {
                'id': 'external_order_id',
                'date': 'date string',
                'fullSum': '73591.00',
                'items': [
                    {
                        'id': 'item_id',
                        'name': 'name',
                        'amount': '4',
                        'sum': '137.00',
                        'full_price': '150.00',
                        'vat': '20',
                    },
                ],
                'type': 'reserve',
            },
        },
    )

    assert response.status_code == 200
    assert mock_wms.times_called == 1


async def test_set_courier(
        taxi_grocery_wms_gateway, mockserver, testpoint, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    original_depot_id = consts.DEFAULT_DEPOT_ID
    mapped_depot_id = consts.DEFAULT_WMS_DEPOT_ID

    api_request = {
        'external_id': 'order_id',
        'store_id': original_depot_id,
        'courier_name': 'Иван Васильевич',
        'courier_arrival_time': 5,
        'courier_delivery_promise': '2020-03-12T21:50:00+00:00',
        'courier_phone': '88005553535',
        'courier_type': 'rover',
        'related_orders': ['a', 'b', 'c'],
        'courier_vin': 'JH2PC35051M200020',
        'dispatch_delivery_type': 'yandex_taxi',
        'taxi_driver_uuid': 'some_very_log_uid',
    }

    wms_response = {
        'order': {
            'order_id': 'order_id',
            'external_id': 'external_id',
            'status': 'reserving',
            'store_id': mapped_depot_id,
        },
    }

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/set_courier')
    def mock_wms(request):
        wms_api_request = copy.deepcopy(api_request)
        wms_api_request['store_id'] = mapped_depot_id

        assert request.json == wms_api_request

        return wms_response

    @testpoint('fix-log-no-phone')
    def testpoint_logs(data):
        assert api_request['courier_name'] not in data['log']
        assert api_request['courier_phone'] not in data['log']

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/set_courier', api_request,
    )
    assert response.status_code == 200

    assert mock_wms.times_called == 1

    wms_response['order']['store_id'] = original_depot_id
    assert response.json() == wms_response

    assert testpoint_logs.times_called == 1


ARRIVAL_TIME = 15
COURIER_TYPE = 'human'


@pytest.mark.config(
    GROCERY_WMS_GATEWAY_DEFAULT_COURIER_ARRIVAL_TIME_MINUTES=ARRIVAL_TIME,
)
async def test_set_courier_missing_fields(
        taxi_grocery_wms_gateway, mockserver, testpoint, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    original_depot_id = consts.DEFAULT_DEPOT_ID
    mapped_depot_id = consts.DEFAULT_WMS_DEPOT_ID

    api_request = {
        'external_id': 'order_id',
        'store_id': original_depot_id,
        'courier_name': 'Иван Васильевич',
        'courier_phone': '88005553535',
        'related_orders': ['a', 'b', 'c'],
    }

    wms_response = {
        'order': {
            'order_id': 'order_id',
            'external_id': 'external_id',
            'status': 'reserving',
            'store_id': mapped_depot_id,
        },
    }

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/set_courier')
    def mock_wms(request):
        api_request['store_id'] = mapped_depot_id
        assert 'courier_external_id' not in request.json

        assert 'courier_arrival_time' in request.json
        assert request.json['courier_arrival_time'] == ARRIVAL_TIME
        request.json.pop('courier_arrival_time')

        assert 'courier_type' in request.json
        assert request.json['courier_type'] == COURIER_TYPE
        request.json.pop('courier_type')

        assert request.json == api_request

        return wms_response

    @testpoint('fix-log-no-phone')
    def testpoint_logs(data):
        assert api_request['courier_name'] not in data['log']
        assert api_request['courier_phone'] not in data['log']

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/set_courier', api_request,
    )
    assert response.status_code == 200

    assert mock_wms.times_called == 1

    wms_response['order']['store_id'] = original_depot_id
    assert response.json() == wms_response

    assert testpoint_logs.times_called == 1


async def test_set_eda_status(
        taxi_grocery_wms_gateway, mockserver, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    original_depot_id = consts.DEFAULT_DEPOT_ID
    mapped_depot_id = consts.DEFAULT_WMS_DEPOT_ID

    api_request = {
        'external_id': 'order_id',
        'store_id': original_depot_id,
        'eda_status': 'CALL_CENTER_CONFIRMED',
        'delivery_eta': '2020-03-12T21:50:00+00:00',
    }

    wms_response = {
        'code': 'OK',
        'order_id': 'wowSuchIdMuchWms0',
        'external_id': 'order_id',
        'store_id': original_depot_id,
        'eda_status': 'CALL_CENTER_CONFIRMED',
        'delivery_eta': '2020-03-12T21:50:00+00:00',
    }

    @mockserver.json_handler(
        '/grocery-wms/api/external/orders/v1/set_eda_status',
    )
    def mock_wms(request):
        api_request['store_id'] = mapped_depot_id
        assert request.json == api_request

        return wms_response

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/set_eda_status', api_request,
    )
    assert response.status_code == 200

    assert mock_wms.times_called == 1

    wms_response['store_id'] = original_depot_id
    assert response.json() == wms_response


@pytest.mark.parametrize('wms_error', [False, True])
async def test_assemble(
        taxi_grocery_wms_gateway, mockserver, wms_error, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/status')
    def mock_wms(request):
        assert request.json == {
            'store_id': consts.DEFAULT_WMS_DEPOT_ID,
            'external_id': 'external_order_id',
            'status': 'confirm',
        }

        if wms_error:
            return mockserver.make_response('{}', 409)

        return {
            'order': {
                'order_id': 'wms-order_id',
                'external_id': 'external_order_id',
                'status': 'processing',
                'store_id': consts.DEFAULT_WMS_DEPOT_ID,
            },
        }

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/assemble',
        json={
            'depot_id': consts.DEFAULT_DEPOT_ID,
            'order_id': 'external_order_id',
        },
    )

    assert response.status_code == 200
    if wms_error:
        assert response.json() == {'status': 'error'}
    else:
        assert response.json() == {'status': 'ok'}

    assert mock_wms.times_called == 1


async def test_set_pause(taxi_grocery_wms_gateway, mockserver, grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    original_depot_id = consts.DEFAULT_DEPOT_ID
    mapped_depot_id = consts.DEFAULT_WMS_DEPOT_ID

    api_request = {
        'external_id': 'order_id',
        'store_id': original_depot_id,
        'duration': 10,
    }

    wms_response = {
        'code': 'OK',
        'order_id': 'wowSuchIdMuchWms0',
        'external_id': 'order_id',
        'store_id': original_depot_id,
        'paused_until': '2020-03-12T21:50:00+00:00',
    }

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/set_pause')
    def mock_wms(request):
        api_request['store_id'] = mapped_depot_id
        assert request.json == api_request
        return wms_response

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/set_pause', api_request,
    )
    assert response.status_code == 200
    assert mock_wms.times_called == 1
    assert response.json() == {'paused_until': wms_response['paused_until']}
