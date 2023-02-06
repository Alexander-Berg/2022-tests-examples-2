# pylint: disable=too-many-statements
async def test_one_shelf(tap, dataset, wait_order_status, uuid):
    with tap.plan(30, 'перетасовка яиц'):
        egg = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='repacking')
        shelf_store = await dataset.shelf(store=store)

        stock1 = await dataset.stock(
            product=egg,
            shelf=shelf,
            count=15,
            valid='2018-05-10',
            lot=uuid(),
        )
        tap.eq(
            (stock1.store_id, stock1.count, stock1.reserve),
            (store.store_id, 15, 0),
            'первый остаток создан',
        )

        stock2 = await dataset.stock(
            product=egg,
            shelf=shelf,
            count=15,
            valid='2018-05-08',
            lot=uuid(),
        )
        tap.eq(
            (stock2.store_id, stock2.count, stock2.reserve),
            (store.store_id, 15, 0),
            'второй остаток создан',
        )

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='repacking',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            required=[
                {
                    'product_id': egg.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')
        tap.eq(
            order.required[0].product_id,
            egg.product_id,
            'яйца на перефасовку',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2box', 'на этапе перефасовки')

        suggests = {
            s.type: s
            for s in await dataset.Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 1, 'появился 1 саджест')
        tap.eq(
            (
                suggests['shelf2box'].product_id,
                suggests['shelf2box'].shelf_id,
                suggests['shelf2box'].count,
            ),
            (
                egg.product_id,
                shelf.shelf_id,
                30,
            ),
            'непригодные после перефасовки товары в корзину',
        )

        await suggests['shelf2box'].done(count=10)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2shelf',
               'на этапе перемещения в треш')

        suggests = {
            s.type: s
            for s in await dataset.Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 2, 'появился второй саджест')
        tap.eq(
            (
                suggests['box2shelf'].product_id,
                suggests['box2shelf'].shelf_id,
                suggests['box2shelf'].count,
            ),
            (
                egg.product_id,
                trash.shelf_id,
                10,
            ),
            'выкинуть непригодные после перефасовки товары',
        )

        await suggests['box2shelf'].done()

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'repacking2box',
               'на этапе возвращения товаров на полку')

        suggests = {
            s.vars('stage'): s
            for s in await dataset.Suggest.list_by_order(order)
        }
        tap.eq(len(suggests), 3, 'появился третий саджест')
        tap.eq(
            (
                suggests['repacking2box'].product_id,
                suggests['repacking2box'].shelf_id,
                suggests['repacking2box'].status,
                suggests['repacking2box'].count,
            ),
            (
                egg.product_id,
                shelf.shelf_id,
                'request',
                20,
            ),
            'полученные после перефасовки товары на полку',
        )

        await suggests['repacking2box'].done(count=14)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'repacking2shelf',
               'на этапе возвращения товаров на полку')

        suggests = {
            s.vars('stage'): s
            for s in await dataset.Suggest.list_by_order(order)
        }
        tap.eq(len(suggests), 4, 'появился четвертый саджест')
        tap.eq(
            (
                suggests['repacking2shelf'].product_id,
                suggests['repacking2shelf'].shelf_id,
                suggests['repacking2shelf'].status,
                suggests['repacking2shelf'].count,
            ),
            (
                egg.product_id,
                shelf_store.shelf_id,
                'request',
                14,
            ),
            'полученные после перефасовки товары на полку',
        )

        await suggests['repacking2shelf'].done()

        await wait_order_status(order, ('complete', 'begin'), user_done=user)

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 2, 'резервов по ордеру')

        await wait_order_status(order, ('complete', 'done'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'не резервов по ордеру')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf_store.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(sum(s.count for s in stocks), 14, 'положено на полку')
        tap.eq(stocks[0].valid, stock2.valid, 'срок годнисти наименьший')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(sum(s.count for s in stocks), 6,
               'осталось на полке перефасовка')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(sum(s.count for s in stocks), 10, 'попало в треш')


# pylint: disable-msg=too-many-locals
async def test_two_shelves(tap, dataset, wait_order_status, uuid):
    with tap.plan(25, 'перефасовка на 2 полках'):
        egg = await dataset.product()

        store = await dataset.store()
        shelf1 = await dataset.shelf(store=store, type='repacking')
        shelf2 = await dataset.shelf(store=store, type='repacking')
        shelf_store = await dataset.shelf(store=store)

        stock1 = await dataset.stock(
            product=egg,
            shelf=shelf1,
            count=5,
            lot=uuid(),
            valid='2018-05-10',
        )
        tap.eq(
            (stock1.store_id, stock1.count, stock1.reserve),
            (store.store_id, 5, 0),
            'остаток на 1 полке создан',
        )

        stock2 = await dataset.stock(
            product=egg,
            shelf=shelf2,
            count=6,
            lot=uuid(),
            valid='2018-05-08',
        )
        tap.eq(
            (stock2.store_id, stock2.count, stock2.reserve),
            (store.store_id, 6, 0),
            'остаток на 2 полке создан',
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
                    'shelf_id': shelf1.shelf_id,
                },
                {
                    'product_id': egg.product_id,
                    'shelf_id': shelf2.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2box', 'на этапе перефасовки')

        suggests = {
            s.shelf_id: s for s in await
            dataset.Suggest.list_by_order(order, status='request')
        }

        tap.eq(len(suggests), 2, 'появилося 2 саджеста')

        await suggests[shelf1.shelf_id].done(count=2)
        await suggests[shelf2.shelf_id].done(count=2)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2shelf',
               'на этапе перемещения в треш')

        suggests = {
            s.vars('shelf_id'): s for s in await
            dataset.Suggest.list_by_order(order,  status='request')
        }

        tap.eq(len(suggests), 2, 'появилося еще 2 саджеста')

        await suggests[shelf1.shelf_id].done()
        await suggests[shelf2.shelf_id].done()

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'repacking2box',
               'на этапе возвращения товаров на полку')

        suggests = {
            s.shelf_id: s for s in await
            dataset.Suggest.list_by_order(order, status='request')
        }
        tap.eq(len(suggests), 2, 'еще раз появилось 2 саджеста')

        await suggests[shelf1.shelf_id].done(count=1)
        await suggests[shelf2.shelf_id].done(count=3)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'repacking2shelf',
               'на этапе возвращения товаров на полку')

        suggests = {
            s.vars('shelf_id'): s for s in await
            dataset.Suggest.list_by_order(order, status='request')
        }
        tap.eq(len(suggests), 2, 'вау, появилось еще 2 саджеста')

        await suggests[shelf1.shelf_id].done()
        await suggests[shelf2.shelf_id].done()

        await wait_order_status(order, ('complete', 'begin'), user_done=user)

        await wait_order_status(order, ('complete', 'done'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'не резервов по ордеру')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf_store.shelf_id,
            store_id=store.store_id,
            product_id=egg.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 1 + 3, 'положено на полку')
        tap.eq(stocks[0].valid, stock2.valid, 'срок годнисти наименьший')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf1.shelf_id,
            store_id=store.store_id,
            product_id=egg.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 5 - 2 - 1,
               'осталось на первой полке перефасовка')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf2.shelf_id,
            store_id=store.store_id,
            product_id=egg.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 6 - 2 - 3,
               'осталось на второй полке перефасовка')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
            product_id=egg.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 2 + 2, 'попало в треш')


