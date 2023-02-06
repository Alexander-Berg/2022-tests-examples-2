# pylint: disable=unused-variable

async def test_like_shelf(tap, dataset, wait_order_status):
    with tap.plan(19, 'Тесты успешного like_shelf в весовой раскладке'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()
        tap.eq(len(products), 3, 'весовые товары созданы')

        shelf = await dataset.shelf(store=store)
        tap.ok(shelf, 'Полка создана')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.ok(
                await s.done(
                    weight=500,
                    count=1,
                ),
                'закрыт саджест'
            )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )
        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'один саджест добавился')
        new_shelf = await dataset.shelf(store=store)
        tap.ok(new_shelf, 'Полка создана')

        with suggests[0] as s:
            tap.ne(s.shelf_id, new_shelf.shelf_id, 'не созданная полка')
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': new_shelf.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'все еще один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, new_shelf.shelf_id, 'полка изменилась')
            tap.eq(s.status, 'request', 'статус')


async def test_with_same_product(tap, dataset, wait_order_status):
    with tap.plan(22,
                  'Тесты like_shelf на полку где такой же ребенок вес товар'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()
        tap.eq(len(products), 3, 'весовые товары созданы')

        shelf = await dataset.shelf(store=store)
        tap.ok(shelf, 'Полка создана')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.ok(
                await s.done(
                    weight=500,
                    count=1,
                ),
                'закрыт саджест'
            )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )
        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'один саджест добавился')
        new_shelf = await dataset.shelf(store=store)
        tap.ok(new_shelf, 'Полка создана')

        stock1 = await dataset.stock(
            store=store,
            order=order,
            shelf=new_shelf,
            product=products[2],
        )
        tap.ok(stock1, 'сток создан')
        tap.eq(stock1.shelf_id, new_shelf.shelf_id, 'сток на новой полке')
        tap.eq(stock1.product_id,
               products[2].product_id,
               'весовой товар как на раскладке'
               )

        old_shelf_id = None
        with suggests[0] as s:
            tap.ne(s.shelf_id, new_shelf.shelf_id, 'не созданная полка')
            old_shelf_id = s.shelf_id
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': new_shelf.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'все еще один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, new_shelf.shelf_id, 'полка новая')
            tap.eq(s.status, 'request', 'статус')


async def test_not_empty_shelf(tap, dataset, wait_order_status):
    with tap.plan(23,
                  'Тесты like_shelf на полку где другой ребенок вес товар'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()
        tap.eq(len(products), 3, 'весовые товары созданы')

        shelf = await dataset.shelf(store=store)
        tap.ok(shelf, 'Полка создана')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.ok(
                await s.done(
                    weight=500,
                    count=1,
                ),
                'закрыт саджест'
            )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )
        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'один саджест добавился')
        new_shelf = await dataset.shelf(store=store)
        tap.ok(new_shelf, 'Полка создана')

        stock1 = await dataset.stock(
            store=store,
            order=order,
            shelf=new_shelf,
            product=products[0],
        )
        tap.ok(stock1, 'сток создан')
        tap.eq(stock1.shelf_id, new_shelf.shelf_id, 'сток на новой полке')
        tap.eq(stock1.product_id, products[0].product_id, 'весовой товар')

        with suggests[0] as s:
            tap.ne(s.shelf_id, new_shelf.shelf_id, 'не созданная полка')
            old_shelf_id = s.shelf_id
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': new_shelf.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'все еще один саджест')
        with suggests[0] as s:
            tap.ne(s.shelf_id, new_shelf.shelf_id, 'полка не новая')
            tap.eq(s.shelf_id, old_shelf_id, 'полка старая')
            tap.eq(s.status, 'request', 'статус')


async def test_shelf_from_another_suggest(tap, dataset, wait_order_status):
    with tap.plan(21,
                  'Тесты like_shelf если есть саджест с другим ребенком '
                  'вес товар на ту же полку'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()
        tap.eq(len(products), 3, 'весовые товары созданы')

        shelf = await dataset.shelf(store=store)
        tap.ok(shelf, 'Полка создана')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.ok(
                await s.done(
                    weight=500,
                    count=1,
                ),
                'закрыт саджест'
            )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )
        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'один саджест добавился')
        new_shelf = await dataset.shelf(store=store)
        tap.ok(new_shelf, 'Полка создана')

        suggest_on_shelf = await dataset.suggest(
            order,
            type='box2shelf',
            status='done',
            shelf_id=new_shelf.shelf_id,
            product_id=products[0].product_id,
        )
        tap.ok(suggest_on_shelf, 'Саджест на новую полку и другой ребенок')

        with suggests[0] as s:
            tap.ne(s.shelf_id, new_shelf.shelf_id, 'не созданная полка')
            old_shelf_id = s.shelf_id
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': new_shelf.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'все еще один саджест')
        with suggests[0] as s:
            tap.ne(s.shelf_id, new_shelf.shelf_id, 'полка не новая')
            tap.eq(s.shelf_id, old_shelf_id, 'полка старая')
            tap.eq(s.status, 'request', 'статус')


async def test_shelf_from_suggest(tap, dataset, wait_order_status):
    with tap.plan(20,
                  'Тесты like_shelf если есть саджест с тем же ребенком '
                  'вес товар на ту же полку'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()
        tap.eq(len(products), 3, 'весовые товары созданы')

        shelf = await dataset.shelf(store=store)
        tap.ok(shelf, 'Полка создана')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.ok(
                await s.done(
                    weight=500,
                    count=1,
                ),
                'закрыт саджест'
            )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )
        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'один саджест добавился')
        new_shelf = await dataset.shelf(store=store)
        tap.ok(new_shelf, 'Полка создана')

        suggest_on_shelf = await dataset.suggest(
            order,
            type='box2shelf',
            status='done',
            shelf_id=new_shelf.shelf_id,
            product_id=products[2].product_id,
        )
        tap.ok(suggest_on_shelf, 'Саджест на новую полку и такой же ребенок')

        with suggests[0] as s:
            tap.ne(s.shelf_id, new_shelf.shelf_id, 'не созданная полка')
            old_shelf_id = s.shelf_id
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': new_shelf.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'все еще один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, new_shelf.shelf_id, 'полка новая')
            tap.eq(s.status, 'request', 'статус')


async def test_shelf_to_trash(tap, dataset, wait_order_status):
    with tap.plan(17,
                  'Тесты like_shelf на треш'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()
        tap.eq(len(products), 3, 'весовые товары созданы')

        shelf = await dataset.shelf(store=store)
        tap.ok(shelf, 'Полка создана')

        trash = await dataset.shelf(store=store, type='trash')
        tap.ok(shelf, 'Полка создана')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.ok(
                await s.done(
                    weight=500,
                    count=1,
                ),
                'закрыт саджест'
            )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )
        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'один саджест добавился')

        with suggests[0] as s:
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': trash.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'все еще один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, trash.shelf_id, 'полка trash')
            tap.eq(s.status, 'request', 'статус')
