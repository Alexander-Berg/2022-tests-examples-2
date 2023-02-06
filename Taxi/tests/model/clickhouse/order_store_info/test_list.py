import datetime
import pytest

from libstall.util import time2time
from stall.model.order import ORDER_STATUS, ORDER_INCOMPLETE_STATUSES
from stall.model.clickhouse.order_store_info import OrderStoreInfo


async def test_last_info(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(9, 'Показатели ордера в последнем статусе'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_wms_order_status_update(
            order=order,
            status='request',
            timestamp=today_at_12,
            items_count=0,
            items_uniq=0,
            suggests_count=0,
        )
        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
            items_count=2,
            items_uniq=2,
            suggests_count=2,
        )

        orders_info = await OrderStoreInfo.list(
            store_id=order.store_id,
            end_timestamp=today_at_12 + datetime.timedelta(seconds=180)
        )

        tap.eq(len(orders_info), 1, '1 запись получена')
        tap.eq(orders_info[0].store_id, order.store_id, 'store_id')
        tap.eq(orders_info[0].type, 'order', 'type')
        tap.eq(orders_info[0].status, 'processing', 'status')
        tap.eq(orders_info[0].order_id, order.order_id, 'order_id')
        tap.eq(orders_info[0].duration, 120, 'duration')
        tap.eq(orders_info[0].items_count, 2, 'items_count')
        tap.eq(orders_info[0].items_uniq, 2, 'items_uniq')
        tap.eq(orders_info[0].suggests_count, 2, 'suggests_count')


async def test_last_info_duplicate(tap, dataset, now, tzone,
                                   clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            9,
            'Время в статусе считается от перехода в статус. '
            'Количество считается по последнему значению'
        ):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_wms_order_status_update(
            order=order,
            status='request',
            timestamp=today_at_12,
            items_count=0,
            items_uniq=0,
            suggests_count=0,
        )
        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
            items_count=2,
            items_uniq=2,
            suggests_count=2,
        )
        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=120),
            items_count=4,
            items_uniq=5,
            suggests_count=6,
        )

        orders_info = await OrderStoreInfo.list(
            store_id=order.store_id,
            end_timestamp=today_at_12 + datetime.timedelta(seconds=180)
        )

        tap.eq(len(orders_info), 1, '1 запись получена')
        tap.eq(orders_info[0].store_id, order.store_id, 'store_id')
        tap.eq(orders_info[0].type, 'order', 'type')
        tap.eq(orders_info[0].status, 'processing', 'status')
        tap.eq(orders_info[0].order_id, order.order_id, 'order_id')
        tap.eq(orders_info[0].duration, 120, 'duration')
        tap.eq(orders_info[0].items_count, 4, 'items_count')
        tap.eq(orders_info[0].items_uniq, 5, 'items_uniq')
        tap.eq(orders_info[0].suggests_count, 6, 'suggests_count')


@pytest.mark.parametrize(
    'status',
    set(ORDER_STATUS) - set(ORDER_INCOMPLETE_STATUSES)
)
async def test_info_for_complete(
        tap, dataset, now, tzone, clickhouse_client, status
):
    # pylint: disable=unused-argument
    with tap.plan(1, f'Ордера в {status} не учитываются'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_wms_order_status_update(
            order=order,
            status='request',
            timestamp=today_at_12,
        )
        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
        )
        await dataset.ch_wms_order_status_update(
            order=order,
            status=status,
            timestamp=today_at_12 + datetime.timedelta(seconds=120),
        )

        orders_info = await OrderStoreInfo.list(
            store_id=order.store_id,
            end_timestamp=today_at_12 + datetime.timedelta(seconds=180)
        )

        tap.eq(len(orders_info), 0, 'Нет записей')


async def test_type_filter(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Фильтр по типу ордера'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_wms_order_status_update(
            order=order,
            type='stowage',
            status='request',
            timestamp=today_at_12,
        )

        orders_info = await OrderStoreInfo.list(
            store_id=order.store_id,
            order_type='stowage',
            end_timestamp=today_at_12 + datetime.timedelta(seconds=180)
        )

        tap.eq(len(orders_info), 1, '1 запись получена')
        tap.eq(orders_info[0].store_id, order.store_id, 'store_id')
        tap.eq(orders_info[0].type, 'stowage', 'type')

        orders_info = await OrderStoreInfo.list(
            store_id=order.store_id,
            order_type='order',
            end_timestamp=today_at_12 + datetime.timedelta(seconds=180)
        )

        tap.eq(len(orders_info), 0, 'Нет записей')


async def test_pause_processing(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(2, 'Для ордер в статусе processing учитывается пауза'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12,
            total_pause=140,
        )

        orders_info = await OrderStoreInfo.list(
            store_id=order.store_id,
            end_timestamp=today_at_12 + datetime.timedelta(seconds=180)
        )

        tap.eq(orders_info[0].order_id, order.order_id, 'order_id')
        tap.eq(orders_info[0].duration, 40, 'duration (пауза в 140 секунд)')


async def test_pause_request(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(2, 'Для ордер в статусе request пауза не учитывается'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_wms_order_status_update(
            order=order,
            status='request',
            timestamp=today_at_12,
            total_pause=100,
        )

        orders_info = await OrderStoreInfo.list(
            store_id=order.store_id,
            end_timestamp=today_at_12 + datetime.timedelta(seconds=180)
        )

        tap.eq(orders_info[0].order_id, order.order_id, 'order_id')
        tap.eq(orders_info[0].duration, 180, 'duration (пауза не учитывается)')


async def test_pause_null(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(2, 'Для ордер в статусе processing учитывается пауза'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12,
            total_pause=None,
        )

        orders_info = await OrderStoreInfo.list(
            store_id=order.store_id,
            end_timestamp=today_at_12 + datetime.timedelta(seconds=180)
        )

        tap.eq(orders_info[0].order_id, order.order_id, 'order_id')
        tap.eq(
            orders_info[0].duration,
            180,
            'duration (NULL пауза не ломает запрос)'
        )
