import pytest
from stall.model.suggest import Suggest


async def test_begin(tap, dataset):
    with tap.plan(8, 'Срыв заказа'):
        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            status='canceled',
            estatus='begin',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'update_required', 'update_required')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_update_required(tap, dataset, wait_order_status):
    with tap.plan(17, 'Срыв заказа и обновление required'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            type='sale_stowage',
            store=store,
            acks=[user.user_id],
            status='reserving',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 45,
                    'valid': '2018-01-03',
                }
            ]
        )

        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.eq(s.valid.strftime('%F'), '2018-01-03', 'valid')
            tap.eq(s.count, 45, 'count')
            tap.eq(s.product_id, product.product_id, 'product_id')

            tap.ok(await s.done(count=5), 'закрыли')

        # генерирует новый саджест
        await wait_order_status(order, ('processing', 'waiting'))
        # записывает товар на полку
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'саджест')

        tap.ok(await order.cancel(), 'отменяем')
        await wait_order_status(order, ('canceled', 'update_required'))
        await order.business.order_changed()

        await order.reload()

        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.required[0]['result_count'],
               5,
               'result_count обновился в required')


@pytest.mark.parametrize(
    'stages',
    [
        ['store', 'store'],
        ['trash', 'store'],
        ['store', 'trash'],
        ['trash', 'trash'],
    ]
)
async def test_suggests_drop(tap, dataset, wait_order_status, stages):
    with tap.plan(14, 'Срыв заказа и удаление саджестов'):
        store = await dataset.store()

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            status='canceled',
            estatus='begin',
            vars={
                'put': {}
            }
        )
        tap.ok(order, 'Заказ получен')

        suggest1 = await dataset.suggest(
            order,
            status='done',
            type='box2shelf',
            product_id=product.product_id,
            count=10,
            result_count=5,
            vars={
                'stage': stages[0]
            }
        )
        tap.ok(suggest1, 'Закрытый саджест')
        suggest2 = await dataset.suggest(
            order,
            status='request',
            type='box2shelf',
            product_id=product.product_id,
            count=10,
            result_count=5,
            vars={
                'stage': stages[1]
            }
        )
        tap.ok(suggest2, 'Cаджест в реквесте')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Два саджеста')

        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await wait_order_status(order, ('canceled', 'done'))

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'done', 'done')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Саджесты удалены')

        await order.reload()
        tap.ok('put' not in order.vars, 'удалены put')
