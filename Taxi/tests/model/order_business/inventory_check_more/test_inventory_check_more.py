import pytest


# pylint: disable=too-many-statements,too-many-locals
async def test_inventory(tap, dataset, wait_order_status, cfg):
    with tap.plan(47, 'слепая инвентаризация'):
        cfg.set(
            'business.order.inventory_check_more.upversion_each_check_more',
            True
        )
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        tap.ok(await dataset.shelf(
            store=store,
            type='lost',
        ), 'полка lost')

        tap.ok(await dataset.shelf(
            store=store,
            type='found',
        ), 'полка found')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        stock2 = await dataset.stock(store=store,
                                     shelf_id=stock.shelf_id)
        tap.eq(stock2.shelf_id, stock.shelf_id, 'на той же полке ещё сток')

        order = await dataset.order(
            type='inventory_check_more',
            store=store,
            required=[{'shelf_id': stock.shelf_id}],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))
        version = order.version

        tap.eq(order.shelves, [stock.shelf_id], 'shelves заполнился')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест на полку')

        with suggests[0] as suggest:
            tap.eq(suggest.type, 'check_more', 'тип')
            tap.eq(suggest.shelf_id, stock.shelf_id, 'полка')
            tap.ok(suggest.conditions.all, 'conditions.all')
            tap.ok(not suggest.conditions.editable, 'не редактруемый')

            tap.ok(await suggest.done(product_id=product.product_id, count=20),
                   'саджест закрыт')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'ещё один саджест на полку')
        tap.ok(order.version > version, 'версия увеличилась')
        version = order.version

        request = list(s for s in suggests if s.status == 'request')[0]

        tap.eq(request.type, 'check_more', 'тип')
        tap.eq(request.shelf_id, stock.shelf_id, 'полка')
        tap.ok(request.conditions.all, 'conditions.all')
        tap.ok(not request.conditions.editable, 'не редактруемый')
        tap.ok(await request.done(product_id=stock2.product_id,
                                  count=stock2.count),
               'второй саджест закрыт')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'ещё один саджест на полку')
        tap.ok(order.version > version, 'версия увеличилась')
        request = list(s for s in suggests if s.status == 'request')[0]
        tap.ok(await request.done(status='error'),
               'работу с саджестами завершаем')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'число саджестов не поменялось')

        await wait_order_status(order,
                                ('complete', 'wait_child_done'),
                                user_done=user)
        await wait_order_status(order, ('complete', 'wait_child_done'))

        child = await dataset.Order.load(order.vars('child_order_id'))
        tap.ok(child, 'дочерний ордер создан')
        tap.eq(child.type, 'inventory_check_product_on_shelf', 'тип ордера')
        tap.eq(child.store_id, order.store_id, 'на складе')
        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'ack')
        await wait_order_status(child, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child)
        count = 0
        for s in suggests:
            tap.eq(s.store_id, store.store_id, 'склад в саджесте')
            tap.ok(await s.done(count=20), f'завершаем саджест {s.type}')
            if s.count:
                count += s.count
        tap.ok(count, 'есть саджесты с count')
        suggests = await dataset.Suggest.list_by_order(child)
        await wait_order_status(child, ('complete', 'done'), user_done=user)

        await wait_order_status(order,
                                ('complete', 'done'),
                                user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=[
                ('store_id', child.store_id),
                ('product_id', set(s.product_id for s in suggests)),
                ('shelf_type', 'NOT IN', ('lost', 'found',))
            ],
            sort=(),
        )

        res = {}
        for s in stocks:
            if s.product_id not in res:
                res[s.product_id] = s.count
            else:
                res[s.product_id] += s.count
        tap.eq(res,
               dict((s.product_id, 20) for s in suggests),
               'итого в остатках')


@pytest.mark.parametrize('shelf_type, expected_quants', [
    ('store', 1),
    ('kitchen_components', 66),
])
async def test_inventory_quants(
        tap, dataset, wait_order_status, shelf_type, expected_quants):
    with tap.plan(20, 'слепая инвентаризация кванты'):
        product = await dataset.product(quants=66)
        tap.ok(product, 'товар создан')

        store = await dataset.full_store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        shelf = await dataset.shelf(
            store=store,
            type=shelf_type,
        )

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь связан')

        order = await dataset.order(
            type='inventory_check_more',
            store=store,
            required=[{'shelf_id': shelf.shelf_id}],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(order.shelves, [shelf.shelf_id], 'shelves заполнился')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест на полку')

        with suggests[0] as suggest:
            tap.ok(await suggest.done(product_id=product.product_id, count=20),
                   'саджест закрыт')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        request = list(s for s in suggests if s.status == 'request')[0]
        tap.ok(
            await request.done(status='error'),
            'работу с саджестами завершаем'
        )
        await wait_order_status(
            order,
            ('complete', 'wait_child_done'),
            user_done=user
        )
        child = await dataset.Order.load(order.vars('child_order_id'))
        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'ack')
        await wait_order_status(child, ('processing', 'waiting'))
        await wait_order_status(child, ('complete', 'done'), user_done=user)
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=[
                ('store_id', child.store_id),
                ('product_id', set(s.product_id for s in suggests)),
                (
                    'shelf_type',
                    'NOT IN',
                    ('lost', 'found', 'kitchen_lost', 'kitchen_found')
                )
            ],
            sort=(),
        )
        tap.ok(stocks, 'Есть остатки')
        tap.eq(len(stocks.list), 1, 'Один остаток')
        stock = stocks.list[0]
        tap.eq(stock.quants, expected_quants, 'Ожидаемые кванты в остатке')
