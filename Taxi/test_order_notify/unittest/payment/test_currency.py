import decimal

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.payment import currency as curr
from order_notify.repositories.payment.currency import CurrencyManager


@pytest.mark.parametrize(
    'value, locale, expected_value',
    [
        pytest.param(None, 'ru', None, id='value_None'),
        pytest.param(
            decimal.Decimal(1.1236), 'ru', '1,124 sign', id='locale_ru',
        ),
        pytest.param(
            decimal.Decimal(1.1234), 'en', '1.123 sign', id='locale_en',
        ),
    ],
)
def test_add_currency_sign(value, locale, expected_value):
    currency_manager = CurrencyManager(
        currency_sign='{value} sign', value_format='.###', locale=locale,
    )
    value_with_currency_sign = currency_manager.add_currency_sign(value=value)
    assert value_with_currency_sign == expected_value


@pytest.fixture(name='mock_functions')
def mock_currency_manager_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_currency_sign = Counter()
            self.get_value_format = Counter()

    counters = Counters()

    @patch('order_notify.repositories.payment.currency.' 'get_currency_sign')
    def _get_currency_sign(
            context: stq_context.Context, currency: str, locale: str,
    ) -> str:
        counters.get_currency_sign.call()
        assert locale == 'ru'
        assert currency == 'RUB'
        return '{value} sign'

    @patch('order_notify.repositories.payment.currency.' 'get_value_format')
    def _get_value_format(context: stq_context.Context, currency: str) -> str:
        counters.get_value_format.call()
        assert currency == 'RUB'
        return '.###'

    return counters


def test_get_currency_manager(
        stq3_context: stq_context.Context, mock_functions,
):
    currency_manager = curr.get_currency_manager(
        context=stq3_context, country_currency='RUB', locale='ru',
    )
    assert currency_manager.currency_sign == '{value} sign'
    assert currency_manager.value_format == '.###'
    assert currency_manager.locale == 'ru'


@pytest.mark.parametrize(
    'payment_currency, expected_value_format',
    [
        pytest.param('RUB', '.##', id='currency_in_config'),
        pytest.param('BYN', '.#', id='currency_not_in_config'),
        pytest.param('KZT', '0', id='no_default_in_config'),
    ],
)
@pytest.mark.config(
    CURRENCY_FORMATTING_RULES={
        'RUB': {'__default__': 2},
        '__default__': {'__default__': 1},
        'KZT': {},
    },
)
def test_get_value_format(
        stq3_context: stq_context.Context,
        payment_currency,
        expected_value_format,
):
    value_format = curr.get_value_format(
        context=stq3_context, currency=payment_currency,
    )
    assert value_format == expected_value_format


@pytest.mark.parametrize(
    'payment_currency, expected_currency_sign',
    [
        pytest.param('GBP', 'GBP_SIGN{value}', id='gbp_template_exist_sign'),
        pytest.param(
            'RUB', '{value} RUB_SIGN', id='default_template_exist_sign',
        ),
        pytest.param(
            'BYN', '{value} byn', id='default_template_sign_not_exist',
        ),
    ],
)
@pytest.mark.translations(
    tariff={
        'currency_with_sign.gbp': {'ru': '$SIGN$$VALUE$$CURRENCY$'},
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.gbp': {'ru': 'GBP_SIGN'},
        'currency_sign.rub': {'ru': 'RUB_SIGN'},
        'currency.byn': {'ru': 'byn'},
    },
)
def test_get_currency_sign(
        stq3_context: stq_context.Context,
        payment_currency,
        expected_currency_sign,
):
    currency_sign = curr.get_currency_sign(
        context=stq3_context, currency=payment_currency, locale='ru',
    )
    assert currency_sign == expected_currency_sign


@pytest.mark.parametrize(
    'payment_currency, expected_round',
    [
        pytest.param('GBP', 16, id='no_currency'),
        pytest.param('RUB', 15, id='exist_currency'),
    ],
)
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'RUB': {'__default__': 3},
        '__default__': {'__default__': 1},
    },
)
def test_round_by_currency(
        stq3_context: stq_context.Context, payment_currency, expected_round,
):
    curr_round = curr.round_by_currency(
        context=stq3_context, cost=16, currency=payment_currency,
    )
    assert curr_round == expected_round
