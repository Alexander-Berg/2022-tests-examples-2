# pylint: disable=unused-variable,unused-argument

from datetime import timedelta

import pytest

from stall.model.courier_shift import COURIER_SHIFT_STATUSES, CourierShiftEvent
from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_stop(tap, api, dataset, now, uuid, ext_api):
    with tap.plan(21, 'Конец смены'):

        # Отрицательный результат не влияет на обработку запроса
        async def handler(request):
            tap.passed('Еда оповещена')
            return 500, ''

        async with await ext_api('eda_core', handler):
            store = await dataset.store()
            courier = await dataset.courier(
                vars={'external_ids': {'eats': 12345}},
            )

            event_started_id = uuid()
            shift = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='processing',
                started_at=(now() - timedelta(minutes=1)),
                shift_events=[
                    CourierShiftEvent({
                        'shift_event_id': event_started_id,
                        'type': 'started',
                        'courier_id': courier.courier_id,
                        'location': {
                            'lat': 55.0,
                            'lon': 33.0,
                        },
                    }),
                ]
            )

            event_id = uuid()

            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_stop',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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
                tap.eq(shift.status, 'complete', 'complete')
                tap.eq(len(shift.shift_events), 3, 'события добавлены 2')

                with shift.shift_events[-2] as event:
                    tap.eq(
                        event.shift_event_id,
                        f'{event_started_id}:stopped',
                        'started shift_event_id'
                    )
                    tap.eq(event.type, 'stopped', 'stopped')
                    tap.eq(event.location.lat, 55.0, 'lat')
                    tap.eq(event.location.lon, 33.0, 'lon')
                    tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')
                    tap.eq(event.detail['reason'], 'pro', 'reason')

                with shift.shift_events[-1] as event:
                    tap.ok(event.shift_event_id, 'shift_event_id')
                    tap.eq(event.type, 'complete', 'complete')
                    tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')

            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_stop',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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
            tap.eq(shift.status, 'complete', 'complete')
            tap.eq(len(shift.shift_events), 3, 'события не дублированы')


@pytest.mark.parametrize(
    'status',
    set(COURIER_SHIFT_STATUSES) - {'complete', 'leave', 'processing'}
)
async def test_processing(tap, api, dataset, now, uuid, status):
    with tap.plan(5, 'закрываем только в статусе processing'):
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
            'api_external_pro_courier_shifts_stop',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'stop.invalid_previous_status'
        )

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, status, 'Статус не менялся')


@pytest.mark.parametrize(['placement', 'status'], [
    ('planned', 'leave'),
    ('planned-extra', 'leave'),
    ('replacement', 'leave'),
    ('unplanned', 'complete'),
])
async def test_leave(tap, api, dataset, now, uuid, placement, status):
    with tap.plan(14, 'Курьер закрыл смену не дождавшись конца'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'stopped_leave_before_time': 10,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        event_started_id = uuid()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            placement=placement,
            started_at=(now() - timedelta(hours=1)),
            closes_at=(now() + timedelta(hours=1)),
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': event_started_id,
                    'type': 'started',
                }),
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_stop',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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

        with await shift.reload() as shift:
            tap.eq(shift.status, status, f'status is {status}')
            tap.eq(len(shift.shift_events), 3, '+2 события добавлены')

            with shift.shift_events[1] as event:
                tap.eq(
                    event.shift_event_id,
                    f'{event_started_id}:stopped',
                    'started shift_event_id'
                )
                tap.eq(event.type, 'stopped', 'stopped')
                tap.eq(event.location.lat, 55.0, 'lat')
                tap.eq(event.location.lon, 33.0, 'lon')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')
            with shift.shift_events[2] as event:
                tap.ok(event.shift_event_id, 'shift_event_id')
                tap.eq(event.type, status, f'event status is {status}')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')


async def test_order(tap, api, dataset, now, uuid):
    with tap.plan(3, 'Нельзя закрыть смену пока открыт заказ'):

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=(now() - timedelta(minutes=1)),
            shift_events=[
                CourierShiftEvent({
                    'type': 'started',
                    'courier_id': courier.courier_id,
                    'location': {
                        'lat': 55.0,
                        'lon': 33.0,
                    },
                }),
            ]
        )

        await dataset.order(
            store=store,
            courier_shift=shift,
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_stop',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'stop.has_orders'
        )


