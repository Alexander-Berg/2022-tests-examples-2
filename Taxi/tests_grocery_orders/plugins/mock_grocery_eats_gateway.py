import copy
import json

import pytest

DEFAULT_ORDER_REQUEST = {
    'eats_user_id': 'eats_user_id_0',
    'status_updated': '2020-05-25T17:43:00+00:00',
    'delivered_eta_ts': '2020-05-25T17:43:00+00:00',
    'location': {'latitude': 20.0, 'longitude': 10.0},
    'delivery_type': 'courier',
    'created': '2020-05-25T17:40:45+00:00',
    'updated': '2020-05-25T17:43:00+00:00',
    'app_name': 'eda_webview_iphone',
    'order_history': [],
    'payment_method': 'grocery',
    'region_id': 213,
    'depot_id': '12345',
    'short_order_id': '000000-111-2222',
    'is_hold_money_finished': False,
}

DEFAULT_COURIER_REQUEST = {
    'courier_name': 'Ivan',
    'transport_type': 'bicycle',
    'eats_courier_id': 'eats_courier_id_123',
    'claim_id': 'dispatch_id_123',
}


@pytest.fixture(name='grocery_eats_gateway')
def mock_grocery_eats_gateway(mockserver):
    class Context:
        def __init__(self):
            self.order_info = copy.deepcopy(DEFAULT_ORDER_REQUEST)
            self.courier_info = copy.deepcopy(DEFAULT_COURIER_REQUEST)

        def times_stq_orders(self):
            return mock_stq_orders.times_called

        def times_stq_couriers(self):
            return mock_stq_couriers.times_called

        def __set_data(self, info, key, value):
            if value is None and key in info:
                del info[key]
            elif value is not None:
                info[key] = value

        def set_order_data(self, **kwargs):
            for key, value in kwargs.items():
                self.__set_data(self.order_info, key, value)

        def set_courier_data(self, **kwargs):
            for key, value in kwargs.items():
                self.__set_data(self.courier_info, key, value)

        def __add_history_item(
                self, order_id, time, event_type, event_data, cursor,
        ):
            cursor.execute(
                'Insert into orders.orders_history Values(%s, %s, %s, %s);',
                [order_id, time, event_type, json.dumps(event_data)],
            )
            if event_type == 'status_change':
                self.order_info['order_history'].append(
                    {
                        'ts': time,
                        'event_type': event_type,
                        'event_data': {'status': event_data['to']},
                    },
                )
            elif event_type == 'dispatch_status_change':
                new_item = {
                    'ts': time,
                    'event_type': event_type,
                    'event_data': {
                        'dispatch_status': event_data['to_dispatch_status'],
                    },
                }
                if 'to_dispatch_cargo_status' in event_data:
                    new_item['event_data'][
                        'dispatch_cargo_status'
                    ] = event_data['to_dispatch_cargo_status']
                self.order_info['order_history'].append(new_item)

        def add_history(self, order_id, time, pgsql):
            cursor = pgsql['grocery_orders'].cursor()
            self.__add_history_item(
                order_id, time, 'status_change', {'to': 'draft'}, cursor,
            )
            self.__add_history_item(
                order_id, time, 'status_change', {'to': 'delivering'}, cursor,
            )
            self.__add_history_item(
                order_id, time, 'state_change', {'to': 'canceled'}, cursor,
            )
            self.__add_history_item(
                order_id,
                time,
                'dispatch_status_change',
                {
                    'to_dispatch_status': 'delivering',
                    'to_dispatch_cargo_status': 'pickuped',
                },
                cursor,
            )

    context = Context()

    @mockserver.json_handler(
        '/grocery-eats-gateway/orders/v1/tracking/stq/order',
    )
    def mock_stq_orders(request):
        if 'finished_at' in request.json:
            assert request.json['finished_at'] == '2020-03-13T07:19:00+00:00'
            del request.json['finished_at']
        if 'suffix_stq_task_id' not in context.order_info:
            assert 'suffix_stq_task_id' in request.json
            del request.json['suffix_stq_task_id']
        for idx, _ in enumerate(request.json['order_history']):
            if 'ts' in request.json['order_history'][idx]:
                del request.json['order_history'][idx]['ts']
        for idx, _ in enumerate(context.order_info['order_history']):
            if 'ts' in context.order_info['order_history'][idx]:
                del context.order_info['order_history'][idx]['ts']

        assert context.order_info == request.json
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/grocery-eats-gateway/orders/v1/tracking/stq/courier',
    )
    def mock_stq_couriers(request):
        if 'suffix_stq_task_id' not in context.courier_info:
            assert 'suffix_stq_task_id' in request.json
            del request.json['suffix_stq_task_id']
        assert context.courier_info == request.json
        return mockserver.make_response(status=200)

    return context
