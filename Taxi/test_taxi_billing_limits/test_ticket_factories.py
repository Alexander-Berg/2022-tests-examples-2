# pylint: disable=redefined-outer-name
import datetime
import decimal

import pytest

from taxi_billing_limits import limits
from taxi_billing_limits import tickets


@pytest.fixture
def limit():
    return limits.Limit(
        ref='badc0de',
        label='moscow',
        tickets=['TAXIRATE-1'],
        currency='USD',
        account_id='budget/badc0de',
        approvers=['me'],
        windows=[
            limits.TumblingWindow(
                start=datetime.datetime(
                    2019, 9, 25, 2, 27, 0, tzinfo=datetime.timezone.utc,
                ),
                value=decimal.Decimal(1000),
                threshold=103,
                label='Недельный',
                size=604800,
            ),
        ],
    )


@pytest.mark.now('2019-10-01T10:00:00.000000+00:00')
def test_weekly_factory(limit):
    ticket = tickets.Ticket.make(
        limit=limit,
        window=limit.windows[0],
        balance=decimal.Decimal(1100),
        now=datetime.datetime.now(tz=datetime.timezone.utc),
    )
    assert isinstance(ticket, tickets.Ticket)
    assert ticket.queue == 'TAXIBUDGETALERT'
    assert ticket.summary == (
        'moscow - Недельный лимит исчерпан на 103% - 01.10.2019'
    )
    assert ticket.description == (
        '1. Субсидии по тикету: TAXIRATE-1\n'
        '2. Плановая величина расходов: 1000.00 USD\n'
        '3. Фактическая величина расходов: 1100.00 USD\n'
        '4. Исчерпание произошло за 6 д. 7 ч. 33 мин.\n'
    )
    assert ticket.link_to == ['TAXIRATE-1']
    assert ticket.notify == ['me']
