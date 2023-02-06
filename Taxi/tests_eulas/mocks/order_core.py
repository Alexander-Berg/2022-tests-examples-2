import bson
import pytest


class OrderProcGetFieldsContext:
    class Response:
        def __init__(self):
            self.order = {}
            self.error_code = None

        def set_zone(self, zone):
            self.order['order']['nz'] = zone

        def set_candidate_tags(self, tags, candidate_idx=0):
            self.order['candidates'][candidate_idx]['tags'] = tags

        def delete_order_field(self, order_field: str):
            keys = order_field.split('.')
            subdict = self.order

            for key in keys[:-1]:
                if isinstance(subdict, list):
                    subdict = subdict[0]
                else:
                    subdict = subdict[key]

            if isinstance(subdict, list):
                subdict = subdict[0]

            del subdict[keys[-1]]

    class Expectations:
        def __init__(self):
            self.order_id = None
            self.fields = None
            self.search_archive = False

    class Call:
        def __init__(self):
            self.response = OrderProcGetFieldsContext.Response()
            self.expected = OrderProcGetFieldsContext.Expectations()

    def __init__(self):
        self.call = OrderProcGetFieldsContext.Call()
        self.handler = None

    @property
    def times_called(self):
        return self.handler.times_called


@pytest.fixture(name='mock_order_core_get_fields')
def mock_get_fields(mockserver):
    context = OrderProcGetFieldsContext()

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def handler(request):
        assert request.content_type == 'application/bson'

        expected = context.call.expected
        response = context.call.response

        if expected.order_id is not None:
            assert request.query['order_id'] == expected.order_id
        assert request.query['require_latest'] == 'false'
        if expected.fields is not None:
            assert bson.BSON.decode(request.get_data()) == {
                'fields': expected.fields,
            }
        if expected.search_archive is not None:
            assert (
                request.query['autorestore']
                == str(expected.search_archive).lower()
            )

        if response.error_code is not None:
            return mockserver.make_response(
                status=response.error_code,
                json={'code': str(response.error_code), 'message': 'error'},
            )

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({'document': response.order}),
        )

    context.handler = handler
    return context
