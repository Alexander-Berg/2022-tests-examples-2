# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import bson
import pytest

from cashback_levels_plugins import *  # noqa: F403 F401


PROTO_JSON_FORMAT_KWARGS = {
    'including_default_value_fields': True,
    'preserving_proto_field_name': True,
    'float_precision': 4,
}
ORDER_CORE_ENDPOINT_PATH = (
    '/order-core/internal/processing/v1/order-proc/get-fields'
)
INVOICE_RETRIEVE_ENDPOINT = '/transactions/v2/invoice/retrieve'


@pytest.fixture
def mock_order_core(mockserver):
    def _mock(order_proc_fields):
        @mockserver.handler(ORDER_CORE_ENDPOINT_PATH)
        def _mock_order_core_response(request):
            order = {
                'document': order_proc_fields,
                'revision': {'order.version': 8, 'processing.version': 16},
            }
            return mockserver.make_response(
                response=bson.BSON.encode(order),
                status=200,
                content_type='application/bson',
            )

        return _mock_order_core_response

    return _mock


@pytest.fixture
def mock_invoice_retrieve(mockserver):
    def _mock(invoice):
        @mockserver.handler(INVOICE_RETRIEVE_ENDPOINT)
        def _mock_invoice_retrieve_response(request):
            return mockserver.make_response(json=invoice, status=200)

        return _mock_invoice_retrieve_response

    return _mock


@pytest.fixture
def mock_logbrocker_publish(testpoint):
    def _mock():
        @testpoint('logbroker_publish_b64')
        def mock_lb_publish(data):
            pass

        return mock_lb_publish

    return _mock
