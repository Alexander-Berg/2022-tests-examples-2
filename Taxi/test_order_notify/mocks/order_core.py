from typing import Dict

from bson import BSON
import pytest


class OrderProcGetFieldsContext:
    class Response:
        def __init__(self):
            self.order = {}
            self.error_code = None

        def set_alternative_type(self, alternative_type: str):
            self.order['order']['calc']['alternative_type'] = alternative_type

    class Expectations:
        def __init__(self):
            self.order_id = None
            self.fields = None
            self.require_latest = False
            self.order_id_type = 'alias_id'

    class Call:
        def __init__(self):
            self.response = OrderProcGetFieldsContext.Response()
            self.expected = OrderProcGetFieldsContext.Expectations()

    def __init__(self):
        self.calls: Dict(str, OrderProcGetFieldsContext.Call) = {}
        self.handler = None

    @property
    def times_called(self):
        return self.handler.times_called


@pytest.fixture(name='mock_order_core_get_fields')
def mock_get_fields(mockserver):
    def mock():
        context = OrderProcGetFieldsContext()

        @mockserver.handler(
            '/order-core/internal/processing/v1/order-proc/get-fields',
        )
        def handler(request):
            assert request.content_type == 'application/bson'

            order_id = request.query['order_id']
            if order_id not in context.calls:
                return mockserver.make_response(
                    status=404,
                    json={
                        'code': 'no_such_order',
                        'message': f'{order_id} was not found',
                    },
                )

            expected = context.calls[order_id].expected
            response = context.calls[order_id].response

            if expected.order_id is not None:
                assert request.query['order_id'] == expected.order_id
            if expected.fields is not None:
                assert BSON.decode(request.get_data()) == {
                    'fields': expected.fields,
                }
            if expected.require_latest is not None:
                assert (
                    request.query['require_latest']
                    == str(expected.require_latest).lower()
                )
            if expected.order_id_type is not None:
                assert request.query['order_id_type'] == expected.order_id_type

            if response.error_code is not None:
                return mockserver.make_response(
                    status=response.error_code,
                    json={
                        'code': str(response.error_code),
                        'message': 'error',
                    },
                )

            return mockserver.make_response(
                status=200,
                content_type='application/bson',
                response=BSON.encode({'document': response.order}),
            )

        context.handler = handler
        return context

    return mock
