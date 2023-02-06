# encoding=utf-8
import pytest


@pytest.fixture(name='billing_orders', autouse=True)
def _mock_billing_orders(mockserver, load_json):
    class BillingOrdersContext:
        def __init__(self):
            self.request_path = 'billing_orders_request.json'

        def set_request_path(self, request_path):
            self.request_path = request_path

    context = BillingOrdersContext()

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _mock_v2_process_async(request):
        def get_park_id_from_dict(arg):
            return arg['data']['template_entries'][0]['context']['park_id']

        expected_request = load_json(context.request_path)
        request_json = request.json

        # Check that there is only one field in root path
        assert len(expected_request) == len(request_json)
        assert sorted(
            request_json['orders'], key=get_park_id_from_dict,
        ) == sorted(expected_request['orders'], key=get_park_id_from_dict)
        return {
            'orders': [
                {'topic': 'shi', 'external_ref': 'hit', 'doc_id': 6112},
            ],
        }

    return context
