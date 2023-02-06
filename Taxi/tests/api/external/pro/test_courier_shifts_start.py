# pylint: disable=unused-variable,unused-argument
from datetime import timedelta

import pytest

from stall.model.courier_shift import COURIER_SHIFT_STATUSES, CourierShiftEvent
from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_start(tap, api, dataset, now, uuid, ext_api):
    with tap.plan(20, 'Начало смены'):

        # Отрицательный результат не влияет на обработку запроса
        async def handler(request):
            tap.passed('Еда оповещена')
            return 500, ''

        async with await ext_api('eda_core', handler):
            store = await dataset.store()
            courier = await dataset.courier(
                vars={'external_ids': {'eats': 12345}},
            )

            shift = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='waiting',
                started_at=(now() - timedelta(minutes=1)),
            )

            event_id = uuid()

            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_start',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                    'X-App-Version': '1.2.3',
                },
                json={
                    'id': event_id,
                    'location': {
                        'latitude': 55.0,
                        'longitude': 33.0,
                    },
                }
            )
            t.status_is(204, diag=True)

            with await shift.reload() as shift:
                tap.eq(shift.status, 'processing', 'processing')
                tap.eq(len(shift.shift_events), 2, 'события добавлены')

                with shift.shift_events[0] as event:
                    tap.eq(event.shift_event_id, event_id, 'shift_event_id')
                    tap.eq(event.type, 'started', 'started')
                    tap.eq(event.location.lat, 55.0, 'lat')
                    tap.eq(event.location.lon, 33.0, 'lon')
                    tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')
                with shift.shift_events[1] as event:
                    tap.ok(event.shift_event_id, 'shift_event_id')
                    tap.eq(event.type, 'processing', 'processing')
                    tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')

            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_start',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                    'X-App-Version': '1.2.3',
                },
                json={
                    'id': event_id,
                    'location': {
                        'latitude': 55.0,
                        'longitude': 33.0,
                    },
                }
            )
            t.status_is(204, diag=True)
            tap.ok(await shift.reload(), 'Получили смену')
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 2, 'события не дублированы')


@pytest.mark.parametrize(
    'status',
    [x for x in COURIER_SHIFT_STATUSES if x not in {'waiting', 'processing'}]
)
async def test_waiting(tap, api, dataset, now, uuid, status):
    with tap.plan(5, f'Стартуем только из статуса {status}'):
        store = await dataset.store()
        courier = await dataset.courier()

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status=status,
            started_at=(now() - timedelta(minutes=1)),
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.change_request.validator.shift_does_not_exist'
        )

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, status, 'Статус не менялся')


async def test_before(tap, api, dataset, now, uuid, tzone):
    with tap.plan(7, 'Нельзя начинать смену раньше указанного лага'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_before_time': 600,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        started_at = now(tz=tzone(store.tz)) + timedelta(hours=1)
        real_at    = started_at - timedelta(
            seconds=cluster.courier_shift_setup.started_before_time)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=started_at,
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'start.start_time_early'
        )
        t.json_is(
            'errors.0.attributes.arguments.time',
            real_at.strftime('%H:%M')
        )
        t.json_like('errors.0.attributes.title', real_at.strftime('%H:%M'))

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, 'waiting', 'Статус не менялся')


async def test_after(tap, api, dataset, now, uuid):
    with tap.plan(5, 'Нельзя начинать смену позже указанного лага'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_after_time': 10,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=(now() - timedelta(minutes=1)),
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'start.start_time_late'
        )

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, 'waiting', 'Статус не менялся')


async def test_double(tap, api, dataset, now, uuid):
    with tap.plan(5, 'нельзя открывать две смены параллельно'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=(now() - timedelta(hours=2)),
        )
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=(now() - timedelta(hours=1)),
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift2.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'start.has_active_shift'
        )

        tap.ok(await shift2.reload(), 'Получили смену')
        tap.eq(shift2.status, 'waiting', 'Статус не менялся')


