from datetime import timezone, timedelta

import pytest

from libstall.util import now
from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_save_time_processing(tap, api, dataset, time2iso_utc):
    with tap.plan(10, 'Обновление времени завершения требует подтверждения'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store)
        courier = await dataset.courier(cluster=cluster)

        _now            = now(tz=timezone.utc).replace(microsecond=0)
        _started_at     = _now - timedelta(hours=1)
        _closes_at      = _now + timedelta(hours=3)
        _new_closes_at  = _closes_at + timedelta(hours=1, minutes=35)

        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            user=user,
            courier=courier,
            status='processing',
            started_at=_started_at,
            closes_at=_closes_at,
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'started_at': time2iso_utc(shift.started_at),
                            'closes_at': time2iso_utc(_new_closes_at),
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('courier_shift.courier_shift_id', shift.courier_shift_id)
        t.json_is('courier_shift.started_at', time2iso_utc(_started_at))
        t.json_is(
            'courier_shift.closes_at',
            time2iso_utc(_closes_at),
            'время сразу не применено'
        )
        t.json_is('courier_shift.shift_events.0.type', 'edit')
        t.json_is('courier_shift.shift_events.1.type', 'change')
        t.json_is('courier_shift.shift_events.1.detail.old.closes_at',
                  time2iso_utc(_closes_at))
        t.json_is('courier_shift.shift_events.1.detail.new.closes_at',
                  time2iso_utc(_new_closes_at))


async def test_disable_approve(tap, api, dataset, time2iso_utc):
    with tap.plan(7, 'Обновление времени завершения при отключеии аппрува'):
        cluster = await dataset.cluster(
            courier_shift_setup = {
                'shift_approve_disable': True,
            },
        )
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store)
        courier = await dataset.courier(cluster=cluster)

        _now            = now(tz=timezone.utc).replace(microsecond=0)
        _started_at     = _now - timedelta(hours=1)
        _closes_at      = _now + timedelta(hours=3)
        _new_closes_at  = _closes_at + timedelta(hours=1, minutes=35)

        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            user=user,
            courier=courier,
            status='processing',
            started_at=_started_at,
            closes_at=_closes_at,
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'started_at': time2iso_utc(shift.started_at),
                            'closes_at': time2iso_utc(_new_closes_at),
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('courier_shift.courier_shift_id', shift.courier_shift_id)
        t.json_is('courier_shift.started_at', time2iso_utc(_started_at))
        t.json_is(
            'courier_shift.closes_at',
            time2iso_utc(_new_closes_at),
            'время применено сразу'
        )

        with await shift.reload() as shift:
            tap.ok(not shift.event_change(), 'нет события для аппрува')


async def test_save_update_time_range_err(tap, api, dataset):
    with tap.plan(6, 'Обновление смены с кривым стартом/окончанием'):
        _now = now(tz=timezone.utc).replace(microsecond=0)
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        cs_target = await dataset.courier_shift(
            store=store,
            started_at=_now,
            closes_at=_now + timedelta(hours=4),
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': cs_target.courier_shift_id,
                            'started_at': cs_target.closes_at,
                            'closes_at': cs_target.started_at,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_TIME_RANGE')

        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': cs_target.courier_shift_id,
                'closes_at': cs_target.started_at - timedelta(minutes=1),
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_TIME_RANGE')


async def test_save_time_started_err(tap, api, dataset):
    with tap.plan(3, 'Обновление смены с началом в прошлом.'):
        _now = now(tz=timezone.utc).replace(microsecond=0)
        store = await dataset.store()
        shift = await dataset.courier_shift(
            store=store,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=5),
        )
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'started_at': _now - timedelta(minutes=1),
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_TIME_RANGE')


@pytest.mark.parametrize('duration', [1, 9])
async def test_save_update_duration_err(tap, api, dataset, duration):
    with tap.plan(3, 'Обновление смены со слишком малой/большой длительностью'):
        _now = now(tz=timezone.utc).replace(microsecond=0)
        cluster = await dataset.cluster(courier_shift_setup={
            'slot_min_size': 2 * 3600,
            'slot_max_size': 8 * 3600,
        })
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=5)

        cs_target = await dataset.courier_shift(
            store=store,
            started_at=started_at,
            closes_at=closes_at,
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': cs_target.courier_shift_id,
                            'closes_at': started_at + timedelta(hours=duration),
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_STORE_COURIER_SHIFT_SETUP')


async def test_save_beginner_started_at(
    tap, api, dataset, time2iso_utc, push_events_cache, job,
):
    with tap.plan(10, 'У курьера новичка сдвигают время начала смены'):
        cluster = await dataset.cluster(courier_shift_setup={
            'shift_approve_disable': True,
        })
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store)
        courier = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])

        _now = now(tz=timezone.utc).replace(microsecond=0)

        # смена-новичок
        shift_1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            tags=[TAG_BEGINNER],
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=11),
            closes_at=_now + timedelta(hours=13),
            tags=[],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift_1.courier_shift_id,
                # сдвигаем на 24 часа
                'started_at': time2iso_utc(_now + timedelta(hours=1 + 24)),
                'closes_at': time2iso_utc(_now + timedelta(hours=3 + 24)),
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await push_events_cache(shift_1, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'назначена')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера назначен')
            tap.eq(shift.tags, [], 'больше не новичок')

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'назначена')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера назначен')
            tap.eq(shift.tags, [TAG_BEGINNER], 'теперь смена - новичок')


async def test_save_beginner_closes_at(
    tap, api, dataset, time2iso_utc, push_events_cache, job,
):
    with tap.plan(10, 'У курьера новичка сдвигают НЕ время начала'):
        cluster = await dataset.cluster(courier_shift_setup={
            'shift_approve_disable': True,
        })
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store)
        courier = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])

        _now = now(tz=timezone.utc).replace(microsecond=0)

        # смена-новичок
        shift_1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            tags=[TAG_BEGINNER],
            guarantee=200,
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=11),
            closes_at=_now + timedelta(hours=13),
            tags=[],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift_1.courier_shift_id,
                'closes_at': time2iso_utc(_now + timedelta(hours=4)),
                'guarantee': '100',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await push_events_cache(shift_1, job_method='job_recheck_beginner')
        tap.ok(await job.take() is None, 'Задание нет')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'назначена')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера назначен')
            tap.eq(shift.tags, [TAG_BEGINNER], 'все еще новичок')

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'назначена')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера назначен')
            tap.eq(shift.tags, [], 'все еще нет')
