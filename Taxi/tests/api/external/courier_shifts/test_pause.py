from datetime import timedelta

import pytest


async def test_simple(tap, api, dataset, time2time):
    with tap.plan(7, 'Остановка смены'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            status='processing',
            courier=courier,
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )

        t = await api(token=company.token)
        await t.post_ok('api_external_courier_shifts_pause', json={
            'id': courier.external_id,
            'ticket': 'LAVKADEV-4917',
        })

        t.status_is(200, diag=True)
        t.json_is('current_slot_shift_id', shift.courier_shift_id, 'ID')

        pause_ends_at = t.res['json']['pause_ends_at']
        tap.eq(time2time(pause_ends_at), shift.closes_at, 'pause_ends_at')

        await shift.reload()
        pause = shift.shift_events[-2]
        tap.ok(pause, 'Пауза была')

        event = shift.shift_events[-1]
        tap.eq(event.type, 'paused', 'paused')
        tap.eq(
            time2time(event.detail.get('ends_at')),
            shift.closes_at,
            'ends_at'
        )


async def test_no_access(tap, api, dataset):
    with tap.plan(2, 'Остановка смены: нет прав'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        company_external = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        await dataset.courier_shift(
            store=store,
            status='processing',
            courier=courier,
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )

        t = await api(token=company_external.token)
        await t.post_ok('api_external_courier_shifts_pause', json={
            'id': courier.external_id,
        })
        t.status_is(403, diag=True)


@pytest.mark.skip('Пока не вынесли pause в отдельную функцию с учётом времени')
async def test_specific_time(tap, api, dataset, time2time):
    with tap.plan(7, 'Остановка смены на заданное время'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            status='processing',
            courier=courier,
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )

        t = await api(token=company.token)
        await t.post_ok('api_external_courier_shifts_pause', json={
            'id': courier.external_id,
            'duration': 1800,
        })

        t.status_is(200, diag=True)
        t.json_is('current_slot_shift_id', shift.courier_shift_id, 'ID')

        await shift.reload()
        pause = shift.shift_events[-2]
        tap.ok(pause, 'Пауза была')

        pause_ends_at = t.res['json']['pause_ends_at']
        tap.eq(
            time2time(pause_ends_at),
            pause.created + timedelta(seconds=1800),
            'pause_ends_at'
        )

        event = shift.shift_events[-1]
        tap.eq(event.type, 'paused', 'paused')
        tap.eq(
            time2time(event.detail.get('ends_at')),
            pause.created + timedelta(seconds=1800),
            'ends_at'
        )
