# pylint: disable=too-many-locals, too-many-statements

from libstall.util import now
from stall.model.suggest import Suggest


async def test_errors_shelf2box(tap, wait_order_status, dataset, cfg):
    cfg.set(
        'business.order.stowage.suggest_conditions.need_valid.testing',
        False
    )
    cfg.set(
        'business.order.stowage.suggest_conditions.need_valid.local',
        False
    )
    with tap.plan(26, 'Откат саджестов при раскладке'):

        product1 = await dataset.product()
        product2 = await dataset.product()

        store   = await dataset.full_store()
        user    = await dataset.user(store=store)

        await dataset.shelf(store=store, type='store')
        await dataset.shelf(store=store, type='trash')

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required = [
                {'product_id': product1.product_id, 'count': 1},
                {'product_id': product2.product_id, 'count': 2},
            ],
        )
        tap.ok(order, 'Заказ получен')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Список саджестов shelf2box')
        suggests = dict((x.product_id, x) for x in suggests)

        with suggests[product1.product_id] as suggest:
            tap.ok(await suggest.done(), 'Саджест выполнен')

        with suggests[product2.product_id] as suggest:
            tap.ok(await suggest.done(), 'Саджест выполнен')

        tap.ok(await order.cancel(), 'Отмена')

        await wait_order_status(
            order,
            ('processing', 'suggests_error'),
        )

        tap.ok(
            await order.business.order_changed(),
            'Обработчик запущен'
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'canceled', 'target: canceled')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2 + 2, 'Список саджестов + откат')

        shelf2box = dict(
            (x.product_id, x) for x in suggests if x.type == 'shelf2box'
        )
        box2shelf = dict(
            (x.product_id, x) for x in suggests if x.type == 'box2shelf'
        )

        with shelf2box[product1.product_id] as suggest:
            parent = box2shelf[suggest.product_id]

            tap.eq(parent.conditions.editable, False, 'Редактировать нельзя')

            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.vars['parent'], parent.suggest_id, 'Родитель')
            tap.eq(suggest.count, 1, 'Количество возврата')
            tap.eq(suggest.order, -parent.order, 'Обратный порядок')
            tap.eq(suggest.shelf_id, parent.shelf_id, 'Полка')

        with shelf2box[product2.product_id] as suggest:
            parent = box2shelf[suggest.product_id]

            tap.eq(parent.conditions.editable, False, 'Редактировать нельзя')

            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.vars['parent'], parent.suggest_id, 'Родитель')
            tap.eq(suggest.count, 2, 'Количество возврата')
            tap.eq(suggest.order, -parent.order, 'Обратный порядок')
            tap.eq(suggest.shelf_id, parent.shelf_id, 'Полка')
