import json

import pytest

from tests_grocery_uber_gw import consts

HEX_DIGIT_REGEX = '[0-9a-f]'
UUID_REGEX = '{0}{{8}}-{0}{{4}}-{0}{{4}}-{0}{{4}}-{0}{{12}}'.format(
    HEX_DIGIT_REGEX,
)

STORE_ID_REGEX = r'(?P<store_id>{})'.format(UUID_REGEX)
ORDER_ID_REGEX = r'(?P<order_id>{})'.format(UUID_REGEX)


@pytest.fixture(name='mock_uber_api', autouse=True)
def mock_uber_api(mockserver):
    class Context:
        def __init__(self):
            self._payload = {}
            self._deny_reason = None

        def set_payload(self, payload):
            self._payload = payload

        def set_deny_reason(self, reason):
            self._deny_reason = reason

        @property
        def stores(self):
            return self._payload.get('stores', consts.DEFAULT_STORES)

        @property
        def orders(self):
            return self._payload.get('orders', consts.DEFAULT_ORDERS)

        @property
        def menus(self):
            return self._payload.get('menus', consts.DEFAULT_MENUS)

        @property
        def deny_reason(self):
            return self._deny_reason

        @property
        def order_accept_times_called(self):
            return _mock_accept_order.times_called

        @property
        def restaurant_status_times_called(self):
            return _mock_restaurant_status.times_called

        @property
        def get_order_details_times_called(self):
            return _mock_get_order_details.times_called

        @property
        def upd_delivery_stat_times_called(self):
            return _mock_update_delivery_status.times_called

        @property
        def cancel_order_times_called(self):
            return _mock_cancel_order.times_called

        @property
        def deny_order_times_called(self):
            return _mock_deny_order.times_called

    context = Context()

    @mockserver.json_handler('/uber-api/v1/eats/stores')
    def _mock_list_all_stores(request):
        assert 'Authorization' in request.headers

        stores = list(context.stores.values())

        limit = (
            int(request.query['limit']) if ('limit' in request.query) else 50
        )
        start_key = (
            request.query['start_key']
            if ('start_key' in request.query)
            else None
        )

        if start_key is None:
            start_key = stores[0].cursor

        start_index = next(
            i for i, store in enumerate(stores) if store.cursor == start_key
        )

        response_stores = []
        for i in range(start_index, min(start_index + limit, len(stores))):
            response_stores.append(stores[i].get_data())

        response = {'stores': response_stores}
        if start_index + limit < len(stores):
            response['next_key'] = stores[start_index + limit].cursor
        return response

    @mockserver.json_handler(
        r'/uber-api/v1/eats/store/{}/status'.format(STORE_ID_REGEX),
        regex=True,
    )
    def _mock_restaurant_status(request, store_id):
        assert 'Authorization' in request.headers
        assert request.method in {'GET', 'POST'}
        if store_id not in context.stores:
            return mockserver.make_response(status=404)
        if request.method == 'GET':
            assert context.stores[store_id].status in {'ONLINE', 'OFFLINE'}
            if context.stores[store_id].status == 'ONLINE':
                response = {'status': 'ONLINE'}
                return response
            if context.stores[store_id].status == 'OFFLINE':
                response = {
                    'status': 'OFFLINE',
                    'offlineReason': 'PAUSED_BY_RESTAURANT',
                }
                return response
        if request.method == 'POST':
            request_body = json.loads(request.get_data())
            assert request_body['status'] in {'ONLINE', 'PAUSED'}
            if request_body['status'] == 'ONLINE':
                context.stores[store_id].status = 'ONLINE'
            if request_body['status'] == 'PAUSED':
                context.stores[store_id].status = 'OFFLINE'
            return mockserver.make_response(status=204)
        return mockserver.make_response(status=400)

    @mockserver.json_handler(
        r'/uber-api/v2/eats/order/{}'.format(ORDER_ID_REGEX), regex=True,
    )
    def _mock_get_order_details(request, order_id):
        assert 'Authorization' in request.headers
        if order_id in context.orders:
            return context.orders[order_id].get_data()
        return mockserver.make_response(status=404)

    @mockserver.json_handler(
        r'/uber-api/v1/eats/orders/{}/accept_pos_order'.format(UUID_REGEX),
        regex=True,
    )
    def _mock_accept_order(request):
        assert 'Authorization' in request.headers
        assert 'reason' in request.json
        assert 'external_reference_id' in request.json
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        r'/uber-api/v1/eats/orders/{}/deny_pos_order'.format(UUID_REGEX),
        regex=True,
    )
    def _mock_deny_order(request):
        assert 'Authorization' in request.headers
        assert 'reason' in request.json
        reason = request.json['reason']
        assert 'explanation' in reason
        assert reason['code'] in [
            'STORE_CLOSED',
            'POS_NOT_READY',
            'POS_OFFLINE',
            'ITEM_AVAILABILITY',
            'MISSING_ITEM',
            'MISSING_INFO',
            'PRICING',
            'CAPACITY',
            'ADDRESS',
            'SPECIAL_INSTRUCTIONS',
            'OTHER',
        ]
        if context.deny_reason:
            ctx_reason = context.deny_reason
            assert ctx_reason['code'] == reason['code']
            if 'invalid_items' in ctx_reason:
                assert ctx_reason['invalid_items'] == reason['invalid_items']
            else:
                assert 'invalid_items' not in reason
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        r'/uber-api/v1/eats/orders/{}/restaurantdelivery/status'.format(
            UUID_REGEX,
        ),
        regex=True,
    )
    def _mock_update_delivery_status(request):
        assert 'Authorization' in request.headers
        assert request.json['status'] in ['started', 'arriving', 'delivered']
        # update order delivery status
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        r'/uber-api/v1/eats/orders/{}/cancel'.format(UUID_REGEX), regex=True,
    )
    def _mock_cancel_order(request):
        assert 'Authorization' in request.headers
        assert request.json['reason'] in [
            'OUT_OF_ITEMS',
            'KITCHEN_CLOSED',
            'CUSTOMER_CALLED_TO_CANCEL',
            'RESTAURANT_TOO_BUSY',
            'CANNOT_COMPLETE_CUSTOMER_NOTE',
            'OTHER',
        ]
        if request.json['reason'] == 'OTHER':
            assert 'details' in request.json
        # cancel order
        # if no order return 404
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        r'/uber-api/v2/eats/stores/{}/menus'.format(STORE_ID_REGEX),
        regex=True,
    )
    def _mock_get_store_menu(request, store_id):
        assert 'Authorization' in request.headers
        if store_id in context.menus:
            return context.menus[store_id].get_data()
        return mockserver.make_response(status=404)

    return context
