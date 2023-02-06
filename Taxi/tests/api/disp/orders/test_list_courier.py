# pylint: disable=unused-argument,too-many-locals,unused-variable
from datetime import timedelta

import pytest

from stall.model.order import (
    ORDER_DELIVERY_STATUS_ASSIGNED,
    ORDER_DELIVERY_STATUS_TAKEN,
)


async def test_list_free(
        tap, dataset, api, uuid, ext_api, time2iso_utc, now
):
    with tap.plan(8, 'проверяем работу списка свободных'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=uuid(),
        )
        user = await dataset.user(store=store, role='admin')
        courier1 = await dataset.courier(cluster=cluster)
        courier2 = await dataset.courier(cluster=cluster)
        order1 = await dataset.order(
            store=store,
            courier_id=courier1.courier_id,
            eda_status='WAITING_ASSIGNMENTS',
        )
        order2 = await dataset.order(
            store=store,
            courier_id=courier2.courier_id,
            status='complete',
            estatus='done',
            eda_status='DELIVERED',
            eda_status_updated=now() - timedelta(minutes=15),
        )

        async def handler(response):
            return 200, {
                'couriers': [
                    {
                        'courier_id': courier2.external_id,
                        'checkin_timestamp': time2iso_utc(now()),
                    }
                ]
            }
        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order1.order_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('couriers.0')
            t.json_is('couriers.0.status', 'free')
            t.json_is('couriers.0.courier.courier_id', courier2.courier_id)
            t.json_hasnt('couriers.0.orders.0')
            t.json_hasnt('couriers.1')


@pytest.mark.parametrize('eda_status', ORDER_DELIVERY_STATUS_ASSIGNED)
async def test_list_assigned(
        tap, dataset, api, uuid, ext_api, time2iso_utc, now, eda_status
):
    with tap.plan(8, 'проверяем работу списка на лавке'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=uuid(),
        )
        user = await dataset.user(store=store, role='admin')
        courier1 = await dataset.courier(cluster=cluster)
        courier2 = await dataset.courier(cluster=cluster)
        order1 = await dataset.order(
            store=store,
            courier_id=courier1.courier_id,
            eda_status='WAITING_ASSIGNMENTS',
        )
        order2 = await dataset.order(
            store=store,
            courier_id=courier2.courier_id,
            eda_status=eda_status,
        )

        async def handler(response):
            return 200, {
                'couriers': [
                    {
                        'courier_id': courier2.external_id,
                        'checkin_timestamp': time2iso_utc(now()),
                    }
                ]
            }
        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order1.order_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('couriers.0')
            t.json_is('couriers.0.status', 'assigned')
            t.json_is('couriers.0.courier.courier_id', courier2.courier_id)
            t.json_is('couriers.0.orders.0.order_id', order2.order_id)
            t.json_hasnt('couriers.1')


@pytest.mark.parametrize('eda_status', ORDER_DELIVERY_STATUS_TAKEN)
async def test_list_busy(
        tap, dataset, api, uuid, ext_api, time2iso_utc, now, eda_status
):
    with tap.plan(8, 'занятые курьеры'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=uuid(),
        )
        user = await dataset.user(store=store, role='admin')
        courier1 = await dataset.courier(cluster=cluster)
        courier2 = await dataset.courier(cluster=cluster)
        order1 = await dataset.order(
            store=store,
            courier_id=courier1.courier_id,
            eda_status='WAITING_ASSIGNMENTS',
        )
        order2 = await dataset.order(
            store=store,
            courier_id=courier2.courier_id,
            eda_status=eda_status,
        )

        async def handler(response):
            return 200, {
                'couriers': [
                    {
                        'courier_id': courier2.external_id,
                        'checkin_timestamp': time2iso_utc(now()),
                    }
                ]
            }
        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order1.order_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('couriers.0')
            t.json_is('couriers.0.status', 'busy')
            t.json_is('couriers.0.courier.courier_id', courier2.courier_id)
            t.json_is('couriers.0.orders.0.order_id', order2.order_id)
            t.json_hasnt('couriers.1')


async def test_list_return(
        tap, dataset, api, uuid, ext_api, time2iso_utc, now
):
    with tap.plan(8, 'когда курьер без заказа возвращается в лавку он занят'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=uuid(),
        )
        user = await dataset.user(store=store, role='admin')
        courier1 = await dataset.courier(cluster=cluster)
        courier2 = await dataset.courier(cluster=cluster)
        order1 = await dataset.order(
            store=store,
            courier_id=courier1.courier_id,
            eda_status='WAITING_ASSIGNMENTS',
        )
        order2 = await dataset.order(
            store=store,
            courier_id=courier2.courier_id,
            status='complete',
            estatus='done',
            eda_status='DELIVERED',
            eda_status_updated=now() - timedelta(minutes=15),
        )

        async def handler(response):
            return 200, {
                'couriers': [
                    {
                        'courier_id': courier2.external_id,
                        'checkin_timestamp': time2iso_utc(
                            now()- timedelta(minutes=25)
                        ),
                    }
                ]
            }
        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order1.order_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('couriers.0')
            t.json_is('couriers.0.status', 'busy')
            t.json_is('couriers.0.courier.courier_id', courier2.courier_id)
            t.json_is('couriers.0.orders.0.order_id', order2.order_id)
            t.json_hasnt('couriers.1')


