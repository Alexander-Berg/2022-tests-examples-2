async def test_all_to_store(tap, dataset, wait_order_status, uuid):
    with tap.plan(19, 'кейс: ничего в треш, почти все в дело!'):
        egg = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='repacking')
        shelf_store = await dataset.shelf(store=store)

        stock = await dataset.stock(
            product=egg,
            shelf=shelf,
            count=5,
            lot=uuid(),
        )
        tap.eq(
            (stock.store_id, stock.count, stock.reserve),
            (store.store_id, 5, 0),
            'остаток на 1 полке создан',
        )

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='repacking',
            status='reserving',
            estatus='reserving',
            acks=[user.user_id],
            required=[
                {
                    'product_id': egg.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2box', 'на этапе перефасовки')

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился первый саджест')

        await suggests[0].done(count=0)

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()
        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(order.vars('stage'), 'repacking2box',
               'на этапе возвращения товаров на полку')

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился еще 1 саджест')

        await suggests[0].done(count=3)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'repacking2shelf',
               'на этапе возвращения товаров на полку')

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'еще 1 саджест')

        await suggests[0].done()

        await wait_order_status(order, ('complete', 'begin'), user_done=user)

        await wait_order_status(order, ('complete', 'done'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'не резервов по ордеру')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf_store.shelf_id,
            store_id=store.store_id,
            product_id=egg.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 3, 'положено на полку')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
            product_id=egg.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 2,
               'осталось на первой полке перефасовка')


async def test_all_to_trash(tap, dataset, wait_order_status, uuid):
    with tap.plan(15, 'кейс: все в помойку!'):
        egg = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='repacking')

        stock = await dataset.stock(
            product=egg,
            shelf=shelf,
            count=5,
            lot=uuid(),
        )
        tap.eq(
            (stock.store_id, stock.count, stock.reserve),
            (store.store_id, 5, 0),
            'остаток на 1 полке создан',
        )

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='repacking',
            status='reserving',
            estatus='reserving',
            acks=[user.user_id],
            required=[
                {
                    'product_id': egg.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2box', 'на этапе перефасовки')

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился первый саджест')

        await suggests[0].done(count=5)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2shelf',
               'на этапе перемещения в треш')

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился еще саджест')

        await suggests[0].done()

        await wait_order_status(order, ('complete', 'begin'), user_done=user)

        await wait_order_status(order, ('complete', 'done'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'не резервов по ордеру')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
            product_id=egg.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 0,
               'осталось на первой полке перефасовка')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
            product_id=egg.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 5, 'попало в треш')


async def test_nothing_to_do(tap, dataset, wait_order_status, uuid):
    with tap.plan(16, 'кейс: ничего не хотим делать!'):
        egg = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='repacking')
        shelf_store = await dataset.shelf(store=store)
        tap.eq(shelf_store.store_id, store.store_id, 'создали складскую полку')

        stock = await dataset.stock(
            product=egg,
            shelf=shelf,
            count=5,
            lot=uuid(),
        )
        tap.eq(
            (stock.store_id, stock.count, stock.reserve),
            (store.store_id, 5, 0),
            'остаток на 1 полке создан',
        )

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='repacking',
            status='reserving',
            estatus='reserving',
            acks=[user.user_id],
            required=[
                {
                    'product_id': egg.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2box', 'на этапе перефасовки')

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился первый саджест')

        await suggests[0].done(count=0)

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()
        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(order.vars('stage'), 'repacking2box',
               'на этапе возвращения товаров на полку')

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился еще 1 саджест')

        await suggests[0].done(count=0)

        await wait_order_status(order, ('complete', 'begin'), user_done=user)

        await wait_order_status(order, ('complete', 'done'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'не резервов по ордеру')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
            product_id=egg.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 5,
               'осталось на полке перефасовка')
