from datetime import date

from libstall.util import now


async def test_unreserve(tap, dataset, wait_order_status):
    with tap.plan(24, 'Резервирование товара'):

        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)
        await dataset.shelf(store=store, type='incoming')

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )
        tap.ok('dont_trust' not in order.vars,
               'не делаем вывод о типе приемки')
        tap.ok('has_weight_products' not in order.vars,
               'нет весового товара')

        # Еще продукт
        await dataset.suggest(
            order,
            status='done',
            type='check',
            product_id=product2.product_id,
            result_count=4,
            result_valid=date(2020, 4, 3),
        )

        await wait_order_status(
            order,
            ('complete', 'result_update'),
            user_done=user,
        )

        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'result_update', 'result_update')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'stowage_prepare', 'сабстатус')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        with order.required[0] as require:
            tap.eq(require.product_id, product1.product_id, 'Продукт')
            tap.eq(require.count, 1, 'Количество не менялось')
            tap.eq(require.result_count, 1, 'Результат количества добавлен')
            tap.eq(require.valid, None, 'СГ не менялось')
            tap.eq(require.result_valid, None, 'Результат СГ не менялось')

        with order.required[1] as require:
            tap.eq(require.product_id, product2.product_id, 'Продукт')
            tap.eq(require.count, 0, 'Изначально не было')
            tap.eq(require.result_count, 4, 'Результат количества добавлен')
            tap.eq(require.valid, None, 'Изначально не было')
            tap.eq(require.result_valid, date(2020, 4, 3), 'Результат СГ')
