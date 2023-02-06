import decimal

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData
from order_notify.repositories.payment.payment_info import get_payment_data
from order_notify.repositories.payment.payment_info import PaymentData


PAYMENT_TECH = {
    'user_to_pay': {'ride': 3130000, 'tips': 50000, 'cashback': 270000},
    'without_vat_to_pay': {'ride': 2430000, 'tips': 240000},
}


@pytest.fixture(name='mock_functions')
def mock_payment_data_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_basic_cost = Counter()
            self.get_tips_percent = Counter()
            self.get_vat_perc = Counter()
            self.round_by_currency = Counter()

    counters = Counters()

    @patch('order_notify.repositories.payment.basic_cost.get_basic_cost')
    def _get_basic_cost(order_data: OrderData) -> float:
        counters.get_basic_cost.call()
        return 1000.0

    @patch('order_notify.repositories.payment.payment_info.get_tips_percent')
    def _get_tips_percent(order_data: OrderData) -> float:
        counters.get_tips_percent.call()
        return 20.0

    @patch('order_notify.repositories.payment.vat_perc.get_vat_coeff')
    async def _get_vat_coeff(
            context: stq_context.Context, order_data: OrderData,
    ) -> float:
        counters.get_vat_perc.call()
        return 12000.0

    @patch('order_notify.repositories.payment.currency.round_by_currency')
    def _round_by_currency(
            context: stq_context.Context, cost: float, currency: str,
    ) -> float:
        assert cost == decimal.Decimal(1200)
        assert currency == 'RUB'
        counters.round_by_currency.call()
        return 1200.0

    return counters


@pytest.mark.parametrize(
    'payment_type, need_accept, times_called, expected_payment_data',
    [
        pytest.param(
            'cash',
            True,
            [1, 0, 0, 0],
            PaymentData(total_cost=decimal.Decimal(1000)),
            id='cash',
        ),
        pytest.param(
            'card',
            False,
            [1, 1, 0, 0],
            PaymentData(
                total_cost=decimal.Decimal(345),
                cost_without_vat=decimal.Decimal(270),
                tips=decimal.Decimal(5),
                tips_percent=20,
            ),
            id='not_need_accept_not_corp',
        ),
        pytest.param(
            'corp',
            False,
            [1, 1, 1, 0],
            PaymentData(
                total_cost=decimal.Decimal(345),
                cost_without_vat=decimal.Decimal(270),
                tips=decimal.Decimal(5),
                tips_percent=20,
                vat_value=decimal.Decimal(78),
                vat_perc=20,
            ),
            id='not_need_accept_corp',
        ),
        pytest.param(
            'corp',
            True,
            [1, 0, 1, 1],
            PaymentData(
                total_cost=decimal.Decimal(1200),
                cost_without_vat=decimal.Decimal(1000),
                vat_value=decimal.Decimal(200),
                vat_perc=20,
            ),
            id='need_accept_corp',
        ),
        pytest.param(
            'card',
            True,
            [1, 0, 0, 0],
            PaymentData(total_cost=decimal.Decimal(1000)),
            id='need_accept_not_corp',
        ),
    ],
)
async def test_get_payment_data(
        stq3_context: stq_context.Context,
        mock_functions,
        times_called,
        payment_type,
        need_accept,
        expected_payment_data,
):
    PAYMENT_TECH['type'] = payment_type
    PAYMENT_TECH['need_accept'] = need_accept
    payment_data = await get_payment_data(
        context=stq3_context,
        order_data=OrderData(
            brand='',
            country='',
            order={'payment_tech': PAYMENT_TECH},
            order_proc={
                'order': {'performer': {'tariff': {'currency': 'RUB'}}},
            },
        ),
    )
    assert payment_data == expected_payment_data
    assert [
        mock_functions.get_basic_cost.times_called,
        mock_functions.get_tips_percent.times_called,
        mock_functions.get_vat_perc.times_called,
        mock_functions.round_by_currency.times_called,
    ] == times_called
