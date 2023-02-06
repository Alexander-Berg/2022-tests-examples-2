from datetime import timezone, timedelta

from libstall.util import now


async def test_simple(tap, api, dataset):
    with tap.plan(5, 'Обновление курьерской смены'):
        company = await dataset.company()
        cluster = await dataset.cluster()
        store = await dataset.store(company=company, cluster=cluster)

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)

        # Создаём смену
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=started_at,
            closes_at=closes_at,
            delivery_type='foot',
        )

        t = await api(token=company.token)
        await t.post_ok('api_external_courier_shifts_reschedule_next', json={
            'id': courier.external_id,
        })

        t.status_is(200, diag=True)
        t.json_is('next_slot_shift_id', shift.courier_shift_id, 'ID')

        await shift.reload()
        tap.eq(
            shift.started_at,
            started_at + timedelta(minutes=30),
            'started_at'
        )
        tap.eq(
            shift.closes_at,
            closes_at + timedelta(minutes=30),
            'closes_at'
        )


async def test_limit(tap, api, dataset):
    with tap.plan(3, 'Лимит обновления курьерской смены'):
        company = await dataset.company()
        cluster = await dataset.cluster()
        store = await dataset.store(company=company, cluster=cluster)

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)

        # Создаём смену
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=started_at,
            closes_at=closes_at,
            delivery_type='foot',
        )

        t = await api(token=company.token)
        await t.post_ok('api_external_courier_shifts_reschedule_next', json={
            'id': courier.external_id,
            'delta_started': 999999,
        })

        t.status_is(400, diag=True)

        await shift.reload()
        tap.eq(shift.started_at, started_at, 'not updated')


async def test_intersection(tap, api, dataset):
    with tap.plan(4, 'Обновление курьерской смены с пересечением'):
        company = await dataset.company()
        cluster = await dataset.cluster()
        store = await dataset.store(company=company, cluster=cluster)

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)

        # Создаём смену
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=started_at,
            closes_at=closes_at,
            delivery_type='foot',
        )
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=started_at + timedelta(hours=2),
            closes_at=closes_at + timedelta(hours=6),
            delivery_type='foot',
        )

        t = await api(token=company.token)
        await t.post_ok('api_external_courier_shifts_reschedule_next', json={
            'id': courier.external_id,
        })
        t.status_is(400, diag=True)

        await shift.reload()
        tap.eq(
            shift.started_at,
            started_at,
            'started_at'
        )
        tap.eq(
            shift.closes_at,
            closes_at,
            'closes_at'
        )