async def test_unpause(tap, api, dataset, now, uuid):
    with tap.plan(13, 'Закрытие паузы при завершении смены'):

        store = await dataset.store()
        courier = await dataset.courier(
            vars={'external_ids': {'eats': 12345}},
        )

        event_started_id = uuid()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=(now() - timedelta(minutes=1)),
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': event_started_id,
                    'type': 'started',
                    'courier_id': courier.courier_id,
                    'location': {
                        'lat': 55.0,
                        'lon': 33.0,
                    },
                }),
                CourierShiftEvent({
                    'type': 'paused',
                    'courier_id': courier.courier_id,
                    'location': {
                        'lat': 55.0,
                        'lon': 33.0,
                    },
                }),
            ]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_stop',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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

        with await shift.reload() as shift:
            tap.eq(shift.status, 'complete', 'complete')
            tap.eq(len(shift.shift_events), 5, 'события добавлены 3')

            pause = shift.shift_events[-4]

            with shift.shift_events[-3] as event:
                tap.eq(event.type, 'unpaused', 'unpaused')
                tap.eq(event.location.lat, 55.0, 'lat')
                tap.eq(event.location.lon, 33.0, 'lon')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')
                tap.eq(
                    event.detail['shift_event_id'],
                    pause.shift_event_id,
                    'shift_event_id'
                )
            with shift.shift_events[-2] as event:
                tap.eq(
                    event.shift_event_id,
                    f'{event_started_id}:stopped',
                    'started shift_event_id'
                )
                tap.eq(event.type, 'stopped', 'stopped')
            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'complete', 'complete')


