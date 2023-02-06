import bson
import pytest


ORDER_CORE_FIELDS = [
    'order.pricing_data.published.fixed',
    'order.pricing_data.fixed_price',
    'order.pricing_data.published.taximeter',
    'order.cost',
    'order.performer.db_id',
    'order.driver_cost.cost',
    'order.current_prices.final_cost.driver.total',
    'order.toll_road.toll_road_price',
    'order.coupon.was_used',
    'order.status',
    'order_info.statistics.status_updates',
]


@pytest.fixture(name='mock_order_archive')
def _mock_order_archive(mockserver):
    class Context:
        def __init__(self):
            self.order_id = None
            self.park_id = None
            self.response = {}
            self.is_order_found = True

        def set_data(
                self,
                order_id=None,
                park_id=None,
                response=None,
                is_order_found=None,
        ):
            if order_id is not None:
                self.order_id = order_id
            if park_id is not None:
                self.park_id = park_id
            if response is not None:
                self.response = response
            if is_order_found is not None:
                self.is_order_found = is_order_found

        @property
        def has_mock_calls(self):
            return mock_get_fields.has_calls

        def make_request(self):
            return {
                'fields': ORDER_CORE_FIELDS,
                'filter': {'order.performer.db_id': self.park_id},
            }

        def make_response(self):
            response = self.response
            if self.park_id:
                response['order']['performer'] = {'db_id': self.park_id}
            return {
                'doc': {
                    'processing': {'version': 20},
                    '_id': self.order_id,
                    **response,
                },
            }

    context = Context()

    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def mock_get_fields(request):
        assert request.json == {
            'id': context.order_id,
            'lookup_yt': True,
            'indexes': ['alias'],
        }

        if not context.is_order_found:
            return mockserver.make_response(
                json={'code': 'no_such_order', 'message': 'no_such_order'},
                status=404,
            )
        return mockserver.make_response(
            bson.BSON.encode(context.make_response()), status=200,
        )

    return context
