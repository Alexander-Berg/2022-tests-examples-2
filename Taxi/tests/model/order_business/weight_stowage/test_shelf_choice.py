async def test_choice(tap, dataset):
    with tap.plan(9, 'поиск полок для товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')


        parent, *products = await dataset.weight_products()
        tap.eq(len([parent]+products), 4, 'весовые товары созданы')

        order = await dataset.order(
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'count': 23,
                    'weight': 12340,
                }
            ],
            store=store,
            vars={
                'stage': 'stowage'
            }
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        # pylint: disable=protected-access
        shelf = await order.business._shelf_choice(products[0])
        tap.ok(shelf, 'полка для товара найдена')

        stock = await dataset.stock(
            shelf=shelf,
            product=products[1],
            count=10,
            store=store,
        )
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.product_id, products[1].product_id, 'product_id')
        tap.eq(stock.shelf_id, shelf.shelf_id, 'полка')

        tap.eq(
            await order.business._shelf_choice(products[0]),
            None,
            'коллизии найдены. полка не найдена'
        )


async def test_exclude_choice(tap, dataset):
    with tap.plan(6, 'Исключаем полку'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()
        tap.eq(len([parent]+products), 4, 'весовые товары созданы')

        order = await dataset.order(
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'count': 23,
                    'weight': 12340,
                }
            ],
            store=store,
            vars={
                'stage': 'stowage'
            }
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        # pylint: disable=protected-access
        shelf = await order.business._shelf_choice(products[-1])
        tap.ok(shelf, 'полка для товара найдена')

        # pylint: disable=protected-access
        shelf = await order.business._shelf_choice(products[-1],
                                                   exclude=[shelf.shelf_id])
        tap.eq(shelf, None, 'полка для товара не найдена')
