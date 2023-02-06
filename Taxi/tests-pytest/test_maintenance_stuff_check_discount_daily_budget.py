import datetime

import pytest

from taxi.core import async
from taxi_maintenance.stuff import check_discounts_daily_budget


@pytest.mark.now('2018-05-16T18:35:34.0')
@pytest.inline_callbacks
def test_check_budget(patch):

    @patch('taxi.external.startrack.create_ticket')
    @async.inline_callbacks
    def create_ticket(request):
        yield async.return_value()

    @patch('taxi_maintenance.stuff.check_discounts_daily_budget'
           '.get_discount_expenses_from_yt')
    def discounts_expenses_from_yt(since, to):
        class DymmyTable(object):
            def __init__(self):
                self.rows = [
                    ('14a89eeb265545399ce536af9918fa08', '263.9'),
                    ('36d593b32f4d419b92a35163cbec8b18', '100.51'),
                    ('dd591323449346f8ad031bc2728ecdd1', '200.00')
                ]
        return DymmyTable()

    yield check_discounts_daily_budget.do_stuff(datetime.datetime.utcnow())
    ticket_description = (
        'Discount in zone moscow with description '
        'test_discount2 and id dd591323449346f8ad031bc2728ecdd1'
        ' had exceeded budget: 200.00. \nPlanned budget'
        ' 40.00, overdraft 160.00'
    )

    assert create_ticket.calls == [
        {
            'args': ({
                'description': ticket_description,
                'queue': 'DISCOUNTSBUDGET',
                'summary': '[discounts audit] overdraft 160.00'
            },),
            'kwargs': {}
        }
    ]
