from datetime import timedelta

import pytest

from stall.client.grocery_checkins import GroceryCheckinsError
from stall.client.grocery_checkins import client as gc_client


async def test_start(
        tap, dataset, now, push_events_cache, job, time2time
):
    with tap.plan(8, 'Запуск отложенной паузы по чекину курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[{'type': 'schedule_pause'}]
        )

        courier.checkin_time = now()
        tap.ok(await courier.save(), 'Курьер зачекинился')

        await push_events_cache(courier, job_method='job_start_schedule_pause')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            tap.eq(len(shift.shift_events), 2, 'Событие смены добавлено')

            with shift.shift_events[0] as event:
                tap.eq(event.type, 'schedule_pause', 'schedule_pause')

            with shift.shift_events[1] as event:
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.courier_id, None, 'courier_id=None')
                tap.eq(event.user_id, None, 'user_id=None')
                tap.eq(
                    time2time(event.detail.get('ends_at')),
                    shift.closes_at,
                    'ends_at'
                )


async def test_not_scheduled(tap, dataset, now, push_events_cache, job):
    with tap.plan(3, 'Пауза не была заявлена'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[]
        )

        courier.checkin_time = now()
        tap.ok(await courier.save(), 'Курьер зачекинился')

        await push_events_cache(courier, job_method='job_start_schedule_pause')
        tap.ok(not await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            tap.eq(len(shift.shift_events), 0, 'Событий смены нет')


async def test_not_checkin(tap, dataset, now, push_events_cache, job):
    with tap.plan(4, 'Курьер не зачекинился'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[]
        )

        courier.checkin_time = now()
        tap.ok(await courier.save(), 'Курьер зачекинился')

        await push_events_cache(courier, job_method='job_start_schedule_pause')

        courier.checkin_time = None
        tap.ok(await courier.save(), 'Курьер ушел с лавки')

        tap.ok(not await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            tap.eq(len(shift.shift_events), 0, 'Событий смены нет')


async def test_old_checkin(tap, dataset, now, push_events_cache, job):
    with tap.plan(3, 'Чекин курьера устарел'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[]
        )

        _now = now()

        courier.checkin_time = _now
        courier.last_order_time = _now + timedelta(seconds=1)
        tap.ok(await courier.save(), 'Курьер зачекинился, но уже схватил заказ')

        await push_events_cache(courier, job_method='job_start_schedule_pause')

        tap.ok(not await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            tap.eq(len(shift.shift_events), 0, 'Событий смены нет')


async def test_user(
        tap, dataset, now, push_events_cache, job, time2time
):
    with tap.plan(9, 'Параметры пользователя должны прорасти в паузу'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        user = await dataset.user(store=store)

        _now = now().replace(microsecond=0)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            cluster=cluster,
            status='processing',
            started_at=_now,
            closes_at=_now + timedelta(hours=4),
            shift_events=[{
                'user_id': user.user_id,
                'type': 'schedule_pause',
                'detail': {'duration': 600},
            }]
        )

        courier.checkin_time = now()
        tap.ok(await courier.save(), 'Курьер зачекинился')

        await push_events_cache(courier, job_method='job_start_schedule_pause')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            tap.eq(len(shift.shift_events), 2, 'Событие смены добавлено')

            with shift.shift_events[0] as event:
                tap.eq(event.type, 'schedule_pause', 'schedule_pause')

            with shift.shift_events[1] as event:
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.courier_id, None, 'courier_id=None')
                tap.eq(event.user_id, None, 'user_id=None')
                tap.eq(event.detail.get('duration'), 600, 'duration')
                tap.eq(
                    time2time(event.detail.get('ends_at')),
                    event.created + timedelta(seconds=600),
                    'ends_at'
                )


async def test_grocery_checkins_sync(
        tap, dataset, ext_api, now, push_events_cache, job, time2iso,
):
    with tap.plan(4, 'оповещаем grocery-checkins о паузе'):
        _calls = []

        async def handle(request):
            data = await request.json()
            _calls.append(data)
            return {}

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[{'type': 'schedule_pause'}]
        )

        courier.checkin_time = now()
        tap.ok(await courier.save(), 'Курьер зачекинился')

        async with await ext_api('grocery_checkins', handle):
            await push_events_cache(
                courier, job_method='job_start_schedule_pause'
            )
            tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            event = shift.event_paused()
            tap.ok(event, 'shift is on pause')
            tap.eq(_calls, [{
                'performer_id': courier.external_id,
                'shift_id': shift.courier_shift_id,
                'paused_at': time2iso(event.created)
            }], 'grocery_checkins called once')


@pytest.mark.parametrize('exc_cls', [GroceryCheckinsError, Exception])
async def test_grocery_checkins_fail(
        tap, dataset, now, push_events_cache, job,
        monkeypatch, exc_cls,
):
    with tap.plan(3, 'при ошибках обращения к grocery-checkins не падаем'):
        # pylint: disable=unused-argument
        async def raiser(self, *args, **kwargs):
            raise exc_cls

        monkeypatch.setattr(gc_client, gc_client.shift_pause.__name__, raiser)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[{'type': 'schedule_pause'}]
        )

        courier.checkin_time = now()
        tap.ok(await courier.save(), 'Курьер зачекинился')

        await push_events_cache(
            courier, job_method='job_start_schedule_pause'
        )
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            event = shift.event_paused()
            tap.ok(event, 'shift is on pause')
