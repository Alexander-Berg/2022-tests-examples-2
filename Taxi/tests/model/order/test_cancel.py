import pytest


@pytest.mark.parametrize('order_status',
                         ['reserving', 'approving', 'request'])
async def test_cancel_nonprocessing(tap, dataset, order_status):
    with tap.plan(10, 'Отмена заказа в статусах до processing'):
        order = await dataset.order(status=order_status, estatus='status1')
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, 'статус')
        tap.eq(order.estatus, 'status1', 'странный сабстатус')
        tap.eq(order.target, 'complete', 'изначально заказ имеет цель комплит')

        revision = order.revision
        lsn = order.lsn

        tap.ok(await order.cancel(), 'Отмена совершена')

        tap.eq(order.revision, revision + 1, 'Ревизия увеличена')
        tap.ok(order.lsn > lsn, 'lsn растёт')
        tap.eq(order.status, order_status, 'статус остался')
        tap.eq(order.target, 'canceled', 'цель')
        tap.eq(order.estatus, 'status1', 'сабстатус остался')


@pytest.mark.parametrize('order_status', ['processing'])
async def test_cancel_processing(tap, dataset, order_status):
    with tap.plan(9, 'Отмена заказа в статусах до processing'):
        order = await dataset.order(status=order_status, estatus='status1')
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, 'статус')
        tap.eq(order.estatus, 'status1', 'странный сабстатус')
        tap.eq(order.target, 'complete', 'изначально заказ имеет цель комплит')

        revision = order.revision

        tap.ok(await order.cancel(), 'Отмена совершена')

        tap.eq(order.revision, revision + 1, 'Ревизия увеличена')
        tap.eq(order.status, 'processing', 'Статус не изменился')
        tap.eq(order.target, 'canceled', 'цель')
        tap.eq(order.estatus, 'status1', 'сабстатус остался')


@pytest.mark.parametrize('order_status', ['complete', 'failed'])
async def test_cancel_done(tap, dataset, order_status):
    with tap.plan(10, 'Отмена заказа в статусах до processing'):
        order = await dataset.order(status=order_status,
                                    estatus='status1',
                                    type='writeoff')
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, 'статус')
        tap.eq(order.estatus, 'status1', 'странный сабстатус')
        tap.eq(order.target, 'complete', 'изначально заказ имеет цель комплит')

        revision = order.revision

        tap.ok(not await order.cancel(), 'Отмена совершена')
        tap.ok(await order.reload(), 'перезагружен из БД')

        tap.eq(order.revision, revision, 'Ревизия не поменялась')
        tap.eq(order.status, order_status, 'Статус не изменился')
        tap.eq(order.target, 'complete', 'цель осталась')
        tap.eq(order.estatus, 'status1', 'сабстатус - не поменялся')


@pytest.mark.parametrize('order_status', ['canceled'])
async def test_cancel_canceled(tap, dataset, order_status):
    with tap.plan(10, 'Отмена уже отмененного заказа'):
        order = await dataset.order(status=order_status,
                                    estatus='status1',
                                    type='writeoff')
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, 'статус')
        tap.eq(order.estatus, 'status1', 'странный сабстатус')
        tap.eq(order.target, 'complete', 'изначально заказ имеет цель комплит')

        revision = order.revision

        tap.ok(await order.cancel(), 'Отмена совершена')
        tap.ok(await order.reload(), 'перезагружен из БД')

        tap.eq(order.revision, revision, 'Ревизия не поменялась')
        tap.eq(order.status, order_status, 'Статус не изменился')
        tap.eq(order.target, 'complete', 'цель осталась')
        tap.eq(order.estatus, 'status1', 'сабстатус - не поменялся')


async def test_cancel_complete(tap, dataset):
    with tap.plan(13, 'Отмена заказа .order в статусе complete'):
        order = await dataset.order(status='complete',
                                    estatus='status1',
                                    type='order')
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, 'complete', 'статус')
        tap.eq(order.estatus, 'status1', 'странный сабстатус')
        tap.eq(order.target, 'complete', 'изначально заказ имеет цель комплит')

        revision = order.revision

        tap.ok(await order.cancel(), 'Отмена совершена')
        tap.ok(await order.reload(), 'перезагружен из БД')

        tap.eq(order.revision, revision + 1, 'Ревизия увеличилась')
        tap.eq(order.status, 'complete', 'Статус не изменился')
        tap.eq(order.target, 'canceled', 'цель')
        tap.eq(order.estatus, 'status1', 'сабстатус - не поменялся')

        tap.ok(await order.cancel(), 'Отмена совершена ещё раз')
        tap.ok(await order.reload(), 'перезагружен из БД')

        tap.eq(order.revision, revision + 1, 'Ревизия больше не менялась')


async def test_cancel_complete_ttl(tap, dataset):
    with tap.plan(6, 'Отмена заказа .order в статусе complete'):
        order = await dataset.order(status='complete',
                                    estatus='status1',
                                    type='order',
                                    created='2011-11-12 12:00:00+0000')
        tap.ok(order, 'заказ создан')
        tap.eq(order.created.strftime('%F'), '2011-11-12', 'дата создания')
        tap.eq(order.status, 'complete', 'статус')
        tap.eq(order.estatus, 'status1', 'странный сабстатус')
        tap.eq(order.target, 'complete', 'изначально заказ имеет цель комплит')

        tap.ok(not await order.cancel(), 'Отмена уже не может состояться')


async def test_cancel_force(tap, dataset):
    with tap.plan(6, 'Пермит на форсинг отмены'):
        user = await dataset.user(role='admin')
        order = await dataset.order(status='complete',
                                    estatus='status1',
                                    type='order',
                                    created='2011-11-12 12:00:00+0000')
        tap.ok(order, 'заказ создан')
        tap.eq(order.created.strftime('%F'), '2011-11-12', 'дата создания')
        tap.eq(order.status, 'complete', 'статус')
        tap.eq(order.estatus, 'status1', 'странный сабстатус')
        tap.eq(order.target, 'complete', 'изначально заказ имеет цель комплит')

        tap.ok(await order.cancel(user=user), 'Отмена форсится пермитом')
