async def test_move_markdown(tap, api, dataset, uuid):
    with tap.plan(10, 'перемещение на полку скидок НЕДОСТУПНО'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        markdown = await dataset.shelf(store=store, type='markdown')
        tap.eq(markdown.store_id, store.store_id, 'полка скидок')
        tap.eq(markdown.type, 'markdown', 'тип')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        t = await api(user=user)

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': uuid(),
                            'move': [
                                {
                                    'product_id': stock.product_id,
                                    'count': 1,
                                    'src_shelf_id': stock.shelf_id,
                                    'dst_shelf_id': markdown.shelf_id,
                                }
                            ]
                        })
        t.status_is(400, diag=True)

        admin = await dataset.user(store=store, role='admin')
        tap.eq(admin.store_id, store.store_id, 'админ создан')

        t = await api(user=admin)

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': uuid(),
                            'move': [
                                {
                                    'product_id': stock.product_id,
                                    'count': 1,
                                    'src_shelf_id': stock.shelf_id,
                                    'dst_shelf_id': markdown.shelf_id,
                                }
                            ]
                        })
        t.status_is(200, diag=True)


async def test_move_markdown2markdown(tap, api, dataset, uuid):
    with tap.plan(7, 'С распродажи на распродажу!'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='store_admin')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        markdown = await dataset.shelf(store=store, type='markdown')
        tap.eq(markdown.store_id, store.store_id, 'полка скидок')
        tap.eq(markdown.type, 'markdown', 'тип')

        stock = await dataset.stock(store=store, shelf_type='markdown')
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        t = await api(user=user)

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': uuid(),
                            'move': [
                                {
                                    'product_id': stock.product_id,
                                    'count': 1,
                                    'src_shelf_id': stock.shelf_id,
                                    'dst_shelf_id': markdown.shelf_id,
                                }
                            ]
                        })
        t.status_is(200, diag=True)