@pytest.mark.parametrize('started_after_time', [900, 0])
async def test_hold_absent(tap, api, dataset, now, uuid, started_after_time):
    with tap.plan(4, 'Запуск смены с hold_absent'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_after_time': started_after_time,  # начинаем заранее
                'timeout_processing': 0,                   # 0 сек
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=now() - timedelta(minutes=10),
            shift_events=[CourierShiftEvent({
                'type': 'hold_absent',
                'detail': {
                    'courier_shift_id': uuid(),
                    'duration': 300,
                    'ends_at': now() + timedelta(minutes=5),
                }
            })]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as s:
            tap.eq(s.status, 'processing', 'Статус не менялся')
            tap.eq([e['type'] for e in s.shift_events],
                   ['hold_absent', 'started', 'processing'],
                   'последовательность событий верная')


async def test_hold_absent_ignored(tap, api, dataset, now, uuid):
    with tap.plan(3, 'Игнорирование смены с истекшим hold_absent'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_after_time': 900,      # начинаем заранее
                'timeout_processing': 0,        # 0 сек
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=now() - timedelta(minutes=30),
            shift_events=[CourierShiftEvent({
                'type': 'hold_absent',
                'detail': {
                    'courier_shift_id': uuid(),
                    'duration': 1200,
                    'ends_at': now() - timedelta(minutes=10),
                }
            })]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)

        with await shift.reload() as s:
            tap.eq(s.status, 'waiting', 'Статус не менялся')


async def test_wrong_location(tap, api, dataset, now, uuid, tzone):
    with tap.plan(4, 'Вне локации слота'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'slot_start_range': 300,
            },
        )
        store = await dataset.store(
            cluster=cluster,
            location={'lat': 60.001892, 'lon': 30.260609}
        )
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=now(tz=tzone(store.tz)) + timedelta(hours=1),
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 61.560511,
                    'longitude': 22.769105,
                },
            }
        )

        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'location.wrong_location'
        )
        t.json_is(
            'errors.0.attributes.arguments.location',
            store.title,
        )


async def test_correct_location(tap, api, dataset, now, uuid, tzone):
    with tap.plan(4, 'В зоне доступности слота'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'slot_start_range': 300,
            },
        )
        store = await dataset.store(
            cluster=cluster,
            location={'lat': 60.001892, 'lon': 30.260609}
        )
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=now(tz=tzone(store.tz)) + timedelta(hours=1),
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 60.001892,
                    'longitude': 30.260609,
                },
            }
        )

        t.status_is(204, diag=True)
        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, 'processing', 'processing')


async def test_blocks(tap, api, dataset, now, uuid, tzone):
    with tap.plan(4, 'Курьер имеет блокировку'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            blocks=[{'source': 'wms', 'reason': 'blocked'}],
        )

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=now(tz=tzone(store.tz)) + timedelta(hours=1),
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 61.560511,
                    'longitude': 22.769105,
                },
            }
        )

        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.remote_services.'
            'invalid_work_status'
        )
        t.json_is(
            'errors.0.attributes.arguments.work_status',
            'blocked',
        )


@pytest.mark.parametrize(
    'setup,duration', [
        ({'beginner_auto_pause_duration': 1800}, 1800),  # 30 мин на паузу
        ({}, 7200),                                      # дефолтные 2 часа
    ]
)
async def test_beginner_auto_pause_on(
    tap, api, dataset, now, uuid, time2time, setup, duration,
):
    with tap.plan(9, 'Новичок стартует смену и попадает на паузу'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_before_time': 600,
                'beginner_auto_pause_duration': 7200,
                **setup,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=now() - timedelta(minutes=1),
            closes_at=now() + timedelta(hours=5),
            tags=[TAG_BEGINNER],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload():
            tap.eq(shift.status, 'processing', 'смена началась')
            tap.eq(
                [e.type for e in shift.shift_events],
                ['started', 'processing', 'paused'],
                'смена начата и поставлена на паузу',
            )

            with shift.event_paused() as paused:
                tap.eq(paused.type, 'paused', 'paused')
                tap.eq(paused.courier_id, None, 'не курьер')
                tap.eq(paused.user_id, None, 'не пользователь')
                tap.eq(
                    time2time(paused.detail.get('ends_at')),
                    paused.created + timedelta(seconds=duration),
                    'ends_at'
                )
                tap.eq(paused.detail['duration'], duration, 'duration')


async def test_beginner_auto_pause_off(tap, api, dataset, now, uuid, time2time):
    with tap.plan(4, 'Новичок стартует смену и авто-пауза не работает'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_before_time': 600,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=now() - timedelta(minutes=1),
            closes_at=now() + timedelta(hours=5),
            tags=[TAG_BEGINNER],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_start',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload():
            tap.eq(shift.status, 'processing', 'смена началась')
            tap.eq(
                [e.type for e in shift.shift_events],
                ['started', 'processing'],
                'смена начата, паузы нет, работаем',
            )
