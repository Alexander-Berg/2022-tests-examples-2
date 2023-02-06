# pylint: disable=unused-variable
from datetime import timedelta

import pytest


async def test_activity(api, dataset, tap, now, time2iso_utc):
    with tap.plan(11, 'Получение активности'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store   = await dataset.store(cluster=cluster, company=company)

        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=_now - timedelta(days=2),
            closes_at=_now - timedelta(days=2) + timedelta(hours=4),
        )
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(days=2),
            closes_at=_now + timedelta(days=2) + timedelta(hours=4),
        )

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_courier_shifts_activity',
            json={'ids': [courier.external_id]},
        )
        t.status_is(200, diag=True)

        t.json_is('items.0.courier_id', courier.external_id)
        t.json_is(
            'items.0.last_activity_at',
            time2iso_utc(shift1.started_at)
        )
        t.json_is(
            'items.0.planned_activity_at',
            time2iso_utc(shift2.started_at)
        )
        t.json_is(
            'items.0.shifts.0.started_at',
            time2iso_utc(shift1.started_at)
        )
        t.json_is(
            'items.0.shifts.0.finished_at',
            time2iso_utc(shift1.closes_at)
        )
        t.json_is(
            'items.0.shifts.1.started_at',
            time2iso_utc(shift2.started_at)
        )
        t.json_is(
            'items.0.shifts.1.finished_at',
            time2iso_utc(shift2.closes_at)
        )
        t.json_hasnt('items.0.shifts.2')
        t.json_hasnt('items.1')


async def test_partial_closed(api, dataset, tap, now, time2iso_utc):
    with tap.plan(9, 'Есть только закрытая смена, будущей нет'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store   = await dataset.store(cluster=cluster, company=company)

        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=_now - timedelta(days=2),
            closes_at=_now - timedelta(days=2) + timedelta(hours=4),
        )

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_courier_shifts_activity',
            json={'ids': [courier.external_id]},
        )
        t.status_is(200, diag=True)

        t.json_is('items.0.courier_id', courier.external_id)
        t.json_is(
            'items.0.last_activity_at',
            time2iso_utc(shift1.started_at)
        )
        t.json_is(
            'items.0.planned_activity_at',
            None
        )
        t.json_is(
            'items.0.shifts.0.started_at',
            time2iso_utc(shift1.started_at)
        )
        t.json_is(
            'items.0.shifts.0.finished_at',
            time2iso_utc(shift1.closes_at)
        )
        t.json_hasnt('items.0.shifts.1')
        t.json_hasnt('items.1')


async def test_partial_waiting(api, dataset, tap, now, time2iso_utc):
    with tap.plan(9, 'Есть только будущая смена, старой нет'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store   = await dataset.store(cluster=cluster, company=company)

        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(days=2),
            closes_at=_now + timedelta(days=2) + timedelta(hours=4),
        )

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_courier_shifts_activity',
            json={'ids': [courier.external_id]},
        )
        t.status_is(200, diag=True)

        t.json_is('items.0.courier_id', courier.external_id)
        t.json_is(
            'items.0.last_activity_at',
            None
        )
        t.json_is(
            'items.0.planned_activity_at',
            time2iso_utc(shift2.started_at)
        )
        t.json_is(
            'items.0.shifts.0.started_at',
            time2iso_utc(shift2.started_at)
        )
        t.json_is(
            'items.0.shifts.0.finished_at',
            time2iso_utc(shift2.closes_at)
        )
        t.json_hasnt('items.0.shifts.1')
        t.json_hasnt('items.1')


async def test_nearly(api, dataset, tap, now, time2iso_utc):
    with tap.plan(6, 'В параметрах показываем ближайшие смены'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store   = await dataset.store(cluster=cluster, company=company)

        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=_now - timedelta(days=2),
            closes_at=_now - timedelta(days=2) + timedelta(hours=4),
        )

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=_now - timedelta(days=1),
            closes_at=_now - timedelta(days=1) + timedelta(hours=4),
        )

        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(days=2),
            closes_at=_now + timedelta(days=2) + timedelta(hours=4),
        )

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(days=3),
            closes_at=_now + timedelta(days=3) + timedelta(hours=4),
        )

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_courier_shifts_activity',
            json={'ids': [courier.external_id]},
        )
        t.status_is(200, diag=True)

        t.json_is('items.0.courier_id', courier.external_id)
        t.json_is(
            'items.0.last_activity_at',
            time2iso_utc(shift1.started_at)
        )
        t.json_is(
            'items.0.planned_activity_at',
            time2iso_utc(shift2.started_at)
        )
        t.json_hasnt('items.1')


async def test_alien(api, dataset, tap, now, uuid):
    with tap.plan(3, 'Курьер не найден'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store   = await dataset.store(cluster=cluster, company=company)

        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=_now - timedelta(days=2),
            closes_at=_now - timedelta(days=2) + timedelta(hours=4),
        )
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(days=2),
            closes_at=_now + timedelta(days=2) + timedelta(hours=4),
        )

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_courier_shifts_activity',
            json={'ids': [uuid()]},
        )
        t.status_is(200, diag=True)

        t.json_hasnt('items.0')


async def test_too_old(api, dataset, tap, now):
    with tap.plan(3, 'Слишком старая'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store   = await dataset.store(cluster=cluster, company=company)

        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=_now - timedelta(days=5),
            closes_at=_now - timedelta(days=5) + timedelta(hours=4),
        )

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_courier_shifts_activity',
            json={'ids': [courier.external_id]},
        )
        t.status_is(200, diag=True)

        t.json_hasnt('items.0')


@pytest.mark.parametrize('status', ['absent', 'closed', 'cancelled'])
async def test_status(api, dataset, tap, now, status):
    with tap.plan(3, 'Учитываем только выполнявшиеся'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store   = await dataset.store(cluster=cluster, company=company)

        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status=status,
            started_at=_now - timedelta(days=5),
            closes_at=_now - timedelta(days=5) + timedelta(hours=4),
        )

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_courier_shifts_activity',
            json={'ids': [courier.external_id]},
        )
        t.status_is(200, diag=True)

        t.json_hasnt('items.0')
