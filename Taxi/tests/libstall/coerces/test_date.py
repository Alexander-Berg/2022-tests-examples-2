import datetime
from libstall.model.coerces import date

def test_coerce(tap):
    with tap.plan(2):
        tap.eq(date(None), None, 'None')
        d = date('2019-02-03')
        tap.isa_ok(d, datetime.date, 'распарсено')

