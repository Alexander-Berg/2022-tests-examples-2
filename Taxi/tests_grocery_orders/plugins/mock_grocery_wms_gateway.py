import typing

import pytest

from tests_grocery_orders import headers
from tests_grocery_orders import models

NOW = '2020-03-13T07:19:00+00:00'


@pytest.fixture(name='grocery_wms_gateway', autouse=True)
def mock_grocery_wms_gateway(mockserver):
    payload = {}

    @mockserver.json_handler('/grocery-wms-gateway/v1/order/', prefix=True)
    def mock_close_order(request):
        if payload.get('http_code', None):
            return mockserver.make_response(
                payload.get('http_resp', {}), payload.get('http_code'),
            )
        if payload.get('fail', False):
            return {'success': 0}
        return {'success': 1}

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/assemble')
    def mock_assemble_order(request):
        if payload.get('http_code', None):
            return mockserver.make_response(
                payload.get('http_resp', {}), payload.get('http_code'),
            )
        if payload.get('fail', False):
            return {'status': 'error'}
        return {'status': 'ok'}

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/invoice')
    def mock_update_invoice(request):
        if payload.get('http_code', None):
            return mockserver.make_response(
                payload.get('http_resp', {}), payload.get('http_code'),
            )
        if 'invoices' in payload:
            assert request.json == payload['invoices']
        return {}

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/set_courier')
    def mock_set_courier(request):
        assert 'store_id' in request.json
        assert 'external_id' in request.json
        assert 'related_orders' in request.json
        assert 'courier_type' in request.json

        if 'taxi_driver_uuid' in payload:
            assert 'taxi_driver_uuid' in request.json
            assert (
                payload['taxi_driver_uuid'] == request.json['taxi_driver_uuid']
            )

        if 'courier_vin' in payload:
            assert 'courier_name' in request.json
            assert request.json['courier_vin'] == payload['courier_vin']

        if 'dispatch_delivery_type' in payload:
            assert (
                request.json['dispatch_delivery_type']
                == payload['dispatch_delivery_type']
            )

        return {
            'order': {
                'external_id': request.json['external_id'],
                'order_id': request.json['external_id'],
                'status': 'reserving',
                'store_id': request.json['store_id'],
                'courier_type': request.json['courier_type'],
            },
        }

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/set_eda_status')
    def mock_set_eda_status(request):
        if payload.get('http_code', None):
            return mockserver.make_response(
                payload.get('http_resp', {}), payload.get('http_code'),
            )

        assert 'store_id' in request.json
        assert 'external_id' in request.json
        if 'eda_status' in payload:
            assert request.json['eda_status'] == payload['eda_status']
        else:
            assert 'eda_status' in request.json

        return {
            'code': 'OK',
            'store_id': request.json['store_id'],
            'external_id': request.json['external_id'],
            'eda_status': request.json['eda_status'],
            'order_id': request.json['external_id'],
        }

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/set_pause')
    def mock_set_pause(request):
        if payload.get('http_code', None):
            return mockserver.make_response(
                payload.get('http_resp', {}), payload.get('http_code'),
            )

        assert 'store_id' in request.json
        assert 'external_id' in request.json
        assert 'duration' in request.json

        return {'paused_until': NOW}

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/add')
    def mock_order_add(request):
        if payload.get('http_code', None):
            return mockserver.make_response(
                payload.get('http_resp', {}), payload.get('http_code'),
            )
        if 'reserve_request' in payload:
            assert request.json == payload['reserve_request']

        if context.logistic_tags is not None:
            assert (
                context.logistic_tags == request.json['order']['logistic_tags']
            )

        if context.reserve_timeout is not None:
            assert (
                context.reserve_timeout
                == request.json['order']['reserve_timeout']
            )

        ret = {
            'success': 1,
            'data': {
                'createdObjects': [],
                'updatedObjects': [],
                'orderInfo': {
                    'orderId': 'abcdef',
                    'customer': {'id': '123123abc'},
                    'organization': '',
                    'sum': 123,
                    'status': 'ok',
                    'items': [],
                },
            },
        }
        if payload.get('fail', False):
            ret['success'] = 0
        return ret

    class Context:
        logistic_tags = None
        reserve_timeout = None

        def check_reserve(
                self,
                items: typing.List[models.GroceryCartItem],
                full_sum: str,
                order: models.Order,
                order_revision,
                max_eta: int = 55,
                maybe_rover: bool = False,
                client_tags: typing.List[str] = None,
                reserve_timeout: int = None,
        ):
            request_items = []
            for item in items:
                request_item = {
                    'amount': item.quantity,
                    'id': item.item_id,
                    'name': item.title,
                    'sum': item.price,
                    'vat': item.vat,
                }
                if item.full_price:
                    request_item['full_price'] = item.full_price
                request_items.append(request_item)

            payload['reserve_request'] = {
                'customer': {
                    'id': 'taxi_user_id:' + headers.USER_ID,
                    'personal_phone_id': headers.PERSONAL_PHONE_ID,
                },
                'order': {
                    'date': order.created.isoformat().replace(
                        '+00:00', '+0000',
                    ),
                    'fullSum': full_sum,
                    'id': order.order_id,
                    'items': request_items,
                    'short_id': order.short_order_id,
                    'type': 'reserve',
                    'delivery_eta': max_eta,
                    'delivery_address': {
                        'full_address': (
                            'order_country, order_city,'
                            ' order_street, order_building'
                        ),
                        'lat': 20.0,
                        'lon': 10.0,
                    },
                    'maybe_rover': maybe_rover,
                },
                'organization': order.depot_id,
            }
            if order_revision is not None:
                payload['reserve_request']['order_revision'] = order_revision
            if client_tags is not None:
                payload['reserve_request']['order'][
                    'client_tags'
                ] = client_tags
            if reserve_timeout is not None:
                payload['reserve_request']['order'][
                    'reserve_timeout'
                ] = reserve_timeout

        def check_update_invoices(self, invoices):
            payload['invoices'] = invoices

        def check_set_eda_status(self, status):
            payload['eda_status'] = status

        def check_set_courier(self, courier_vin):
            payload['courier_vin'] = courier_vin

        def set_fail_flag(self, flag):
            payload['fail'] = flag

        def set_http_resp(self, resp='{}', code=200):
            payload['http_code'] = code
            payload['http_resp'] = resp

        def set_driver_uuid(self, driver_uuid='driver_uuid'):
            if driver_uuid is not None:
                payload['taxi_driver_uuid'] = driver_uuid
            elif 'taxi_driver_uuid' in payload:
                del payload['taxi_driver_uuid']

        def set_wms_logistic_tag(self, tags):
            self.logistic_tags = tags

        def set_reserve_timeout(self, reserve_timeout):
            self.reserve_timeout = reserve_timeout

        def set_dispatch_delivery_type(self, dispatch_delivery_type):
            payload['dispatch_delivery_type'] = dispatch_delivery_type

        def times_mock_order_add(self):
            return mock_order_add.times_called

        def times_reserve_called(self):
            return mock_order_add.times_called

        def times_assemble_called(self):
            return mock_assemble_order.times_called

        def times_close_called(self):
            return mock_close_order.times_called

        def times_update_invoices_called(self):
            return mock_update_invoice.times_called

        def times_set_courier_called(self):
            return mock_set_courier.times_called

        def times_set_eda_status_called(self):
            return mock_set_eda_status.times_called

        def times_set_pause_called(self):
            return mock_set_pause.times_called

        def flush_all(self):
            mock_order_add.flush()
            mock_assemble_order.flush()
            mock_close_order.flush()
            mock_update_invoice.flush()

    context = Context()
    return context