async def test_stop_auto_start_normal(
        tap, api, dataset, now, uuid, ext_api, job, push_events_cache
):
    # pylint: disable=too-many-locals
    with tap.plan(31, 'Авто-старт следующей смены'):
        # Отрицательный результат не влияет на обработку запроса
        async def handler(request):
            tap.passed('Еда оповещена')
            return 500, ''

        async with await ext_api('eda_core', handler):
            cluster = await dataset.cluster(
                courier_shift_setup={
                    'auto_start_disable': False,  # авто-старт не запрещен
                    'auto_start_max_lag': 600,    # "стык в стык" <= 10 минут
                },
            )
            store = await dataset.store(cluster=cluster)
            courier = await dataset.courier(
                cluster=cluster,
                vars={'external_ids': {'eats': 12345}},
            )

            _now = now()
            event_started_id = uuid()
            shift = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='processing',
                started_at=(_now - timedelta(hours=4)),
                closes_at=(_now - timedelta(minutes=1)),
                shift_events=[
                    CourierShiftEvent({
                        'shift_event_id': event_started_id,
                        'type': 'started',
                        'courier_id': courier.courier_id,
                        'location': {
                            'lat': 55.0,
                            'lon': 33.0,
                        },
                    }),
                ]
            )
            shift_next = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='waiting',
                started_at=_now,
                closes_at=(_now + timedelta(hours=5)),
            )

            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_stop',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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

            # смена закрыта
            with await shift.reload():
                tap.eq(shift.status, 'complete', 'complete')
                tap.eq(len(shift.shift_events), 3, '2 события добавлены')

                with shift.shift_events[-2] as event:
                    tap.eq(event.shift_event_id,
                           f'{event_started_id}:stopped',
                           'started shift_event_id')
                    tap.eq(event.type, 'stopped', 'stopped')
                    tap.eq(event.location.lat, 55.0, 'lat')
                    tap.eq(event.location.lon, 33.0, 'lon')
                    tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')

                with shift.shift_events[-1] as event:
                    tap.ok(event.shift_event_id, 'shift_event_id')
                    tap.eq(event.type, 'complete', 'complete')
                    tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')

            # правая смена не изменилась
            with await shift_next.reload():
                tap.eq(shift_next.status, 'waiting', 'waiting')
                tap.eq(len(shift_next.shift_events), 0, 'событий нет')

            await push_events_cache(shift, job_method='job_auto_start')
            tap.ok(await job.call(await job.take()), 'Задание выполнено')

            # права смена стартовала после запуска задачи
            with await shift_next.reload():
                tap.eq(shift_next.status, 'processing', 'processing')
                tap.eq(len(shift_next.shift_events), 2, 'события добавлены 2')

                with shift_next.shift_events[0] as event:
                    tap.eq(event.type, 'started', 'started')
                    tap.eq(event.location, None, 'lat')
                    tap.eq(event.courier_id, None, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')
                    tap.eq(event.detail['prev_shift']['courier_shift_id'],
                           shift.courier_shift_id,
                           'prev_shift_id')

                    _, stopped = shift.get_event_pair('started')
                    tap.ok(
                        event.created > stopped.created,
                        'Смены стартуют друг а другом без пересечений'
                    )

                with shift_next.shift_events[1] as event:
                    tap.eq(event.type, 'processing', 'processing')
                    tap.eq(event.location, None, 'lat')
                    tap.eq(event.courier_id, None, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')


@pytest.mark.parametrize(
    'started_after_time', [
        0,      # опаздывать запрещено!
        900,    # курьер может начать смену на 15 минут позже
    ]
)
async def test_stop_auto_start_with_late(
        tap, api, dataset, now, uuid, ext_api, job, push_events_cache,
        started_after_time
):
    # pylint: disable=too-many-arguments,too-many-locals
    with tap.plan(18,
                  'Авто-старт смены если предыдущая закрыта позже планового '
                  'начала'
                  ):
        # Отрицательный результат не влияет на обработку запроса
        async def handler(request):
            tap.passed('Еда оповещена')
            return 500, ''

        async with await ext_api('eda_core', handler):
            cluster = await dataset.cluster(
                courier_shift_setup={
                    'auto_start_disable': False,  # авто-старт не запрещен
                    'auto_start_max_lag': 600,    # "стык в стык" <= 10 минут
                    'timeout_processing': 1800,   # hold_absent на 30 минут
                    'started_after_time': started_after_time,
                },
            )
            store = await dataset.store(cluster=cluster)
            courier = await dataset.courier(
                cluster=cluster,
                vars={'external_ids': {'eats': 12345}},
            )

            _now = now()
            shift = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='processing',
                started_at=(_now - timedelta(hours=4)),
                closes_at=(_now - timedelta(minutes=15)),  # затянулась
                shift_events=[
                    CourierShiftEvent({
                        'shift_event_id': uuid(),
                        'type': 'started',
                        'courier_id': courier.courier_id,
                        'location': {
                            'lat': 55.0,
                            'lon': 33.0,
                        },
                    }),
                ]
            )
            shift_next = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='waiting',
                started_at=(_now - timedelta(minutes=11)),   # давно пора
                closes_at=(_now + timedelta(hours=5)),
                shift_events=[
                    CourierShiftEvent({
                        'type': 'hold_absent',
                        'detail': {
                            'courier_shift_id': shift.courier_shift_id,
                            'duration': 26 * 60,
                            'ends_at': _now + timedelta(minutes=26),
                        },
                    }),
                ]
            )

            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_stop',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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

            # смена закрыта
            with await shift.reload():
                tap.eq(shift.status, 'complete', 'complete')
                tap.eq(len(shift.shift_events), 3, '2 события добавлены')

            await push_events_cache(shift, job_method='job_auto_start')
            tap.ok(await job.call(await job.take()), 'Задание выполнено')

            # права смена стартовала после запуска задачи
            with await shift_next.reload():
                tap.eq(shift_next.status, 'processing', 'processing')
                tap.eq(len(shift_next.shift_events), 3, 'события добавлены 2')

                with shift_next.shift_events[-2] as event:
                    tap.eq(event.type, 'started', 'started')
                    tap.eq(event.location, None, 'lat')
                    tap.eq(event.courier_id, None, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')

                    _, stopped = shift.get_event_pair('started')
                    tap.ok(
                        event.created > stopped.created,
                        'Смены стартуют друг а другом без пересечений'
                    )

                with shift_next.shift_events[-1] as event:
                    tap.eq(event.type, 'processing', 'processing')
                    tap.eq(event.location, None, 'lat')
                    tap.eq(event.courier_id, None, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')


@pytest.mark.parametrize(
    'started_before_time', [
        0,      # начинать слишком рано запрещено!
        900,    # курьер может начать смену на 15 минут раньше
    ]
)
async def test_stop_auto_start_too_early(
        tap, api, dataset, now, uuid, ext_api, job, push_events_cache,
        started_before_time
):
    # pylint: disable=too-many-arguments,too-many-locals
    with tap.plan(18,
                  'Авто-старт смены если предыдущая закрыта раньше планового '
                  'начала'
                  ):
        # Отрицательный результат не влияет на обработку запроса
        async def handler(request):
            tap.passed('Еда оповещена')
            return 500, ''

        async with await ext_api('eda_core', handler):
            cluster = await dataset.cluster(
                courier_shift_setup={
                    'auto_start_disable': False,  # авто-старт не запрещен
                    'auto_start_max_lag': 600,    # "стык в стык" <= 10 минут
                    'timeout_processing': 1800,   # hold_absent на 30 минут
                    'started_before_time': started_before_time,
                },
            )
            store = await dataset.store(cluster=cluster)
            courier = await dataset.courier(
                cluster=cluster,
                vars={'external_ids': {'eats': 12345}},
            )

            _now = now()
            shift = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='processing',
                started_at=(_now - timedelta(hours=4)),
                closes_at=(_now + timedelta(minutes=5)),  # закрывает раньше
                shift_events=[
                    CourierShiftEvent({
                        'shift_event_id': uuid(),
                        'type': 'started',
                        'courier_id': courier.courier_id,
                        'location': {
                            'lat': 55.0,
                            'lon': 33.0,
                        },
                    }),
                ]
            )
            shift_next = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='waiting',
                started_at=(_now + timedelta(minutes=8)),   # запуск раньше
                closes_at=(_now + timedelta(hours=15)),
                shift_events=[
                    CourierShiftEvent({
                        'type': 'hold_absent',
                        'detail': {
                            'courier_shift_id': shift.courier_shift_id,
                            'duration': 26 * 60,
                            'ends_at': _now + timedelta(minutes=26),
                        },
                    }),
                ]
            )

            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_stop',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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

            # смена закрыта
            with await shift.reload():
                tap.eq(shift.status, 'complete', 'complete')
                tap.eq(len(shift.shift_events), 3, '2 события добавлены')

            await push_events_cache(shift, job_method='job_auto_start')
            tap.ok(await job.call(await job.take()), 'Задание выполнено')

            # права смена стартовала после запуска задачи
            with await shift_next.reload():
                tap.eq(shift_next.status, 'processing', 'processing')
                tap.eq(len(shift_next.shift_events), 3, 'события добавлены 2')

                with shift_next.shift_events[-2] as event:
                    tap.eq(event.type, 'started', 'started')
                    tap.eq(event.location, None, 'lat')
                    tap.eq(event.courier_id, None, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')

                    _, stopped = shift.get_event_pair('started')
                    tap.ok(
                        event.created > stopped.created,
                        'Смены стартуют друг а другом без пересечений'
                    )

                with shift_next.shift_events[-1] as event:
                    tap.eq(event.type, 'processing', 'processing')
                    tap.eq(event.location, None, 'lat')
                    tap.eq(event.courier_id, None, 'courier_id')
                    tap.eq(event.user_id, None, 'user_id')


async def test_stop_auto_start_ignored(
        tap, api, dataset, now, uuid, ext_api, job, push_events_cache
):
    # pylint: disable=too-many-locals
    with tap.plan(8, 'Нет авто-старта, т.к. смена закрыта слишком рано'):
        # Отрицательный результат не влияет на обработку запроса
        async def handler(request):
            tap.passed('Еда оповещена')
            return 500, ''

        async with await ext_api('eda_core', handler):
            cluster = await dataset.cluster(
                courier_shift_setup={
                    'auto_start_disable': False,  # авто-старт не запрещен
                    'auto_start_max_lag': 600,    # "стык в стык" <= 10 минут
                },
            )
            store = await dataset.store(cluster=cluster)
            courier = await dataset.courier(
                cluster=cluster,
                vars={'external_ids': {'eats': 12345}},
            )

            event_started_id = uuid()
            _now = now()
            shift = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='processing',
                started_at=(_now - timedelta(hours=4)),
                closes_at=(_now + timedelta(hours=4)),
                shift_events=[
                    CourierShiftEvent({
                        'shift_event_id': event_started_id,
                        'type': 'started',
                        'courier_id': courier.courier_id,
                        'location': {
                            'lat': 55.0,
                            'lon': 33.0,
                        },
                    }),
                ]
            )
            shift_next = await dataset.courier_shift(
                store=store,
                courier=courier,
                status='waiting',
                started_at=(_now + timedelta(hours=4, minutes=5)),
                closes_at=(_now + timedelta(hours=6)),
            )

            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_stop',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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

            # смена закрыта
            with await shift.reload():
                tap.eq(shift.status, 'complete', 'complete')
                tap.eq(len(shift.shift_events), 3, '2 события добавлены')

            await push_events_cache(shift, job_method='job_auto_start')
            tap.ok(not await job.take(), 'Задания на авто-старт нет')

            # правая смена не изменилась
            with await shift_next.reload():
                tap.eq(shift_next.status, 'waiting', 'waiting')
                tap.eq(len(shift_next.shift_events), 0, 'событий нет')


