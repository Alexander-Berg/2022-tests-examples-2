import datetime

from taxi.internal import dbh
from taxi.util import decimal

import pytest


@pytest.mark.filldb(
    currency_rates='for_find_rate_test',
)
@pytest.mark.parametrize('from_currency,to_currency,date,expected_rate', [
    # rate from X to X is always 1
    ('USD', 'USD', datetime.date(2099, 8, 13), decimal.Decimal(1)),
    ('USD', 'RUB', datetime.date(2016, 8, 13), decimal.Decimal('64.3364')),
    ('USD', 'RUB', datetime.date(1999, 3, 17), decimal.Decimal('6.09')),
])
@pytest.inline_callbacks
def test_find_rate(from_currency, to_currency, date, expected_rate):
    actual_rate = yield dbh.currency_rates.Doc.find_rate(
        from_currency=from_currency,
        to_currency=to_currency,
        date=date
    )
    assert actual_rate == expected_rate


@pytest.mark.filldb(
    currency_rates='for_find_rate_test',
)
@pytest.mark.parametrize('from_currency,to_currency,date,expected_exception', [
    # we only know rate for opposite direction
    ('RUB', 'USD', datetime.date(2016, 8, 13), dbh.currency_rates.NotFound),
    # there's know data about datetime.date(2016, 8, 12)
    ('USD', 'RUB', datetime.date(2016, 8, 12), dbh.currency_rates.NotFound),
])
@pytest.inline_callbacks
def test_find_rate_failure(
        from_currency, to_currency, date, expected_exception):
    with pytest.raises(expected_exception):
        yield dbh.currency_rates.Doc.find_rate(
            from_currency=from_currency,
            to_currency=to_currency,
            date=date,
        )


@pytest.mark.filldb(
    currency_rates='for_set_rate_test',
)
@pytest.mark.parametrize(
    'from_currency,to_currency,date,rate,expected_count',
    [
        # add new
        ('USD', 'RUB', datetime.date(2016, 8, 14), decimal.Decimal('90.0'), 2),
        # overwrite existing
        ('USD', 'RUB', datetime.date(2016, 8, 13), decimal.Decimal('30.0'), 1),
    ]
)
@pytest.inline_callbacks
def test_set_rate(from_currency, to_currency, date, rate, expected_count):
    yield dbh.currency_rates.Doc.set_rate(
        from_currency=from_currency,
        to_currency=to_currency,
        date=date,
        rate=rate,
    )
    new_rate = yield dbh.currency_rates.Doc.find_rate(
        from_currency=from_currency,
        to_currency=to_currency,
        date=date,
    )
    assert new_rate == rate
    actual_count = yield dbh.currency_rates.Doc._find().count()
    assert actual_count == expected_count
