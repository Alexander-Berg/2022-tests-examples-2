import datetime
import decimal

import pytest

from taxi_billing_limits import limits
from taxi_billing_limits.database import gateway as db

_LIMIT = limits.Limit(
    ref='tumbling',
    currency='RUB',
    label='moscow',
    account_id='budget/tumbling',
    tickets=['TAXIRATE-1'],
    approvers=[],
    tags=[],
    windows=[
        limits.TumblingWindow(
            pkey=1,
            value=decimal.Decimal(10000),
            size=604800,
            threshold=100,
            label='Недельный',
            start=datetime.datetime(
                2000, 1, 1, 18, tzinfo=datetime.timezone.utc,
            ),
        ),
    ],
    notifications=[
        limits.Notification(kind='ticket', queue='TAXIBUDGETALERT'),
    ],
)


@pytest.mark.parametrize(
    'ref,expected', (('unknown', None), ('tumbling', _LIMIT)),
)
@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
async def test_get_limit_by_ref(web_context, ref, expected):
    repo = db.Gateway(context=web_context)
    limit = await repo.get_limit_by_ref(ref=ref)
    assert limit == expected


@pytest.mark.parametrize(
    'window_pk,expected', ((1, None), (3, 'TAXIBUDGETALERT-10')),
)
@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
async def test_get_attached_ticket(web_context, window_pk, expected):
    repo = db.Gateway(context=web_context)
    key = await repo.get_attached_ticket(window_pk=window_pk)
    assert key == expected


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
async def test_attach_ticket(web_context, pgsql):
    key = 'TAXIBUDGETALERT-1'
    repo = db.Gateway(context=web_context)
    await repo.attach_ticket(window_pk=2, key=key)
    with pgsql['billing_limits@0'].cursor() as cursor:
        cursor.execute(
            f'select id from limits.windows where ticket=\'{key}\';',
        )
        assert [row[0] for row in cursor.fetchall()] == [2]


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.parametrize(
    'limit_ref,expected', (('tumbling', 0), ('test_notified', 18232)),
)
async def test_get_window_last_notified(web_context, limit_ref, expected):
    repo = db.Gateway(context=web_context)
    limit = await repo.get_limit_with_windows_by_ref(ref=limit_ref)
    last_notified = await repo.get_window_last_notified(
        window_pk=limit.windows[0].pkey,
    )
    assert last_notified == expected


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.parametrize(
    'pkey,wid,expected',
    ((1, 1111, True), (4, 18232, False), (4, 18250, True)),
)
async def test_set_window_last_notified(
        web_context, pgsql, pkey, wid, expected,
):
    repo = db.Gateway(context=web_context)
    success = await repo.set_window_last_notified(
        window_pk=pkey, last_notified=wid,
    )
    assert success is expected
    with pgsql['billing_limits@0'].cursor() as cursor:
        cursor.execute(
            f'select id from limits.windows where last_notified_wid = {wid};',
        )
        rows = [row[0] for row in cursor.fetchall()]
        assert rows == [pkey]
