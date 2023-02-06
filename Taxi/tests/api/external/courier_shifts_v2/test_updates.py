# pylint: disable=too-many-locals

from datetime import timedelta

import pytest


@pytest.mark.parametrize('subscribe', [True, False])
async def test_simple(api, dataset, tap, now, time2iso_utc, subscribe):
    with tap.plan(12, 'Репликация смен'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        courier = await dataset.courier()

        _now = now().replace(microsecond=0)

        started_real = _now - timedelta(hours=2, minutes=5)
        stopped_plan = _now + timedelta(hours=2)
        courier_shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=_now - timedelta(hours=2),
            closes_at=stopped_plan,
            shift_events=[
                {'type': 'started', 'created': started_real},
            ],
        )

        await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_now + timedelta(hours=4),
            closes_at=_now + timedelta(hours=6),
        )

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_courier_shifts_v2_updates',
            json={'cursor': None, 'subscribe': subscribe},
        )
        t.status_is(200, diag=True)

        t.json_has('cursor')
        t.json_has('shifts.0')
        t.json_hasnt('shifts.1')

        shifts = {x['shift_id']: x for x in t.res['json']['shifts']}

        data = shifts[courier_shift.courier_shift_id]
        tap.eq(
            data['courier_id'],
            courier.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data['zone_group_id'], store.store_id, 'zone_group_id')
        tap.eq(data['status'], 'in_progress', 'status')
        tap.eq(data['started_at'], time2iso_utc(started_real), 'started_at')
        tap.eq(data['closes_at'], time2iso_utc(stopped_plan), 'closes_at')
        tap.eq(data['store_id'], store.store_id, 'store_id')
        tap.eq(data['store_external_id'], store.external_id, 'external_id')
