# pylint: disable=unused-variable

import pytest

from stall.model.order import ORDER_INCOMPLETE_STATUSES


@pytest.mark.parametrize('eda_status', [
    'UNCONFIRMED',
    'CALL_CENTER_CONFIRMED',
    'PLACE_CONFIRMED',
    'WAITING_ASSIGNMENTS',
    'READY_FOR_DELIVERY',
    'ARRIVED_TO_CUSTOMER',
    'CUSTOMER_NO_SHOW',
    'AWAITING_CARD_PAYMENT',
    'ORDER_TAKEN',
    'COURIER_ASSIGNED',
])
async def test_eda_status(tap, dataset, eda_status):
    with tap.plan(2, 'Список заказов в процессе выполнения курьером'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(store=store)
        order = await dataset.order(
            store=store,
            courier_id=courier.courier_id,
            courier_shift_id=shift.courier_shift_id,
            status='complete',
            eda_status=eda_status,
        )

        orders = await dataset.Order.list_processing_by_courier(
            courier_id=courier.courier_id
        )
        tap.eq(len(orders), 1, 'Заказ получен')
        tap.eq(orders[0].order_id, order.order_id, 'Тот который нужен')


@pytest.mark.parametrize('eda_status', [
    'DELIVERED',
    'CANCELLED',
    'UNKNOWN',
    'PICKUP',
])
async def test_eda_status_none(tap, dataset, eda_status):
    with tap.plan(1, 'Нет заказов на исполнении'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(store=store)
        order = await dataset.order(
            store=store,
            courier_id=courier.courier_id,
            courier_shift_id=shift.courier_shift_id,
            status='complete',
            eda_status=eda_status,
        )

        orders = await dataset.Order.list_processing_by_courier(
            courier_id=courier.courier_id
        )
        tap.eq(len(orders), 0, 'Заказов нет')


@pytest.mark.parametrize('status', ORDER_INCOMPLETE_STATUSES)
async def test_status(tap, dataset, status):
    with tap.plan(2, 'Нет статуса еды, но уже у нас назначен'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(store=store)
        order = await dataset.order(
            store=store,
            courier_id=courier.courier_id,
            courier_shift_id=shift.courier_shift_id,
            status=status,
        )

        orders = await dataset.Order.list_processing_by_courier(
            courier_id=courier.courier_id
        )
        tap.eq(len(orders), 1, 'Заказ получен')
        tap.eq(orders[0].order_id, order.order_id, 'Тот который нужен')


@pytest.mark.parametrize('status', ['canceled', 'failed'])
async def test_status_fail(tap, dataset, status):
    with tap.plan(1, 'Завершился у нас, до доставки точно не дойдет'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(store=store)
        order = await dataset.order(
            store=store,
            courier_id=courier.courier_id,
            courier_shift_id=shift.courier_shift_id,
            status=status,
        )

        orders = await dataset.Order.list_processing_by_courier(
            courier_id=courier.courier_id
        )
        tap.eq(len(orders), 0, 'Заказов нет')
