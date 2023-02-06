import pytest

from order_notify.repositories.order_info import OrderData
from order_notify.repositories.payment import basic_cost as basic_cost_info


@pytest.fixture(name='mock_functions')
def mock_basic_cost_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.does_order_cost_consider_coupon = Counter()
            self.get_coupon_value = Counter()

    counters = Counters()

    @patch(
        'order_notify.repositories.payment.basic_cost.'
        'does_order_cost_consider_coupon',
    )
    def _does_order_cost_consider_coupon(order_data: OrderData) -> bool:
        counters.does_order_cost_consider_coupon.call()
        order_id = order_data.order_proc['_id']
        assert order_id in ('1', '2', '3', '4')
        return order_id in ('1', '2')

    @patch('order_notify.repositories.payment.basic_cost.get_coupon_value')
    def _get_coupon_value(order_data: OrderData) -> float:
        counters.get_coupon_value.call()
        order_id = order_data.order_proc['_id']
        assert order_id in ('3', '4')
        if order_id == '3':
            return 200
        return 1000

    return counters


@pytest.mark.parametrize(
    'order_data, expected_basic_cost, expected_times_called',
    [
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={'_id': '1', 'order': {}},
            ),
            0,
            [1, 0],
            id='no_ride_cost_include_coupon',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={'_id': '2', 'order': {'cost': 103}},
            ),
            103,
            [1, 0],
            id='include_coupon',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={'_id': '3', 'order': {'cost': 500}},
            ),
            300,
            [1, 1],
            id='not_include_coupon_ride_cost_bigger',
        ),
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={'_id': '4', 'order': {'cost': 432}},
            ),
            0,
            [1, 1],
            id='not_include_coupon_ride_cost_less',
        ),
    ],
)
def test_get_basic_cost(
        mock_functions, order_data, expected_basic_cost, expected_times_called,
):
    basic_cost = basic_cost_info.get_basic_cost(order_data)

    assert basic_cost == expected_basic_cost
    assert [
        mock_functions.does_order_cost_consider_coupon.times_called,
        mock_functions.get_coupon_value.times_called,
    ] == expected_times_called
