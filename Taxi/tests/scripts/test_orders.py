from datetime import timedelta

import pytest

from libstall.util import now
from stall.scripts.orders import cancel_orders


async def test_cancel_orders(tap, dataset):
    with tap.plan(6, 'Отмены старых (зависших) заказов типа order'):
        store = await dataset.store()
        another_store = await dataset.store()
        days = 3
        created = now() - timedelta(days=days)

        order1 = await dataset.order(
            type='order',
            store=store,
            status='request',
            created=created - timedelta(minutes=1),
        )

        order1_2 = await dataset.order(
            type='order',
            store=store,
            status='request',
            created=created - timedelta(minutes=1),
        )

        order2 = await dataset.order(
            type='acceptance',
            store=store,
            status='request',
            created=created - timedelta(minutes=1),
        )

        order3 = await dataset.order(
            type='order',
            store=store,
            status='request',
            created=created + timedelta(minutes=1),
        )

        order4 = await dataset.order(
            type='order',
            store=store,
            status='reserving',
            created=created - timedelta(minutes=1),
        )

        order5 = await dataset.order(
            type='order',
            store=another_store,
            status='request',
            created=created - timedelta(minutes=1),
        )

        await cancel_orders(days, 'order', store.store_id)

        await order1.reload()
        await order1_2.reload()
        await order2.reload()
        await order3.reload()
        await order4.reload()
        await order5.reload()

        tap.eq_ok(order1.target, 'canceled', 'Старый order отменен')
        tap.eq_ok(order1_2.target, 'canceled', 'Еще один старый order отменен')
        tap.eq_ok(order2.target, 'complete', 'Другой тип - не меняем')
        tap.eq_ok(order3.target, 'complete', 'Не старый - не меняем')
        tap.eq_ok(order4.target, 'complete', 'Уже в работе - не меняем')
        tap.eq_ok(order5.target, 'complete', 'Из другой лавки - не меняем')


@pytest.mark.parametrize('order_type', ('order', 'acceptance'))
async def test_cancel_all_types(tap, dataset, order_type):
    with tap.plan(4, 'Отмены старых (зависших) заказов всех типов'):
        store = await dataset.store()
        another_store = await dataset.store()
        days = 3
        created = now() - timedelta(days=days)

        order1 = await dataset.order(
            type=order_type,
            store=store,
            status='request',
            created=created - timedelta(minutes=1),
        )

        order3 = await dataset.order(
            type=order_type,
            store=store,
            status='request',
            created=created + timedelta(minutes=1),
        )

        order4 = await dataset.order(
            type=order_type,
            store=store,
            status='reserving',
            created=created - timedelta(minutes=1),
        )

        order5 = await dataset.order(
            type=order_type,
            store=another_store,
            status='request',
            created=created - timedelta(minutes=1),
        )

        await cancel_orders(days, None, store.store_id)

        await order1.reload()
        await order3.reload()
        await order4.reload()
        await order5.reload()

        tap.eq_ok(order1.target, 'canceled', 'Старый order отменен')
        tap.eq_ok(order3.target, 'complete', 'Не старый - не меняем')
        tap.eq_ok(order4.target, 'complete', 'Уже в работе - не меняем')
        tap.eq_ok(order5.target, 'complete', 'Из другой лавки - не меняем')