async def test_list_return_empty_updated(
        tap, dataset, api, uuid, ext_api, time2iso_utc, now
):
    with tap.plan(8, 'возврат на старых заказах где поле не установлено'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=uuid(),
        )
        user = await dataset.user(store=store, role='admin')
        courier1 = await dataset.courier(cluster=cluster)
        courier2 = await dataset.courier(cluster=cluster)
        order1 = await dataset.order(
            store=store,
            courier_id=courier1.courier_id,
            eda_status='WAITING_ASSIGNMENTS',
        )
        order2 = await dataset.order(
            store=store,
            courier_id=courier2.courier_id,
            status='complete',
            estatus='done',
            eda_status='DELIVERED',
            eda_status_updated=None,
        )

        async def handler(response):
            return 200, {
                'couriers': [
                    {
                        'courier_id': courier2.external_id,
                        'checkin_timestamp': time2iso_utc(
                            now()- timedelta(minutes=25)
                        ),
                    }
                ]
            }
        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order1.order_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('couriers.0')
            t.json_is('couriers.0.status', 'free')
            t.json_is('couriers.0.courier.courier_id', courier2.courier_id)
            t.json_hasnt('couriers.0.orders.0')
            t.json_hasnt('couriers.1')


async def test_unknown_courier(
        tap, dataset, api, uuid, ext_api, time2iso_utc, now
):
    with tap.plan(6, 'пришол неизвестный курьер'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=None,
        )
        user = await dataset.user(store=store, role='admin')
        order = await dataset.order(store=store)

        async def handler(response):
            return 200, {
                'couriers': [
                    {
                        'courier_id': uuid(),
                        'checkin_timestamp': time2iso_utc(now()),
                    }
                ]
            }
        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order.order_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_hasnt('couriers.0')
            t.json_hasnt('couriers_assigned.0')
            t.json_hasnt('couriers_busy.0')


async def test_gateway_error(tap, dataset, api, uuid, ext_api):
    with tap.plan(3, 'ошибка если сервис совсем не работает'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=uuid(),
        )
        user = await dataset.user(store=store, role='admin')
        order = await dataset.order(store=store)

        async def handler(response):
            return (500, '')

        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order.order_id},
            )
            t.status_is(424, diag=True)
            t.json_is('code', 'ER_EXTERNAL_SERVICE')


async def test_empty(
        tap, dataset, api, uuid, ext_api, time2iso_utc, now
):
    with tap.plan(4, 'пришол неизвестный курьер'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=None,
        )
        user = await dataset.user(store=store, role='admin')
        order = await dataset.order(store=store)

        async def handler(response):
            return 200, {
                'couriers': []
            }
        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order.order_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_hasnt('couriers.0')


async def test_list_return_last_order(
        tap, dataset, api, uuid, ext_api, time2iso_utc, now):
    with tap.plan(
            5,
            'Курьер без заказа возвращается '
            'в лавку и у него проставлено время последнего заказа'
    ):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=uuid(),
        )
        user = await dataset.user(store=store, role='admin')
        courier1 = await dataset.courier(
            cluster=cluster,
            last_order_time=(now() - timedelta(minutes=25))
        )
        courier2 = await dataset.courier(
            cluster=cluster,
            last_order_time=(now() - timedelta(minutes=5))
        )
        courier3 = await dataset.courier(
            cluster=cluster,
            last_order_time=(now() - timedelta(minutes=20))
        )
        order1 = await dataset.order(
            store=store,
            eda_status='WAITING_ASSIGNMENTS',
        )
        order2 = await dataset.order(
            store=store,
            courier_id=courier3.courier_id,
            status='processing',
            estatus='begin',
            eda_status='DELIVERED',
            eda_status_updated=now() - timedelta(minutes=20),
        )
        tap.ok(order2, 'Повесился заказ в процессинге')

        async def handler(response):
            return 200, {
                'couriers': [
                    {
                        'courier_id': courier2.external_id,
                        'checkin_timestamp': time2iso_utc(
                            now()- timedelta(minutes=25)
                        ),
                    },
                    {
                        'courier_id': courier1.external_id,
                        'checkin_timestamp': time2iso_utc(
                            now() - timedelta(minutes=5)
                        ),
                    },
                    {
                        'courier_id': courier3.external_id,
                        'checkin_timestamp': time2iso_utc(
                            now() - timedelta(minutes=25)
                        ),
                    },
                ]
            }
        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order1.order_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            tap.eq(
                {
                    (courier['courier']['courier_id'], courier['status'])
                    for courier in t.res['json']['couriers']
                },
                {
                    (courier1.courier_id, 'free'),
                    (courier2.courier_id, 'busy'),
                    (courier3.courier_id, 'busy'),
                },
                'два курьера заняты, один свободен'
            )


# pylint: disable=too-many-arguments
@pytest.mark.parametrize('batch_limit, expected_status', [
    (4, 'assigned'),
    (2, 'busy')
])
async def test_list_assigned_limit(
        tap, dataset, api, uuid, ext_api, time2iso_utc, now,
        batch_limit, expected_status, cfg
):
    with tap.plan(11, 'проверяем лимит на батч'):
        cfg.set('manual_dispatch.batch_limit', batch_limit)
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            courier_area_id=uuid(),
        )
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)

        for i in range(3):
            order = await dataset.order(
                store=store,
                courier_id=courier.courier_id,
                eda_status='WAITING_ASSIGNMENTS',
            )
            tap.ok(order, f'Ордер {i} создан')

        order_to_assign = await dataset.order(
            store=store,
            eda_status='WAITING_ASSIGNMENTS',
        )
        tap.ok(order_to_assign, 'Ордер для назначения')

        async def handler(response):
            return 200, {
                'couriers': [
                    {
                        'courier_id': courier.external_id,
                        'checkin_timestamp': time2iso_utc(now()),
                    }
                ]
            }
        async with await ext_api('grocery_checkins', handler):
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_list_courier',
                json={'order_id': order_to_assign.order_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('couriers.0')
            t.json_is('couriers.0.status', expected_status)
            t.json_is('couriers.0.courier.courier_id', courier.courier_id)
            t.json_hasnt('couriers.1')
