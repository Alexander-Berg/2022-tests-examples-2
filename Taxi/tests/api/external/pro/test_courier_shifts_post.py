# pylint: disable=too-many-locals,too-many-lines

from datetime import datetime, timedelta, time

import pytest
import pytz
from dateutil.relativedelta import relativedelta

from libstall.util import tzone
from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_post(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(14, 'Назначение нескольких смен'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        shift1 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
            schedule=[
                {'tags': ['best'],  'time': now() - timedelta(hours=1)},
                {'tags': [],        'time': now() + timedelta(hours=1)},
            ],
        )
        shift2 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=18),
            closes_at=day.replace(hour=19),
            schedule=[
                {'tags': [],        'time': now() - timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift1.group_id,
                        'startsAt': time2iso_utc(shift1.started_at),
                        'endsAt': time2iso_utc(shift1.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift2.group_id,
                        'startsAt': time2iso_utc(shift2.started_at),
                        'endsAt': time2iso_utc(shift2.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')
            tap.eq(shift.courier_tags, courier.tags, 'совпали')
            tap.eq(shift.tags, [], 'на свои теги не влияет')

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')
            tap.eq(shift.courier_tags, ['best'], 'совпали')
            tap.eq(shift.tags, [], 'на свои теги не влияет')


@pytest.mark.parametrize('settings', [
    {'week_from_sunday': True},
    {'week_from_sunday': False},
    {'week_from_sunday': None},
    {},
])
async def test_post_neighboring_weeks(
        tap, api, dataset, uuid, now, time2iso_utc, settings,
):
    with tap.plan(6, 'Назначение нескольких смен с разных недель'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 8,
                'max_week_hours': 8,
                **settings,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
        )

        # На 2 недели вперед, чтобы гарантировать отсутствие флапа
        week_from_sunday = bool(settings.get('week_from_sunday'))
        _day = (now() + timedelta(days=15)).replace(hour=0, minute=0, second=0)
        _week_start = _day - timedelta(days=_day.weekday() + week_from_sunday)

        # конец ПРЕДЫДУЩЕЙ недели, 8-часовая смена
        shift_1 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=_week_start - timedelta(hours=10),
            closes_at=_week_start - timedelta(hours=2),
            schedule=[
                {'tags': ['best'],  'time': now() - timedelta(hours=1)},
                {'tags': [],        'time': now() + timedelta(hours=1)},
            ],
        )

        # начало ТЕКУЩЕЙ недели, 8-часовая смена
        shift_2 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=_week_start + timedelta(hours=10),
            closes_at=_week_start + timedelta(hours=18),
            schedule=[
                {'tags': [],        'time': now() - timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift_1.group_id,
                        'startsAt': time2iso_utc(shift_1.started_at),
                        'endsAt': time2iso_utc(shift_1.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift_2.group_id,
                        'startsAt': time2iso_utc(shift_2.started_at),
                        'endsAt': time2iso_utc(shift_2.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена№1 waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'смена№1 courier_id')

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена№2 waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'смена№2 courier_id')


async def test_tags_empty(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(7, 'Курьер без тегов'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[],
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        shift1 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
            schedule=[
                {'tags': ['best'],  'time': now() - timedelta(hours=2)},
            ],
        )
        shift2 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=18),
            closes_at=day.replace(hour=19),
            schedule=[
                {'tags': [],        'time': now() - timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift1.group_id,
                        'startsAt': time2iso_utc(shift1.started_at),
                        'endsAt': time2iso_utc(shift1.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift2.group_id,
                        'startsAt': time2iso_utc(shift2.started_at),
                        'endsAt': time2iso_utc(shift2.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'request', 'не взял т.к. не для всех')

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')


async def test_shift_tags(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(14, 'Проверка применения тегов смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=['best', 'test1'],
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        shift1 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=['test1'],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
            schedule=[
                {'tags': ['best'], 'time': now() - timedelta(hours=1)},
            ],
        )

        # Сработает первое расписание
        shift2 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=14),
            closes_at=day.replace(hour=15),
            schedule=[
                {'tags': ['best', 'test2'], 'time': now() - timedelta(hours=1)},
                {'tags': ['test2'],         'time': now() - timedelta(hours=1)},
            ],
        )

        # Один из тегов совпал
        shift3 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=['test1', 'test2'],
            started_at=day.replace(hour=16),
            closes_at=day.replace(hour=17),
            schedule=[
                {'tags': [],                'time': now() - timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift1.group_id,
                        'startsAt': time2iso_utc(shift1.started_at),
                        'endsAt': time2iso_utc(shift1.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift2.group_id,
                        'startsAt': time2iso_utc(shift2.started_at),
                        'endsAt': time2iso_utc(shift2.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift3.group_id,
                        'startsAt': time2iso_utc(shift3.started_at),
                        'endsAt': time2iso_utc(shift3.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift1.reload() as shift:
            tap.note('shift1')
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')

        with await shift2.reload() as shift:
            tap.note('shift2')
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')

        with await shift3.reload() as shift:
            tap.note('shift3')
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')


async def test_gone(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(8, 'Смена уже взята другими курьером'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=['test1'],
            delivery_type='foot',
        )
        courier2 = await dataset.courier(
            cluster=cluster,
            tags=['test1'],
            delivery_type='foot',
        )

        shift = await dataset.courier_shift(
            status='processing',
            delivery_type='foot',
            store=store,
            courier=courier2,
            tags=['test1', 'test2'],
            started_at=now(),
            closes_at=now() + timedelta(hours=1),
            schedule=[
                {'tags': ['test1'], 'time': now() - timedelta(hours=1)},
                {'tags': ['test2'], 'time': now() + timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.id', shift.group_id)
        t.json_is('errors.0.type', 'error')
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.save.error.no_shifts_left'
        )
        t.json_is('meta.count', 1)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(
                shift.courier_id,
                courier2.courier_id,
                'courier_id не менялся'
            )


async def test_changed(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(8, 'Смена изменилась'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=now(),
            closes_at=now() + timedelta(hours=1),
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(now() + timedelta(minutes=1)),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.id', shift.group_id)
        t.json_is('errors.0.type', 'error')
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.save.error.no_shifts_left'
        )
        t.json_is('meta.count', 1)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'не назначена')


async def test_exceed_day(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(12, 'Нельзя брать больше чем разрешено в сутки'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 2,
                'max_week_hours': 24 * 7,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        shift1 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift2 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=15),
            closes_at=day.replace(hour=18),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift3 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=22),
            closes_at=day.replace(hour=23),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift1.group_id,
                        'startsAt': time2iso_utc(shift1.started_at),
                        'endsAt': time2iso_utc(shift1.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift2.group_id,
                        'startsAt': time2iso_utc(shift2.started_at),
                        'endsAt': time2iso_utc(shift2.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift3.group_id,
                        'startsAt': time2iso_utc(shift3.started_at),
                        'endsAt': time2iso_utc(shift3.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.type', 'error')
        t.json_is('errors.0.id', shift2.group_id)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.save.error.exceeding_duration'
        )
        t.json_is('meta.count', 1)

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'назначена')
        with await shift2.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'не назначена')
        with await shift3.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'назначена')


@pytest.mark.parametrize(
    'status', ('released', 'cancelled')
)
async def test_exceed_day_no_cancel(
        tap, api, dataset, uuid, now, time2iso_utc, status
):
    with tap.plan(4, 'Отмены не влияют на расчет времени'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 2,
                'max_week_hours': 24 * 7,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        shift1 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=14),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        await dataset.courier_shift(
            status=status,
            store=store,
            courier=courier,
            started_at=day.replace(hour=15),
            closes_at=day.replace(hour=18),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift1.group_id,
                        'startsAt': time2iso_utc(shift1.started_at),
                        'endsAt': time2iso_utc(shift1.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'назначена')


async def test_exceed_day_real(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(4, 'Учитываем фактическое время когда смена выполнена'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 3,
                'max_week_hours': 24 * 7,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Смена на 5 часов, но по факту отработан час
        await dataset.courier_shift(
            status='leave',
            store=store,
            courier=courier,
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=17),
            shift_events=[
                {
                    'type': 'started',
                    'created': day.replace(hour=12)
                },
                {
                    'type': 'stopped',
                    'created': day.replace(hour=13)
                },
            ],
        )

        # Смена на час которую можно взять
        shift = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=18),
            closes_at=day.replace(hour=19),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена взята')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')


async def test_exceed_day_in_week(tap, api, dataset, uuid, now, time2iso_utc):
    # pylint: disable=too-many-locals

    with tap.plan(8, 'Сутки не влияют друг на друга'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 2,
                'max_week_hours': 24 * 7,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        _now = now(tz=tzone(cluster.tz))
        week_start = (_now + timedelta(days=7 - _now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Второе число на той же неделе что и первое
        day1 = week_start + timedelta(days=1)
        day2 = week_start + timedelta(days=2)
        day3 = week_start + timedelta(days=3)

        shift1 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day1.replace(hour=12),
            closes_at=day1.replace(hour=14),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift2 = await dataset.courier_shift(
            status='waiting',
            courier=courier,
            store=store,
            started_at=day2.replace(hour=18),
            closes_at=day2.replace(hour=20),
        )

        shift3 = await dataset.courier_shift(
            status='waiting',
            courier=courier,
            store=store,
            started_at=day3.replace(hour=18),
            closes_at=day3.replace(hour=20, minute=2),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift1.group_id,
                        'startsAt': time2iso_utc(shift1.started_at),
                        'endsAt': time2iso_utc(shift1.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'назначена')
        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'назначена')
        with await shift3.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'назначена')


async def test_exceed_week(tap, api, dataset, uuid, now, time2iso_utc):
    # pylint: disable=too-many-locals

    with tap.plan(12, 'Нельзя брать больше чем разрешено в неделю'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 24,
                'max_week_hours': 2,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day1 = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Второе число на той же неделе что и первое
        weekday2 = 0 if day1.weekday() >= 6 else 6
        week_start = day1 - timedelta(days=day1.weekday())
        day2 = week_start + timedelta(days=weekday2)

        shift1 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day1.replace(hour=12),
            closes_at=day1.replace(hour=13),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift2 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day2.replace(hour=15),
            closes_at=day2.replace(hour=18),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift3 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day2.replace(hour=22),
            closes_at=day2.replace(hour=23),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift1.group_id,
                        'startsAt': time2iso_utc(shift1.started_at),
                        'endsAt': time2iso_utc(shift1.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift2.group_id,
                        'startsAt': time2iso_utc(shift2.started_at),
                        'endsAt': time2iso_utc(shift2.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift3.group_id,
                        'startsAt': time2iso_utc(shift3.started_at),
                        'endsAt': time2iso_utc(shift3.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.type', 'error')
        t.json_is('errors.0.id', shift2.group_id)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.save.error.exceeding_duration'
        )
        t.json_is('meta.count', 1)

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'назначена')
        with await shift2.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'не назначена')
        with await shift3.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'назначена')


async def test_exceed_week_real(tap, api, dataset, uuid, now, time2iso_utc):
    # pylint: disable=too-many-locals

    with tap.plan(4, 'Учитываем фактическое время когда смена выполнена'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 24,
                'max_week_hours': 3,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day1 = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Второе число на той же неделе что и первое
        weekday2 = 0 if day1.weekday() >= 6 else 6
        week_start = day1 - timedelta(days=day1.weekday())
        day2 = week_start + timedelta(days=weekday2)

        await dataset.courier_shift(
            status='complete',
            store=store,
            courier=courier,
            started_at=day1.replace(hour=12),
            closes_at=day1.replace(hour=17),
            shift_events=[
                {
                    'type': 'started',
                    'created': day1.replace(hour=12)
                },
                {
                    'type': 'stopped',
                    'created': day1.replace(hour=13)
                },
            ],
        )

        shift = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day2.replace(hour=18),
            closes_at=day2.replace(hour=19),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена взята')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')


@pytest.mark.parametrize('settings', [
    {'week_from_sunday': True},
    {'week_from_sunday': False},
    {'week_from_sunday': None},
    {},
])
async def test_neighboring_weeks(
        tap, api, dataset, uuid, now, time2iso_utc, settings,
):
    with tap.plan(4, 'Смены с соседних недель не цепляются за max_week_hours'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 8,
                'max_week_hours': 8,
                **settings,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # На 2 недели вперед, чтобы гарантировать отсутствие флапа
        week_from_sunday = bool(settings.get('week_from_sunday'))
        _day = (now() + timedelta(days=15)).replace(hour=0, minute=0, second=0)
        _week_start = _day - timedelta(days=_day.weekday() + week_from_sunday)

        # конец ПРЕДЫДУЩЕЙ недели, 8-часовая смена текущего курьера
        await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
            started_at=_week_start - timedelta(hours=10),
            closes_at=_week_start - timedelta(hours=2),
        )

        # начало ТЕКУЩЕЙ недели, 4-часовая смена
        await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
            started_at=_week_start + timedelta(hours=10),
            closes_at=_week_start + timedelta(hours=14),
        )

        # начало СЛЕДУЮЩЕЙ недели, 8-часовая смена
        await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
            started_at=_week_start + timedelta(days=7, hours=10),
            closes_at=_week_start + timedelta(days=7, hours=14),
        )

        # захватываем
        shift = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=_week_start + timedelta(hours=14),
            closes_at=_week_start + timedelta(hours=18),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена взята')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')


@pytest.mark.parametrize('times', [
    {
        # спереди
        'start_at': datetime(2020, 1, 1, 9, 0, 0),
        'closes_at': datetime(2020, 1, 1, 11, 0, 0),
    },
    {   # сзади
        'start_at': datetime(2020, 1, 1, 19, 0, 0),
        'closes_at': datetime(2020, 1, 1, 22, 0, 0),
    },
])
async def test_no_overlap(tap, api, dataset, uuid, now, times, time2iso_utc):
    with tap.plan(6, 'Можно брать не пересекающиеся смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
            tags=[],
            started_at=times['start_at'],
            closes_at=times['closes_at'],
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift = await dataset.courier_shift(
            status='request',
            store=store,
            tags=[],
            started_at=datetime(2020, 1, 1, 12, 0, 0),
            closes_at=datetime(2020, 1, 1, 18, 0, 0),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')


@pytest.mark.parametrize('times', [
    {
        # спереди
        'start_at': datetime(2020, 1, 1, 9, 0, 0),
        'closes_at': datetime(2020, 1, 1, 12, 0, 0),
    },
    {   # сзади
        'start_at': datetime(2020, 1, 1, 18, 0, 0),
        'closes_at': datetime(2020, 1, 1, 22, 0, 0),
    },
])
async def test_follow(tap, api, dataset, uuid, now, times, time2iso_utc):
    with tap.plan(6, 'Можно брать смены в стык'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
            tags=[],
            started_at=times['start_at'],
            closes_at=times['closes_at'],
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift = await dataset.courier_shift(
            status='request',
            store=store,
            tags=[],
            started_at=datetime(2020, 1, 1, 12, 0, 0),
            closes_at=datetime(2020, 1, 1, 18, 0, 0),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')


async def test_follow_many(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(14, 'Можно брать смены в стык сразу несколько'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift1 = await dataset.courier_shift(
            status='request',
            store=store,
            tags=[],
            started_at=datetime(2020, 1, 1, 9, 0, 0),
            closes_at=datetime(2020, 1, 1, 12, 0, 0),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift2 = await dataset.courier_shift(
            status='request',
            store=store,
            tags=[],
            started_at=datetime(2020, 1, 1, 12, 0, 0),
            closes_at=datetime(2020, 1, 1, 18, 0, 0),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift3 = await dataset.courier_shift(
            status='request',
            store=store,
            tags=[],
            started_at=datetime(2020, 1, 1, 18, 0, 0),
            closes_at=datetime(2020, 1, 1, 22, 0, 0),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift1.group_id,
                        'startsAt': time2iso_utc(shift1.started_at),
                        'endsAt': time2iso_utc(shift1.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift2.group_id,
                        'startsAt': time2iso_utc(shift2.started_at),
                        'endsAt': time2iso_utc(shift2.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift3.group_id,
                        'startsAt': time2iso_utc(shift3.started_at),
                        'endsAt': time2iso_utc(shift3.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')

        with await shift3.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')


@pytest.mark.parametrize('assigned,requested', [
    # Внутри одно дня
    (
        {  # default (1 января)
            'started_at': datetime(2020, 1, 1, 12, 0, 0),
            'closes_at': datetime(2020, 1, 1, 18, 0, 0),
        },
        {  # спереди
            'started_at': datetime(2020, 1, 1, 11, 0, 0),
            'closes_at': datetime(2020, 1, 1, 13, 0, 0),
        },
    ),
    (
        {  # default (1 января)
            'started_at': datetime(2020, 1, 1, 12, 0, 0),
            'closes_at': datetime(2020, 1, 1, 18, 0, 0),
        },
        {   # внутри
            'started_at': datetime(2020, 1, 1, 13, 0, 0),
            'closes_at': datetime(2020, 1, 1, 14, 0, 0),
        },
    ),
    (
        {  # default (1 января)
            'started_at': datetime(2020, 1, 1, 12, 0, 0),
            'closes_at': datetime(2020, 1, 1, 18, 0, 0),
        },
        {  # сзади
            'started_at': datetime(2020, 1, 1, 15, 0, 0),
            'closes_at': datetime(2020, 1, 1, 20, 0, 0),
        },
    ),
    (
        {  # default (1 января)
            'started_at': datetime(2020, 1, 1, 12, 0, 0),
            'closes_at': datetime(2020, 1, 1, 18, 0, 0),
        },
        {  # снаружи
            'started_at': datetime(2020, 1, 1, 11, 0, 0),
            'closes_at': datetime(2020, 1, 1, 20, 0, 0),
        },
    ),

    # Между соседними днями/неделями
    (
        {  # default (1 января)
            'started_at': datetime(2020, 1, 1, 12, 0, 0),
            'closes_at': datetime(2020, 1, 1, 18, 0, 0),
        },
        {  # из прошлого дня
            'started_at': datetime(2019, 12, 31, 23, 0, 0),
            'closes_at': datetime(2020, 1, 1, 13, 0, 0),
        },
    ),
    (
        {  # смена слишком затянулась и цепляем смену из следующего дня
            'started_at': datetime(2019, 12, 31, 23, 0, 0),
            'closes_at': datetime(2020, 1, 1, 13, 0, 0),
        },
        {  # из следующего дня
            'started_at': datetime(2020, 1, 1, 12, 0, 0),
            'closes_at': datetime(2020, 1, 1, 18, 0, 0),
        }
    ),
    (
        {  # понедельник
            'started_at': datetime(2022, 1, 17, 12, 0, 0),
            'closes_at': datetime(2022, 1, 17, 18, 0, 0),
        },
        {  # воскресенье (с предыдущей недели)
            'started_at': datetime(2022, 1, 16, 23, 0, 0),
            'closes_at': datetime(2022, 1, 17, 13, 0, 0),
        },
    ),
    (
        {  # воскресенье
            'started_at': datetime(2022, 1, 16, 23, 0, 0),
            'closes_at': datetime(2022, 1, 17, 13, 0, 0),
        },
        {  # понедельник (со следующей недели)
            'started_at': datetime(2022, 1, 17, 12, 0, 0),
            'closes_at': datetime(2022, 1, 17, 18, 0, 0),
        },
    ),
])
async def test_overlap(
        tap, api, dataset, uuid, now, time2iso_utc, assigned, requested
):
    with tap.plan(6, 'Нельзя брать пересекающиеся смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
            tags=[],
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
            **assigned
        )

        shift = await dataset.courier_shift(
            status='request',
            store=store,
            tags=[],
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
            **requested
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.id', shift.group_id)
        t.json_is('errors.0.type', 'error')
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.'
            'save.error.intersection'
        )

        with await shift.reload() as shift:
            tap.eq(shift.status, 'request', 'не взята')


async def test_overlap_fact(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(4, 'Можно брать если фактическое время не пересекается'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Смена с которой ушли
        await dataset.courier_shift(
            status='leave',
            store=store,
            courier=courier,
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=16),
            shift_events=[
                {
                    'type': 'started',
                    'created': day.replace(hour=12)
                },
                {
                    'type': 'stopped',
                    'created': day.replace(hour=13)
                },
            ],
        )

        # Смена явно пересекающаяся с предыдущей, но не пересекающая фактическое
        shift = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=15),
            closes_at=day.replace(hour=18),
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],

        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена взята')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')


async def test_overlap_requested(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(7, 'Нельзя брать пересекающиеся смены в одном запросе'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster, tz='Europe/Moscow')
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        shift_1 = await dataset.courier_shift(
            status='request',
            store=store,
            tz='Europe/Moscow',
            tags=[],
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
            started_at=day + timedelta(hours=15),
            closes_at=day + timedelta(hours=20, minutes=45),
        )

        shift_2 = await dataset.courier_shift(
            status='request',
            store=store,
            tz='Europe/Moscow',
            tags=[],
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
            started_at=day + timedelta(hours=16),
            closes_at=day + timedelta(hours=20, minutes=45),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift_1.group_id,
                        'startsAt': time2iso_utc(shift_1.started_at),
                        'endsAt': time2iso_utc(shift_1.closes_at),
                        'startPointId': store.store_id,
                    },
                    {
                        'id': shift_2.group_id,
                        'startsAt': time2iso_utc(shift_2.started_at),
                        'endsAt': time2iso_utc(shift_2.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.id', shift_2.group_id)
        t.json_is('errors.0.type', 'error')
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.'
            'save.error.intersection'
        )

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'взята первая')

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'request', 'вторая не взята')


@pytest.mark.parametrize('times', [
    {   # спереди
        'start_at': datetime(2020, 1, 1, 9, 0, 0),
        'closes_at': datetime(2020, 1, 1, 11, 0, 0),
    },
    {   # сзади
        'start_at': datetime(2020, 1, 1, 19, 0, 0),
        'closes_at': datetime(2020, 1, 1, 23, 0, 0),
    },
])
async def test_between(tap, api, dataset, uuid, now, times, time2iso_utc):
    with tap.plan(10, 'При переходе между лавками есть задержка на путь'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'duration_between_stores': 2 * 60 * 60,
            },
        )
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        await dataset.courier_shift(
            status='waiting',
            store=store1,
            courier=courier,
            tags=[],
            started_at=times['start_at'],
            closes_at=times['closes_at'],
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift1 = await dataset.courier_shift(
            status='request',
            store=store1,
            tags=[],
            started_at=datetime(2020, 1, 1, 12, 0, 0),
            closes_at=datetime(2020, 1, 1, 18, 0, 0),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        shift2 = await dataset.courier_shift(
            status='request',
            store=store2,
            tags=[],
            started_at=datetime(2020, 1, 1, 12, 0, 0),
            closes_at=datetime(2020, 1, 1, 18, 0, 0),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift1.group_id,
                        'startsAt': time2iso_utc(shift1.started_at),
                        'endsAt': time2iso_utc(shift1.closes_at),
                        'startPointId': store1.store_id,
                    },
                    {
                        'id': shift2.group_id,
                        'startsAt': time2iso_utc(shift2.started_at),
                        'endsAt': time2iso_utc(shift2.closes_at),
                        'startPointId': store2.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.id', shift2.group_id)
        t.json_is('errors.0.type', 'error')
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.'
            'save.error.intersection'
        )

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'взята т.к. в той же лавке')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')

        with await shift2.reload() as shift:
            tap.eq(
                shift.status,
                'request',
                'не взята т.к. лавки разные, а зазор  на путь <2 часов'
            )


async def test_ignore_between(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(
            6,
            'При переходе между лавками не заданная задержка не учитывается'
    ):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'duration_between_stores': None,
            },
        )
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        await dataset.courier_shift(
            status='waiting',
            store=store1,
            courier=courier,
            started_at=now(),
            closes_at=now() + timedelta(hours=1),
            tags=[],
        )

        shift_2 = await dataset.courier_shift(
            status='request',
            store=store2,
            started_at=now() + timedelta(hours=1, seconds=2),
            closes_at=now() + timedelta(hours=3),
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift_2.group_id,
                        'startsAt': time2iso_utc(shift_2.started_at),
                        'endsAt': time2iso_utc(shift_2.closes_at),
                        'startPointId': store2.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')


async def test_replacement(tap, api, dataset, now, uuid, time2iso_utc):
    # pylint: disable=import-outside-toplevel
    with tap.plan(
            8,
            'Курьер проспал смену, но должен мочь взять перевыставленную из нее'
    ):
        cluster = await dataset.cluster(courier_shift_setup={
            'max_day_hours': 2,
            'max_week_hours': 2,
        })
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            vars={'external_ids': {'eats': 12345}},
        )

        _now = now()

        shift1 = await dataset.courier_shift(
            placement='planned',
            cluster=cluster,
            store=store,
            status='waiting',
            schedule=[
                {'tags': [], 'time': _now - timedelta(hours=1)},
            ],
            started_at=_now - timedelta(minutes=1),
            closes_at=_now + timedelta(hours=1),
            courier_id=courier.courier_id,
        )

        from scripts.cron.close_courier_shifts import close_courier_shifts
        tap.ok(
            await close_courier_shifts(cluster_id=cluster.cluster_id),
            'Скрипт отработал'
        )

        with await shift1.reload():
            tap.eq(shift1.status, 'absent', 'Смена сорвана')

        reissued = await shift1.list_reissued()
        tap.eq(len(reissued), 1, 'Есть перевысталенная смена')

        with reissued[0] as shift2:
            tap.eq(shift2.status, 'request', 'request')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift2.group_id,
                        'startsAt': time2iso_utc(shift2.started_at),
                        'endsAt': time2iso_utc(shift2.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')


async def test_blocks(tap, api, dataset, now, uuid, time2iso_utc):
    with tap.plan(5, 'Курьер имеет блокировку'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            blocks=[{'source': 'wms', 'reason': 'blocked'}],
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        shift = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.id', shift.group_id)
        t.json_is('errors.0.type', 'error')
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.remote_services.'
            'invalid_work_status'
        )


async def test_working_interval(tap, dataset, api, now, uuid, time2iso_utc):
    with tap.plan(7, 'выход за пределы рабочего времени'):
        cluster = await dataset.cluster(
            courier_shift_underage_setup={
                'forbidden_before_time': time(12, 0, 0),
                'forbidden_after_time': time(16, 0, 0),
            }
        )
        store = await dataset.store(cluster=cluster)

        birthday_1 = now() - relativedelta(years=15)
        young_courier = await dataset.courier(
            cluster=cluster, birthday=birthday_1
        )

        birthday_2 = now() - relativedelta(years=21)
        adult_courier = await dataset.courier(
            cluster=cluster, birthday=birthday_2
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(pytz.timezone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        shift = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=11),
            closes_at=day.replace(hour=16),
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
        )

        # несовершеннолетний курьер не может взять по конфигу кластера
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': young_courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': young_courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.id', shift.group_id)
        t.json_is('errors.0.type', 'error')
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.'
            'save.error.out_of_working_interval'
        )

        # а совершеннолетний может
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': adult_courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': adult_courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)


async def test_any_delivery(tap, api, dataset, uuid, now, time2iso_utc):
    with tap.plan(6, 'Взятие смены с чужим типом доставки'):
        day = (now() + timedelta(days=2)).replace(hour=0, minute=0, second=0)

        cluster = await dataset.cluster(courier_shift_setup={
            'delivery_type_check_enable': False,
        })
        courier = await dataset.courier(
            cluster=cluster,
            delivery_type='foot',
            tags=['best'],
        )
        shift = await dataset.courier_shift(
            cluster=cluster,
            status='request',
            delivery_type='foot',
            tags=[],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=17),
            schedule=[
                {'tags': ['best'],  'time': now() - timedelta(hours=1)},
                {'tags': [],        'time': now() + timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift.group_id,
                        'startsAt': time2iso_utc(shift.started_at),
                        'endsAt': time2iso_utc(shift.closes_at),
                        'startPointId': shift.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload():
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')


async def test_tag_beginner(
    tap, api, dataset, uuid, now, time2iso_utc, push_events_cache, job,
):
    with tap.plan(10, 'Новичок берет более раннюю смену и тег переназначается'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[TAG_BEGINNER],
        )

        _now = now().replace(microsecond=0)
        shift_1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=3),
            closes_at=_now + timedelta(hours=5),
            tags=[TAG_BEGINNER],
            schedule=[
                {'tags': [], 'time': now() - timedelta(days=1)},
            ],
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=2),
            tags=[],
            schedule=[
                {'tags': [], 'time': now() - timedelta(days=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_post',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift_2.group_id,
                        'startsAt': time2iso_utc(shift_2.started_at),
                        'endsAt': time2iso_utc(shift_2.closes_at),
                        'startPointId': shift_2.store_id,
                    },
                ],
            }
        )
        t.status_is(204, diag=True)

        await push_events_cache(shift_2, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не поменялся #1')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера на месте #1')
            tap.eq(shift.tags, [], 'смена теперь НЕ новичок')

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена назначена #2')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера назначен #2')
            tap.eq(shift.tags, [TAG_BEGINNER], 'смена теперь Новичок')

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER], 'курьер все еще новичок')
