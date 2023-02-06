# pylint: disable=too-many-locals

from datetime import timedelta

import pytest
from aiohttp import web

from scripts.cron.close_courier_shifts_by_offline import (
    close_courier_shifts_by_offline,
)
from stall.client.driver_trackstory import client as client_dt
from stall.model.courier_shift import CourierShiftEvent


@pytest.mark.parametrize('threshold', (None, 300))
async def test_geo_ok(
        tap, dataset, ext_api, now, threshold,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': threshold,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(cluster=cluster)

    async def handler(_):
        return web.json_response({
            'results': [{
                'driver_id': courier.external_id,
                'position': {
                    'timestamp': now().timestamp(),
                },
            }],
        })

    with tap.plan(3, 'Если у курьера есть координаты, ничего не происходит'):
        async with await ext_api(client_dt, handler):
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')

            await courier.reload()
            tap.eq(courier.vars('last_location_time', None), None, 'Флага нет')


@pytest.mark.parametrize('threshold', (1200,))
async def test_old_geo(
        tap, dataset, ext_api, now, threshold,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': threshold,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(cluster=cluster)
    last_location_time = (
        now() - timedelta(minutes=6)
    ).replace(microsecond=0).timestamp()

    async def handler(_):
        return web.json_response({
            'results': [{
                'driver_id': courier.external_id,
                'position': {
                    'timestamp': last_location_time,
                },
            }],
        })

    with tap.plan(3, 'Если у курьера есть координаты, проставляем флаг'):
        async with await ext_api(client_dt, handler):
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')

            await courier.reload()
            tap.eq(
                courier.vars('last_location_time', None),
                last_location_time,
                'Флаг проставлен',
            )


async def test_no_geo(
        tap, dataset, ext_api, now,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 1200,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
    )

    async def handler(_):
        return web.json_response({
            'results': [],
        })

    with tap.plan(3, 'Если у курьера нет координат'):
        async with await ext_api(client_dt, handler):
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')

            await courier.reload()
            tap.ok(courier.vars('last_location_time', None), 'Флаг проставлен')


async def test_geo_stop(
        tap, dataset, ext_api, now,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 1200,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
        vars={
            'last_location_time': (now() - timedelta(minutes=30)).timestamp(),
        },
    )

    async def handler(_):
        return web.json_response({
            'results': [],
        })

    with tap.plan(5, 'Закрыть смену по флагу'):
        async with await ext_api(client_dt, handler):
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'leave', 'Смена закрыта')

            event = shift.shift_events[-2]
            tap.eq(event.type, 'stopped', 'Курьер покинул смену')
            tap.eq(event.detail.get('reason'), 'no_geo', 'Сохранили причину')

            await courier.reload()
            tap.eq(courier.vars('last_location_time', None), None, 'Флаг снят')


async def test_geo_stop_immediately(
        tap, dataset, ext_api, now, time2time,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 300,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
    )
    last_position = (
        now() - timedelta(minutes=6)
    ).replace(microsecond=0)

    async def handler(_):
        return web.json_response({
            'results': [{
                'driver_id': courier.external_id,
                'position': {
                    'timestamp': last_position.timestamp(),
                },
            }],
        })

    with tap.plan(6, 'Закрыть сразу'):
        async with await ext_api(client_dt, handler):
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'leave', 'Смена закрыта')

            event = shift.shift_events[-2]
            tap.eq(event.type, 'stopped', 'Курьер покинул смену')
            tap.eq(event.detail.get('reason'), 'no_geo', 'Сохранили причину')
            tap.eq(
                time2time(event.detail.get('last_location_time')),
                last_position,
                'Сохранили параметры закрытия',
            )

            await courier.reload()
            tap.eq(courier.vars('last_location_time', None), None, 'Флаг снят')


async def test_geo_cancel(
        tap, dataset, ext_api, now,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 5000,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
        vars={
            'last_location_time': (now() - timedelta(minutes=30)).timestamp(),
        },
    )

    async def handler(_):
        return web.json_response({
            'results': [{
                'driver_id': courier.external_id,
                'position': {
                    'timestamp': (now() - timedelta(minutes=2)).timestamp(),
                },
            }],
        })

    with tap.plan(3, 'Снять флаг'):
        async with await ext_api(client_dt, handler):
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')

            await courier.reload()
            tap.eq(courier.vars('last_location_time', None), None, 'Флаг снят')


async def test_geo_update(
        tap, dataset, ext_api, now,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 5000,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
        vars={
            'last_location_time': (now() - timedelta(minutes=30)).timestamp(),
        },
    )
    last_location_time = (
        now() - timedelta(minutes=7)
    ).replace(microsecond=0).timestamp()

    async def handler(_):
        return web.json_response({
            'results': [{
                'driver_id': courier.external_id,
                'position': {
                    'timestamp': last_location_time,
                },
            }],
        })

    with tap.plan(3, 'Обновить флаг'):
        async with await ext_api(client_dt, handler):
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')

            await courier.reload()
            tap.eq(
                courier.vars('last_location_time', None),
                last_location_time,
                'Флаг обновлён',
            )


