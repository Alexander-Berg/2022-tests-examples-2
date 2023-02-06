import bson
import pytest


@pytest.fixture(name='mock_order_core')
def _mock_order_core(mockserver, load_json):
    class Context:
        def __init__(self):
            self.response = None
            self.handler_get_fields = None

        def set_response(self, response):
            self.response = response

    ctx = Context()

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_get_fields(request):
        body = bson.BSON.decode(request.get_data())
        assert body == {
            'filters': [],
            'fields': [
                'candidates.driver_id',
                'candidates.db_id',
                'candidates.point',
                'candidates.tags',
                'candidates.tariff_class',
                'candidates.driver_metrics.activity',
                'order.nz',
                'order.request',
                'order_info.statistics.status_updates',
                'performer.candidate_index',
                'order.performer.has_sticker',
                'order.performer.has_lightbox',
            ],
        }
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(ctx.response),
        )

    ctx.handler_get_fields = _mock_get_fields
    return ctx
