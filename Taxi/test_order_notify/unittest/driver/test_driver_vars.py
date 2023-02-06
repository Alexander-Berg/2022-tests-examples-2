import typing

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.driver import driver_vars as dr_vars
from order_notify.repositories.order_info import OrderData


DEFAULT_ORDER_DATA = OrderData(
    brand='',
    country='',
    order={},
    order_proc={
        'candidates': [{'name': 'L', 'first_name': 'K'}],
        'performer': {'candidate_index': 0, 'driver_id': '345112_1'},
    },
)


@pytest.fixture(name='mock_functions')
def mock_driver_vars_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_car_vars = Counter()
            self.get_park_vars = Counter()
            self.hide_driver_vars = Counter()

    counters = Counters()

    @patch('order_notify.repositories.driver.car_vars.get_car_vars')
    def _get_car_vars(
            context: stq_context.Context, order_data: OrderData, locale: str,
    ) -> dict:
        counters.get_car_vars.call()
        assert order_data == DEFAULT_ORDER_DATA
        assert locale == 'ru'
        return {'car': 'car'}

    @patch('order_notify.repositories.driver.park_vars.get_park_vars')
    async def _get_park_vars(
            context: stq_context.Context, park_id: str, locale: str,
    ) -> dict:
        counters.get_park_vars.call()
        assert park_id == '345112'
        assert locale == 'ru'
        return {'park': 'park'}

    @patch('order_notify.repositories.driver.driver_vars.hide_driver_vars')
    def _hide_driver_vars(
            context: stq_context.Context,
            zone: typing.Optional[str],
            driver_vars: dict,
            driver_first_name: str,
    ) -> dict:
        counters.hide_driver_vars.call()
        return driver_vars

    return counters


async def test_get_driver_vars(
        stq3_context: stq_context.Context, mock_functions,
):
    expected_vars = {
        'car': 'car',
        'park': 'park',
        'driver_name': 'L',
        'show_ogrn_and_unp': False,
    }
    d_vars = await dr_vars.get_driver_vars(
        context=stq3_context,
        order_data=DEFAULT_ORDER_DATA,
        show_ogrn_and_unp=False,
        locale='ru',
    )
    assert d_vars == expected_vars
    assert mock_functions.get_car_vars.times_called == 1
    assert mock_functions.get_park_vars.times_called == 1
    assert mock_functions.hide_driver_vars.times_called == 1
