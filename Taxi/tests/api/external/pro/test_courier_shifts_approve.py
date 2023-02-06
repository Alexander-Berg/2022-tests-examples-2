# pylint: disable=too-many-locals

from datetime import timedelta, time

import pytest
import pytz

from stall.model.courier_shift import COURIER_SHIFT_STATUSES, CourierShiftEvent
from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_approve(
    tap, api, dataset, now, uuid, push_events_cache, job,
):
    with tap.plan(17, 'Подтверждение изменений'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        old_started_at = (now() + timedelta(hours=1)).replace(microsecond=0)
        new_started_at = (now() + timedelta(hours=2)).replace(microsecond=0)

        change_event_id = uuid()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=old_started_at,
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': change_event_id,
                    'type': 'change',
                    'detail': {
                        'old': {
                            'started_at': old_started_at,
                        },
                        'new': {
                            'started_at': new_started_at,
                        },
                    },
                }),
            ]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_approve',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(204, diag=True)

        await push_events_cache(shift, job_method='job_recheck_beginner')
        tap.eq(await job.take(), None, 'Задание нет')

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не менялся')
            tap.eq(len(shift.shift_events), 2, 'события добавлены')

            tap.eq(shift.started_at, new_started_at, 'изменения применены')

            tap.ok(not shift.event_change(), 'изменений нет')

            with shift.shift_events[0] as event:
                tap.eq(event.type, 'change', 'change')
            with shift.shift_events[1] as event:
                tap.eq(
                    f'{change_event_id}:accepted',
                    event.shift_event_id,
                    'id события'
                )
                tap.eq(event.type, 'accepted', 'accepted')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_approve',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)
        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, 'waiting', 'статус не менялся')
        tap.eq(len(shift.shift_events), 2, 'события не дублированы')


@pytest.mark.parametrize(
    'status',
    [x for x in COURIER_SHIFT_STATUSES if x not in {'waiting', 'processing'}]
)
async def test_status(tap, api, dataset, now, status):
    with tap.plan(5, 'Только  доступных статусах'):
        store = await dataset.store()
        courier = await dataset.courier()

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status=status,
            started_at=(now() - timedelta(minutes=1)),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_approve',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.change_request.validator.shift_does_not_exist'
        )

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, status, 'Статус не менялся')


async def test_time_fail(tap, api, dataset, now, uuid):
    with tap.plan(
            5,
            'Курьер не может апрувнуть изменения на больше чем может выполнить'
    ):
        cluster = await dataset.cluster(
            courier_shift_setup={
                # Проверяем что смены не вылезут за 2 часа в день
                'max_day_hours': 2,
                'max_week_hours': 24 * 7,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Смена на 1 час которая уже есть
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        # Смена была на 1 час, а теперь хотим сделать на 2 часа
        # Суммарно shift1 + shift2 станет 3 часа - что запрещено настройками
        old_started_at = day.replace(hour=15)
        new_started_at = day.replace(hour=14)

        change_event_id = uuid()
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=old_started_at,
            closes_at=day.replace(hour=16),
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': change_event_id,
                    'type': 'change',
                    'detail': {
                        'old': {
                            'started_at': old_started_at,
                        },
                        'new': {
                            'started_at': new_started_at,
                        },
                    },
                }),
            ]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_approve',
            params_path={
                'courier_shift_id': shift2.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не менялся')
            tap.eq(len(shift.shift_events), 1, 'события не добавлены')

            tap.eq(shift.started_at, old_started_at, 'изменения не применены')


async def test_working_interval(tap, api, dataset, now, uuid):
    with tap.plan(2, 'проверка рабочего времени'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'forbidden_before_time': time(12, 0, 0),
                'forbidden_after_time': time(16, 0, 0),
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(pytz.timezone(cluster.tz)) + timedelta(days=2))\
            .replace(hour=0, minute=0, second=0, microsecond=0)

        started_at = day.replace(hour=12)
        closes_at = day.replace(hour=16)

        courier_shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=started_at,
            closes_at=closes_at,
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        courier_shift.shift_events = [
            CourierShiftEvent({
                'shift_event_id': uuid(),
                'type': 'change',
                'detail': {
                    'old': {
                        'started_at': courier_shift.started_at,
                        'closes_at': courier_shift.closes_at,
                    },
                    'new': {
                        'started_at': started_at - timedelta(hours=1),
                        'closes_at': closes_at + timedelta(hours=1),
                    },
                },
            })
        ]
        await courier_shift.save()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_approve',
            params_path={
                'courier_shift_id': courier_shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)


async def test_courier_blocked(tap, api, dataset, now, uuid):
    with tap.plan(7, 'Курьер заблокирован и не может аппрувить'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            blocks=[
                {'source': 'wms', 'reason': 'ill'},
            ],
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        old_started_at = day.replace(hour=15)
        new_started_at = day.replace(hour=14)

        change_event_id = uuid()
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=old_started_at,
            closes_at=day.replace(hour=16),
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': change_event_id,
                    'type': 'change',
                    'detail': {
                        'old': {
                            'started_at': old_started_at,
                        },
                        'new': {
                            'started_at': new_started_at,
                        },
                    },
                }),
            ]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_approve',
            params_path={
                'courier_shift_id': shift2.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.remote_services.'
            'invalid_work_status'
        )
        t.json_is(
            'errors.0.attributes.arguments.work_status',
            'ill',
        )

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не менялся')
            tap.eq(len(shift.shift_events), 1, 'события не добавлены')

            tap.eq(shift.started_at, old_started_at, 'изменения не применены')


async def test_approve_beginner(
    tap, api, dataset, now, uuid, push_events_cache, job,
):
    with tap.plan(8, 'Подтверждение изменений новичком'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])

        old_started_at = (now() + timedelta(hours=1)).replace(microsecond=0)
        new_started_at = (now() + timedelta(hours=2)).replace(microsecond=0)

        change_event_id = uuid()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=old_started_at,
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': change_event_id,
                    'type': 'change',
                    'detail': {
                        'old': {
                            'started_at': old_started_at,
                        },
                        'new': {
                            'started_at': new_started_at,
                        },
                    },
                }),
            ]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_approve',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(204, diag=True)

        await push_events_cache(shift, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не менялся')
            tap.eq(len(shift.shift_events), 2, 'события добавлены')

            tap.eq(shift.started_at, new_started_at, 'изменения применены')

            tap.ok(not shift.event_change(), 'изменений нет')
            tap.eq(shift.tags, [TAG_BEGINNER], 'тег назначен')