async def test_paused_old_geo(tap, dataset, ext_api, now):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 1200,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
    )

    async def handler(_):
        return web.json_response({
            'results': [{
                'driver_id': courier.external_id,
                'position': {
                    'timestamp': (now() - timedelta(minutes=60)).timestamp(),
                },
            }],
        })

    with tap.plan(2, 'Если у курьера есть координаты и активна пауза'):
        async with await ext_api(client_dt, handler):
            user = await dataset.user(store=store)
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                    CourierShiftEvent({
                        'type': 'paused',
                        'created': now() - timedelta(minutes=10),
                        'user_id': user.user_id,
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')


async def test_paused_without_geo(tap, dataset, ext_api, now):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 1200,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
    )

    async def handler(_):
        return web.json_response({
            'results': [],
        })

    with tap.plan(2, 'Если у курьера нет координат и активна пауза'):
        async with await ext_api(client_dt, handler):
            user = await dataset.user(store=store)
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                    CourierShiftEvent({
                        'type': 'paused',
                        'created': now() - timedelta(minutes=10),
                        'user_id': user.user_id,
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')


async def test_paused_saved_geo(tap, dataset, ext_api, now):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 1200,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
        vars={
            'last_location_time': (now() - timedelta(minutes=60)).timestamp(),
        },
    )

    async def handler(_):
        return web.json_response({
            'results': [],
        })

    with tap.plan(2, 'Если у курьера сохранены координаты и активна пауза'):
        async with await ext_api(client_dt, handler):
            user = await dataset.user(store=store)
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                    CourierShiftEvent({
                        'type': 'paused',
                        'created': now() - timedelta(minutes=10),
                        'user_id': user.user_id,
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')


async def test_just_unpaused(tap, dataset, ext_api, now):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 1200,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
        vars={
            'last_location_time': (now() - timedelta(minutes=60)).timestamp(),
        },
    )

    async def handler(_):
        return web.json_response({
            'results': [],
        })

    with tap.plan(2, 'Если у курьера сохранены координаты и закончилась пауза'):
        async with await ext_api(client_dt, handler):
            user = await dataset.user(store=store)
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                    CourierShiftEvent({
                        'type': 'paused',
                        'created': now() - timedelta(minutes=20),
                        'user_id': user.user_id,
                    }),
                    CourierShiftEvent({
                        'type': 'unpaused',
                        'created': now() - timedelta(minutes=10),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')


async def test_unpaused_without_geo(tap, dataset, ext_api, now, time2time):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 300,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
        vars={
            'last_location_time': (now() - timedelta(minutes=60)).timestamp(),
        },
    )

    async def handler(_):
        return web.json_response({
            'results': [],
        })

    with tap.plan(5, 'Если у курьера закончилась пауза давно'):
        async with await ext_api(client_dt, handler):
            user = await dataset.user(store=store)
            unpaused = now() - timedelta(minutes=10)
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=6),
                    }),
                    CourierShiftEvent({
                        'type': 'paused',
                        'created': now() - timedelta(minutes=20),
                        'user_id': user.user_id,
                    }),
                    CourierShiftEvent({
                        'type': 'unpaused',
                        'created': unpaused,
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'leave', 'Смена закрыта')

            event = shift.shift_events[-2]
            tap.eq(event.type, 'stopped', 'Курьер покинул смену')
            tap.eq(event.detail.get('reason'), 'no_geo', 'Сохранили причину')
            tap.eq(
                time2time(event.detail.get('last_location_time')),
                unpaused.replace(microsecond=0),
                'Сохранили параметры закрытия',
            )


@pytest.mark.parametrize(
    'delta,flag_last_location', (
        (2, False), # < absence_period
        (10, True), # < courier_non_geo_threshold
    )
)
async def test_cancel_stopping(
        tap, dataset, ext_api, now, delta, flag_last_location,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 1200,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(hours=2),
        vars={
            'last_location_time': (now() - timedelta(minutes=40)).timestamp(),
        },
    )
    last_location_time = (
        now() - timedelta(minutes=delta)
    ).replace(microsecond=0).timestamp()

    async def handler(_):
        return web.json_response({
            'results': [{
                'driver_id': courier.external_id,
                'position': {
                    'timestamp': last_location_time,
                },
            }],
        })

    with tap.plan(3, 'Не закрытвать смену, если появилось приемлемое гео'):
        async with await ext_api(client_dt, handler):
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=2),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')

            await courier.reload()
            tap.eq(
                courier.vars('last_location_time', None),
                last_location_time if flag_last_location else None,
                'Флаг обновился'
            )


async def test_geo_blocked_stop_checkin(
        tap, dataset, ext_api, now,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_non_geo_threshold': 1200,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(
        cluster=cluster,
        checkin_time=now() - timedelta(minutes=10),
    )
    last_position = (
        now() - timedelta(minutes=30)
    ).replace(microsecond=0).timestamp()

    async def handler(_):
        return web.json_response({
            'results': [{
                'driver_id': courier.external_id,
                'position': {
                    'timestamp': last_position,
                },
            }],
        })

    with tap.plan(3, 'Отмена закрытия смены из-за чекина'):
        async with await ext_api(client_dt, handler):
            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now() - timedelta(hours=2),
                closes_at=now() + timedelta(hours=2),
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(hours=2),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, 'processing', 'Смена активна')

            await courier.reload()
            tap.eq(
                courier.vars('last_location_time', None),
                last_position,
                'Флаг стоит'
            )
