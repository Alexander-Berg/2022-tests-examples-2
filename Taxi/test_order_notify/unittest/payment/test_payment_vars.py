import decimal
import typing

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData
from order_notify.repositories.payment import payment_vars
from order_notify.repositories.payment.currency import CurrencyManager
from order_notify.repositories.payment.payment_info import PaymentData


DEFAULT_ORDER_DATA = OrderData(
    brand='',
    country='',
    order={},
    order_proc={'order': {'performer': {'tariff': {'currency': 'RUB'}}}},
)


@pytest.fixture(name='mock_functions')
def mock_payment_vars_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_payment_data = Counter()
            self.get_currency_manager = Counter()
            self.get_payment_method_vars = Counter()

    counters = Counters()

    @patch('order_notify.repositories.payment.currency.get_currency_manager')
    def _get_currency_manager(
            context: stq_context.Context,
            country_currency: typing.Optional[str],
            locale: str,
    ) -> CurrencyManager:
        counters.get_currency_manager.call()
        assert locale == 'ru'
        assert country_currency == 'RUB'
        return CurrencyManager(
            currency_sign='{value} sign', value_format='.###', locale=locale,
        )

    @patch('order_notify.repositories.payment.payment_info.get_payment_data')
    async def _get_payment_data(
            context: stq_context.Context, order_data: OrderData,
    ) -> PaymentData:
        counters.get_payment_data.call()
        assert order_data == DEFAULT_ORDER_DATA
        return PaymentData(
            total_cost=decimal.Decimal(1.945),
            cost_without_vat=decimal.Decimal(1.222),
            tips=decimal.Decimal(1.452),
            tips_percent=20,
            vat_value=decimal.Decimal(0.578),
            vat_perc=20,
        )

    @patch(
        'order_notify.repositories.payment.payment_method.'
        'get_payment_method_vars',
    )
    async def _get_payment_method_vars(
            context: stq_context.Context, order_data: OrderData, locale: str,
    ) -> dict:
        counters.get_payment_method_vars.call()
        assert order_data == DEFAULT_ORDER_DATA
        assert locale == 'ru'
        return {}

    return counters


async def test_get_payment_vars(
        stq3_context: stq_context.Context, mock_functions,
):
    expected_payment_section_vars = {
        'show_fare_with_vat_only': False,
        'total_cost_sign': '1,945 sign',
        'cost_without_vat_sign': '1,222 sign',
        'tips_sign': '1,452 sign',
        'tips_percent': 20,
        'vat_value_sign': '0,578 sign',
        'vat_perc': 20,
    }
    payment_section_vars = await payment_vars.get_payment_vars(
        context=stq3_context,
        order_data=DEFAULT_ORDER_DATA,
        show_fare_with_vat_only=False,
        locale='ru',
    )
    assert payment_section_vars == expected_payment_section_vars
    assert mock_functions.get_payment_data.times_called == 1
    assert mock_functions.get_currency_manager.times_called == 1
    assert mock_functions.get_payment_method_vars.times_called == 1
