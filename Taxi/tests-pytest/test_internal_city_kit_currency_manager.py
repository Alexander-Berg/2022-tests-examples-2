import datetime

import pytest

from taxi.internal.city_kit import currency_manager
from taxi.util import decimal


@pytest.mark.filldb(
    iso_currencies='for_get_all_iso_currencies_codes_test'
)
@pytest.inline_callbacks
def test_get_all_iso_currencies_codes():
    actual_currencies = yield currency_manager.get_all_iso_currencies_codes()
    assert sorted(actual_currencies) == ['BYN', 'EUR', 'RUB']


@pytest.mark.load_data(
    countries='for_get_all_tariff_currencies_test'
)
@pytest.inline_callbacks
def test_get_all_tariff_currencies():
    actual_currencies = yield currency_manager.get_all_tariff_currencies()
    expected_currencies = ['RUB', 'BYR']
    assert actual_currencies == expected_currencies


@pytest.mark.load_data(
    countries='for_is_known_test'
)
@pytest.mark.parametrize('currency,expected_result', [
    ('RUB', True),
    ('USD', False),
])
@pytest.inline_callbacks
def test_is_known(currency, expected_result):
    actual_result = yield currency_manager.is_known(currency)
    assert actual_result is expected_result


@pytest.mark.filldb(
    currency_rates='for_rate_finder_tests'
)
@pytest.mark.parametrize(
    ('from_currencies,min_date,max_date,from_currency,'
     'to_currency,date,expected_rate'
    ),
    [
        (
            ['USD', 'EUR'],
            datetime.date(2016, 8, 1), datetime.date(2016, 8, 13),
            'USD', 'RUB',
            datetime.date(2016, 8, 13), decimal.Decimal('64.3364'),
        ),
        (
            # rate from X to X is always 1
            ['USD', 'EUR'],
            datetime.date(2016, 8, 1), datetime.date(2016, 8, 13),
            'USD', 'USD',
            datetime.date(2099, 8, 13), decimal.Decimal(1),
        ),
        (
            ['USD', 'EUR'],
            datetime.date(1999, 3, 1), datetime.date(2016, 8, 13),
            'USD', 'RUB',
            datetime.date(1999, 3, 17), decimal.Decimal('6.09'),
        ),
        (
            ['USD', 'EUR'],
            datetime.date(1999, 3, 17), datetime.date(2016, 3, 17),
            'USD', 'RUB',
            datetime.date(1999, 3, 17), decimal.Decimal('6.09'),
        ),
        (
            ['USD', 'EUR'],
            datetime.date(2016, 8, 1), datetime.date(2016, 8, 13),
            'EUR', 'RUB',
            datetime.date(2016, 8, 13), decimal.Decimal('71.7158'),
        ),
    ]
)
@pytest.inline_callbacks
def test_rate_finder_find_rate(
        from_currencies, min_date, max_date, from_currency, to_currency, date,
        expected_rate):
    finder = yield currency_manager.create_rate_finder(
        from_currencies=from_currencies,
        min_date=min_date,
        max_date=max_date,
    )
    actual_rate = finder.find_rate(
        from_currency=from_currency,
        to_currency=to_currency,
        date=date,
    )
    assert actual_rate == expected_rate


@pytest.mark.filldb(
    currency_rates='for_rate_finder_tests',
)
@pytest.mark.parametrize(
    'from_currencies,min_date,max_date,from_currency,to_currency,date',
    [
        # min_date is too large
        (
            ['USD', 'EUR'],
            datetime.date(2016, 8, 14), datetime.date(2016, 8, 15),
            'USD', 'RUB',
            datetime.date(2016, 8, 13),
        ),
        # max_date is too small
        (
            ['USD', 'EUR'],
            datetime.date(1998, 8, 1), datetime.date(2016, 8, 12),
            'USD', 'RUB',
            datetime.date(2016, 8, 13),
        ),
        # unknown from_currency
        (
            ['USD', 'EUR'],
            datetime.date(1999, 3, 17), datetime.date(2016, 3, 17),
            'KZT', 'RUB',
            datetime.date(1999, 3, 17),
        ),
        # unknown to_currency
        (
            ['USD', 'EUR'],
            datetime.date(2016, 8, 1), datetime.date(2016, 8, 13),
            'EUR', 'KZT',
            datetime.date(2016, 8, 13),
        ),
    ]
)
@pytest.inline_callbacks
def test_rate_finder_find_rate_failure(
        from_currencies, min_date, max_date, from_currency, to_currency, date):
    finder = yield currency_manager.create_rate_finder(
        from_currencies=from_currencies,
        min_date=min_date,
        max_date=max_date,
    )
    with pytest.raises(currency_manager.RateNotFound):
        finder.find_rate(
            from_currency=from_currency,
            to_currency=to_currency,
            date=date,
        )


@pytest.mark.translations([
    ('tariff', 'currency.rub', 'ru', 'rub.'),
    ('tariff', 'currency.gel', 'ru', 'gel.'),
    ('tariff', 'currency_with_sign.default', 'ru', '$VALUE$ $SIGN$$CURRENCY$'),
])
@pytest.mark.parametrize('args,kwargs,expected_result', [
    ((123.234, 'RUB', 'ru'), {}, '123 rub.'),
    ((123.234, 'GEL', 'ru'), {}, '123,2 gel.'),
    ((123.234, 'RUB', 'ru'), {'do_round': True}, '120 rub.'),
    ((123.500, 'GEL', 'ru'), {'do_round': True}, '123,4 gel.'),
])
@pytest.inline_callbacks
def test_sum_with_currency(args, kwargs, expected_result):
    result = yield currency_manager.sum_with_currency(
        *args, **kwargs
    )
    assert result == expected_result


@pytest.mark.parametrize('args,kwargs,expected_result', [
    (('RUR',), {}, 1),
    (('XXX',), {}, 1),
    (('AMD',), {}, 100),
    (('BYN',), {}, 0.1),
    (('GEL',), {}, 0.2),
    (('KZT',), {}, 10),
    (('UAH',), {}, 0.5),
])
@pytest.inline_callbacks
def test_get_round_factor(args, kwargs, expected_result):
    result = yield currency_manager.get_round_factor(
        *args, **kwargs
    )
    assert result == expected_result


@pytest.mark.parametrize('args,kwargs,expected_result', [
    ((100.05, 'RUB'), {}, 100),
    ((1234, 'AMD'), {}, 1200),
    ((100.9, 'UAH'), {}, 100.5),
    ((109.9, 'KZT'), {}, 100),
])
@pytest.inline_callbacks
def test_round_by_currency(args, kwargs, expected_result):
    result = yield currency_manager.round_by_currency(
        *args, **kwargs
    )
    assert result == expected_result
