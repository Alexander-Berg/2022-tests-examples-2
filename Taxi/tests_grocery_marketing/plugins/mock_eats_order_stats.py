import pytest


@pytest.fixture(name='eats_order_stats')
def eats_order_stats(mockserver):
    class Context:
        def __init__(self):
            self.eats_user_id = None
            self.eats_id_tag_count = None
            self.counters = None

        def set_orders_data(
                self, eats_user_id, eats_id_tag_count, counters=None,
        ):
            self.eats_user_id = eats_user_id
            self.eats_id_tag_count = eats_id_tag_count
            self.counters = counters

        @property
        def times_orders_called(self):
            return mock_order_stats.times_called

    context = Context()

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def mock_order_stats(request):
        assert request.json['identities'] == [
            {'type': 'eater_id', 'value': context.eats_user_id},
        ]
        return {
            'data': [
                {
                    'counters': context.counters if context.counters else [],
                    'identity': {'type': 'eater_id', 'value': '111'},
                },
            ],
        }

    return context
