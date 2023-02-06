import datetime

from dateutil.tz import UTC
import pytest


async def test_approve(tap, dataset):
    with tap.plan(10, 'Одобрение заказа'):

        order = await dataset.order(status='approving')
        tap.ok(order, 'Заказ создан')
        tap.eq(order.approved, None, 'Время одобрения нет')

        approved_time = datetime.datetime(2020, 1, 1, tzinfo=UTC)
        revision = order.revision
        lsn = order.lsn

        tap.ok(await order.approve(time=approved_time),
               'Одобрено')
        tap.ok(order.lsn > lsn, 'lsn растёт')
        tap.eq(order.approved, approved_time, 'Время одобрения')
        tap.eq(order.revision, revision + 1, 'ревизия инкрементнулась')

        lsn = order.lsn
        tap.ok(await order.approve(), 'Повторное одобрение')
        tap.eq(order.approved, approved_time,
               'Время одобрения не изменилось')
        tap.eq(order.revision, revision + 1, 'ревизия не инкрементнулась')
        tap.ok(order.lsn == lsn, 'lsn от повтора не растёт')


@pytest.mark.parametrize('status', ['complete', 'canceled', 'failed'])
async def test_too_late(tap, dataset, status):
    with tap.plan(5, 'Одобрение актуально только до завершения ордера'):

        order = await dataset.order(status=status)
        revision = order.revision
        tap.ok(order, 'Заказ создан')

        tap.ok(not await order.approve(), 'Одобрение запоздало')
        tap.ok(await order.reload(), 'перевыбрали из БД')
        tap.eq(order.approved, None, 'Время одобрения')
        tap.eq(order.revision, revision, 'Изменений в БД не было')