async def test_beginner_leave(
    tap, api, dataset, now, uuid, push_events_cache, job,
):
    with tap.plan(8, 'Новичок закрыл смену не дождавшись конца'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'stopped_leave_before_time': 0,
            },
        )
        courier = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])

        _now = now()
        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier,
            status='processing',
            started_at=_now - timedelta(hours=1),
            closes_at=_now + timedelta(hours=1),
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': uuid(),
                    'type': 'started',
                }),
            ],
            tags=[TAG_BEGINNER],
        )
        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
        )
        shift_3 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=3),
            closes_at=_now + timedelta(hours=5),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_stop',
            params_path={
                'courier_shift_id': shift_1.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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

        # смена закрыта раньше положенного
        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'leave', 'ушел рано')
            tap.eq(shift.tags, [TAG_BEGINNER], 'тег остается')

        await push_events_cache(shift_1, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # назначение нового новичка
        with await shift_2.reload() as shift:
            tap.eq(shift.tags, [TAG_BEGINNER], 'назначена новая смена-новичок')

        with await shift_3.reload() as shift:
            tap.eq(shift.tags, [], 'этой ничего не достается')

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER], 'курьер все еще новичок')


async def test_beginner_complete(
    tap, api, dataset, now, uuid, push_events_cache, job,
):
    with tap.plan(7, 'Новичок остается новичком еще 24 часа'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'stopped_leave_before_time': 10,
            },
        )
        tag = await dataset.courier_shift_tag()
        courier = await dataset.courier(cluster=cluster,
                                        tags=[TAG_BEGINNER, tag.title])

        _now = now()
        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier,
            status='processing',
            started_at=_now - timedelta(hours=1),
            closes_at=_now - timedelta(minutes=1),      # на минуту позже
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': uuid(),
                    'type': 'started',
                }),
            ],
            tags=[TAG_BEGINNER, tag.title],
        )
        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            tags=[tag.title],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_stop',
            params_path={
                'courier_shift_id': shift_1.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
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

        # смена закрыта успешно
        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'complete', 'ушел рано')
            tap.eq(shift.tags, [TAG_BEGINNER, tag.title], 'тег остается')

        await push_events_cache(shift_1, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # назначение нового новичка
        with await shift_2.reload() as shift:
            tap.eq(shift.tags, [tag.title], 'тег не выдан, остался старый')

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER, tag.title], 'тег остается')
