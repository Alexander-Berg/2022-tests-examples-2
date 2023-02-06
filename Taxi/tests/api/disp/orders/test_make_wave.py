async def test_wave_noorders(tap, dataset, api):
    with tap.plan(5):
        user = await dataset.user()
        tap.ok(user, 'пользователь создан')

        t = await api(user=user)
        await t.post_ok('api_disp_orders_make_wave',
                        json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('count', 0)


async def test_wave_orders_noresult(tap, dataset, api):
    with tap.plan(7):
        user = await dataset.user()
        tap.ok(user, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store_id=user.store_id,
            type='collect',
            required=[{'product_id': product.product_id, 'count': 12}],
        )
        tap.eq(order.store_id, user.store_id, 'ордер создан')

        t = await api(user=user)
        await t.post_ok('api_disp_orders_make_wave',
                        json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('count', 0)

async def test_wave_orders(tap, dataset, api, wait_order_status):
    with tap.plan(21):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        stock2 = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        order = await dataset.order(
            store=store,
            type='collect',
            required=[{'product_id': stock.product_id, 'count': 10}],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting_stocks'))

        order2 = await dataset.order(
            store=store,
            type='collect',
            required=[{'product_id': stock2.product_id, 'count': 11}],
        )
        tap.eq(order2.store_id, store.store_id, 'ордер 2 создан')
        shelf2 = await dataset.shelf(type='collection', store=store)
        tap.eq(shelf2.store_id, store.store_id, 'полка создана')
        await wait_order_status(order2, ('processing', 'waiting_stocks'))

        t = await api(user=user)


        await t.post_ok('api_disp_orders_make_wave',
                        json={'limit': 1},
                        desc='Создаём первый ордер')

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('count', 1)


        await t.post_ok('api_disp_orders_make_wave',
                        json={},
                        desc='Создаём второй ордер')

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('count', 1)


        await t.post_ok('api_disp_orders_make_wave',
                        json={},
                        desc='Больше не получается')

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('count', 0)
