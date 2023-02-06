from stall.model.suggest import Suggest


async def test_begin(tap, dataset):
    with tap.plan(8, 'Срыв заказа'):
        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type='weight_stowage',
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
        tap.eq(order.estatus, 'do_put', 'do_put')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_done(tap, dataset):
    with tap.plan(8, 'Заказ обработан'):
        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            status='canceled',
            estatus='done',
            target='canceled',
            required = [],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'canceled', 'target: canceled')


async def test_suggests_drop(tap, dataset):
    with tap.plan(14, 'Очистка саджестов'):
        parent, *products = await dataset.weight_products()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store)

        order = await dataset.order(
            store=store,
            type = 'weight_stowage',
            status='canceled',
            estatus='suggests_drop',
            target='canceled',
            required = [
                {
                    'product_id': parent.product_id,
                    'count': 1
                },
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'canceled', 'target: canceled')

        suggest1 = await dataset.suggest(
            order,
            type='shelf2box',
            shelf_id=shelf.shelf_id,
            status='done',
            product_id=parent.product_id,
        )
        tap.ok(suggest1, 'Саджест 1')

        suggest2 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf.shelf_id,
            product_id=products[0].product_id,
        )
        tap.ok(suggest2, 'Саджест 2')

        suggest3 = await dataset.suggest(
            order,
            type='shelf2box',
            shelf_id=shelf.shelf_id,
            status='request',
            product_id=parent.product_id,
        )
        tap.ok(suggest3, 'Саджест 3')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'canceled', 'target: canceled')

        tap.eq(len(order.problems), 0, 'Нет проблем')
        tap.eq(len(order.shelves), 0, 'Нет полок')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Список саджестов очищен')


# pylint: disable=too-many-statements,too-many-locals
async def test_put(tap, dataset, wait_order_status):
    with tap.plan(25, 'Тесты весового товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()
        tap.ok(products, 'товар создан')
        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                    'count': 6,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        for i in range(3):
            with tap.subtest(21, 'цикл генерация-закрытие') as taps:
                await wait_order_status(
                    order,
                    ('processing', 'waiting'),
                    tap=taps
                )
                suggests = await dataset.Suggest.list_by_order(
                    order,
                    status='request')
                taps.eq(len(suggests), 1, 'один саджест сгенерирован')
                with suggests[0] as s:
                    taps.eq(s.product_id, parent.product_id, 'product_id')
                    taps.eq(s.type, 'shelf2box', 'type')
                    taps.eq(s.store_id, store.store_id, 'store_id')
                    taps.eq(s.order_id, order.order_id, 'order_id')
                    taps.eq(s.count, 6-2*i, 'count')
                    taps.eq(s.weight, None, 'weight')

                    taps.eq(s.conditions.all, True, 'all')
                    taps.eq(s.conditions.need_weight, True, 'need_weight')
                    taps.eq(
                        s.conditions.weight_aggregate,
                        True,
                        'weight_aggregate'
                    )
                    taps.ok(
                        await s.done(
                            weight=123,
                            count=2,
                            product_id=products[0].product_id
                        ),
                        'закрыт саджест'
                    )
                    tap.eq(
                        s.product_id,
                        products[0].product_id,
                        'product_id поменялся'
                    )

                await wait_order_status(
                    order,
                    ('processing', 'waiting'),
                    tap=taps
                )
                suggests = await dataset.Suggest.list_by_order(
                    order,
                    status='request'
                )
                taps.eq(len(suggests), 1, 'один саджест добавился')
                with suggests[0] as s:
                    taps.eq(s.type, 'box2shelf', 'type')
                    taps.eq(s.product_id, products[0].product_id, 'product_id')
                    taps.eq(s.count, 2, 'count')
                    taps.eq(s.weight, 123, 'weight')
                    taps.ok(
                        await s.done(valid='2011-11-12', weight=123),
                        'закрыт и этот саджест'
                    )

                suggests = await dataset.Suggest.list_by_order(
                    order,
                    status='request'
                )
                taps.eq(len(suggests), 0, 'request саждестов нет')
                taps.eq(
                    order.vars('suggest_mode'),
                    'processing',
                    'suggest_mode'
                )

        tap.ok(await order.cancel(), 'отменяем')
        await wait_order_status(order, ('canceled', 'done'))

        await order.reload()

        tap.eq(order.target, 'canceled', 'target')
        tap.eq(order.status, 'canceled', 'status')
        tap.eq(order.estatus, 'done', 'estatus')
        stocks = [
            s
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
            if s.count
        ]

        tap.eq(len(stocks), 1, 'два стока')
        with [s for s in stocks
              if s.shelf_type != 'found'][0] as s:
            tap.eq(s.store_id, store.store_id, 'store_id')
            tap.eq(s.product_id, products[0].product_id, 'product_id')
            tap.eq(s.count, 6, 'количество')
            tap.eq(s.reserve, 0, 'нет резерва')
            tap.eq(s.valid.strftime('%F'), '2011-11-12', 'valid')
            tap.eq(s.vars['weight'], 3 * 123, 'weight')
