import pytest


DEFAULT_RESPONSE = {
    'orders': [
        {'topic': 'topic', 'external_ref': 'external_ref', 'doc_id': 1},
    ],
}


@pytest.fixture(name='billing_orders')
def mock_billing_orders(mockserver):
    data = {}

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _mock_process_async(request):
        if 'http_error_code' in data and data['http_error_code'] is not None:
            return mockserver.make_response('{}', data['http_error_code'])

        if 'finished' not in data:
            return DEFAULT_RESPONSE

        order_id = data['order_id']
        item_id = data['item_id']
        operation_id = data['operation_id']
        assert request.json == {
            'orders': [
                {
                    'data': {
                        'context': {},
                        'entries': [],
                        'event_version': 1,
                        'payments': data['payments'],
                        'schema_version': 'v1',
                        'topic_begin_at': data['finished'],
                    },
                    'event_at': data['finished'],
                    'external_ref': '1',
                    'kind': 'arbitrary_payout',
                    'topic': (
                        f'taxi/lavka_grocery_sale/{order_id}/{item_id}/'
                        f'{operation_id}'
                    ),
                },
            ],
        }
        return DEFAULT_RESPONSE

    class Context:
        def check_request(
                self, finished, order_id, item_id, operation_id, payments,
        ):
            data['finished'] = finished
            data['order_id'] = order_id
            data['item_id'] = item_id
            data['operation_id'] = operation_id
            data['payments'] = payments

        def set_http_error_code(self, code):
            data['http_error_code'] = code

        def process_async_times_called(self):
            return _mock_process_async.times_called

        def flush(self):
            _mock_process_async.flush()

    context = Context()
    return context