async def test_two_products(tap, dataset, wait_order_status):
    with tap.plan(26, 'перефасовка 2 продуктов (на будущее)'):
        egg1 = await dataset.product()
        egg2 = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='repacking')
        shelf_store = await dataset.shelf(store=store)

        stock1 = await dataset.stock(
            product=egg1,
            shelf=shelf,
            count=10,
        )
        tap.eq(
            (stock1.store_id, stock1.count, stock1.reserve),
            (store.store_id, 10, 0),
            'первый остаток создан',
        )

        stock2 = await dataset.stock(
            product=egg2,
            shelf=shelf,
            count=15,
        )
        tap.eq(
            (stock2.store_id, stock2.count, stock2.reserve),
            (store.store_id, 15, 0),
            'второй остаток создан',
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
                    'product_id': egg1.product_id,
                    'shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': egg2.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2box', 'на этапе перефасовки')

        suggests = {
            s.product_id: s
            for s in await dataset.Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 2, 'появилося 2 саджеста')

        await suggests[egg1.product_id].done(count=7)
        await suggests[egg2.product_id].done(count=8)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash2shelf',
               'на этапе перемещения в треш')

        suggests = {
            s.product_id: s for s in await
            dataset.Suggest.list_by_order(order, status='request')
        }

        tap.eq(len(suggests), 2, 'появилося еще 2 саджеста')

        await suggests[egg1.product_id].done()
        await suggests[egg2.product_id].done()

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'repacking2box',
               'на этапе возвращения товаров на полку')

        suggests = {
            s.product_id: s for s in await
            dataset.Suggest.list_by_order(order, status='request')
        }
        tap.eq(len(suggests), 2, 'еще раз появилось 2 саджеста')

        await suggests[egg1.product_id].done(count=2)
        await suggests[egg2.product_id].done(count=4)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'repacking2shelf',
               'на этапе возвращения товаров на полку')

        suggests = {
            s.product_id: s for s in await
            dataset.Suggest.list_by_order(order, status='request')
        }
        tap.eq(len(suggests), 2, 'вау, появилось еще 2 саджеста')

        await suggests[egg1.product_id].done()
        await suggests[egg2.product_id].done()

        await wait_order_status(order, ('complete', 'begin'), user_done=user)

        await wait_order_status(order, ('complete', 'done'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'не резервов по ордеру')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf_store.shelf_id,
            store_id=store.store_id,
            product_id=egg1.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 2, 'положено на полку')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
            product_id=egg1.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 10 - 7 - 2,
               'осталось на полке перефасовка')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
            product_id=egg1.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 7, 'попало в треш')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf_store.shelf_id,
            store_id=store.store_id,
            product_id=egg2.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 15 - 8 - 3, 'положено на полку')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
            product_id=egg2.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 3,
               'осталось на полке перефасовка')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
            product_id=egg2.product_id,
        )
        tap.eq(sum(s.count for s in stocks), 8, 'попало в треш')
