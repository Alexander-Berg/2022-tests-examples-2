# pylint: disable=too-many-locals

from datetime import timedelta

import pytest
from aiohttp import web

from scripts.cron.close_courier_shifts_by_offline import (
    close_courier_shifts_by_offline,
)
from stall.client.contractor_status_history import client as client_cs
from stall.model.courier_shift import CourierShiftEvent


@pytest.mark.parametrize(
    'status,res,updated', (
        ('offline', 'leave', 1643373127.382),
        ('online', 'processing', 1643373127.382),
        ('busy', 'processing', 1643373127.382),
        ('offline', 'processing', None),
        ('online', 'processing', None),
        ('busy', 'processing', None),
    )
)
async def test_simple(
        tap, dataset, ext_api, now, status, res, updated,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_offline_threshold': 1800,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(cluster=cluster)
    park_id, profile_id = courier.external_id.split('_')

    async def handler(_):
        return web.json_response({
            'contractors': [{
                'park_id': park_id,
                'profile_id': profile_id,
                'events': [{
                    'status': status,
                    'timestamp': updated or now().timestamp(),
                }],
            }],
        })

    with tap.plan(3, 'Закрывать смену, если курьер вышел в офлайн'):
        async with await ext_api(client_cs, handler) as client:
            req = await client.events(
                ids=[courier.external_id],
                dttm_from=now(),
                dttm_to=now(),
            )
            tap.ok(req, 'Получили ответ от внешнего API')

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
                        'created': now() - timedelta(minutes=60),
                        'user_id': user.user_id,
                    }),
                    CourierShiftEvent({
                        'type': 'unpaused',
                        'created': now() - timedelta(minutes=40),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, res, 'Новый статус смены')


@pytest.mark.parametrize(
    'started_before,res', (
        (1000, 'processing'),   # < courier_offline_threshold
        (2000, 'leave'),        # > courier_offline_threshold
    )
)
async def test_before_started(
        tap, dataset, ext_api, now, started_before, res,
):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_offline_threshold': 1800,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(cluster=cluster)
    park_id, profile_id = courier.external_id.split('_')
    now_ = now().timestamp()

    async def handler(_):
        return web.json_response({
            'contractors': [{
                'park_id': park_id,
                'profile_id': profile_id,
                'events': [{
                    'status': 'offline',
                    'timestamp': now_ - 3000,
                }],
            }],
        })

    with tap.plan(3, 'Не закрывать смену, если курьер ещё не вошёл в онлайн'):
        async with await ext_api(client_cs, handler) as client:
            req = await client.events(
                ids=[courier.external_id],
                dttm_from=now(),
                dttm_to=now(),
            )
            tap.ok(req, 'Получили ответ от внешнего API')

            shift = await dataset.courier_shift(
                courier_id=courier.courier_id,
                status='processing',
                started_at=now_ - started_before,
                closes_at=now_ + 7200,
                store=store,
                shift_events=[
                    CourierShiftEvent({
                        'type': 'started',
                        'created': now() - timedelta(seconds=started_before),
                    }),
                ],
            )

            tap.eq(shift.status, 'processing', 'Смена активна')

            await close_courier_shifts_by_offline(cluster_id=cluster.cluster_id)

            await shift.reload()
            tap.eq(shift.status, res, 'Новый статус смены')


async def test_paused(tap, dataset, ext_api, now):
    cluster = await dataset.cluster(courier_shift_setup={
        'courier_offline_threshold': 1800,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(cluster=cluster)
    park_id, profile_id = courier.external_id.split('_')

    async def handler(_):
        return web.json_response({
            'contractors': [{
                'park_id': park_id,
                'profile_id': profile_id,
                'events': [{
                    'status': 'offline',
                    'timestamp': 1643373127.382,
                }],
            }],
        })

    with tap.plan(3, 'Не pакрывать смену, если активна пауза'):
        async with await ext_api(client_cs, handler) as client:
            req = await client.events(
                ids=[courier.external_id],
                dttm_from=now(),
                dttm_to=now(),
            )
            tap.ok(req, 'Получили ответ от внешнего API')

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
        'courier_offline_threshold': 1800,
        'stopped_leave_before_time': 0,
    })
    store = await dataset.store(cluster=cluster)
    courier = await dataset.courier(cluster=cluster)
    park_id, profile_id = courier.external_id.split('_')

    async def handler(_):
        return web.json_response({
            'contractors': [{
                'park_id': park_id,
                'profile_id': profile_id,
                'events': [{
                    'status': 'offline',
                    'timestamp': 1643373127.382,
                }],
            }],
        })

    with tap.plan(3, 'Не закрывать смену, если пауза только закончилась'):
        async with await ext_api(client_cs, handler) as client:
            req = await client.events(
                ids=[courier.external_id],
                dttm_from=now(),
                dttm_to=now(),
            )
            tap.ok(req, 'Получили ответ от внешнего API')

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
                        'created': now() - timedelta(minutes=30),
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
