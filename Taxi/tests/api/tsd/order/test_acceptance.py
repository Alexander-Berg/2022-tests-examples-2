async def test_normal(tap, dataset, api, uuid):
    with tap.plan(15, 'обычный воркфлоу'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь')
        tap.eq(user.role, 'executer', 'роль')
        tap.ok(user.company_id, 'компания у пользователя')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_acceptance',
            json={
                'external_id': external_id,
                'required': [
                    {'item_id': item.item_id},
                    {'product_id': product.product_id, 'count': 27},
                ]
            }
        )
        t.status_is(200, diag=True)

        order = await dataset.Order.load(
            [user.store_id, external_id],
            by='external'
        )
        tap.ok(order, 'ордер создан')
        tap.eq(len(order.required), 2, 'две опции required')
        tap.eq(order.required[0].item_id, item.item_id, 'item_id')
        tap.eq(order.required[1].product_id, product.product_id, 'product_id')
        tap.eq(order.required[1].count, 27, 'count')
        tap.eq(order.company_id, user.company_id, 'компания')
        tap.eq(order.source, 'tsd', 'Правильный источник')


async def test_order_double(tap, dataset, api, uuid):
    with tap.plan(11, 'Есть дубли ордеров'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь')
        tap.eq(user.role, 'executer', 'роль')

        dup = await dataset.order(
            store=store,
            type='acceptance',
            required=[{'item_id': item.item_id, 'count': 1}],
        )
        tap.ok(dup, 'дубль есть')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_acceptance',
            json={
                'external_id': external_id,
                'required': [
                    {'item_id': item.item_id},
                    {'product_id': product.product_id, 'count': 27},
                ]
            }
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('details.list.0.item_id', item.item_id)
        t.json_is('details.list.0.message', 'Order with item_id exists')

async def test_error(tap, dataset, api, uuid):
    with tap.plan(7, 'Есть дубли ордеров'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь')
        tap.eq(user.role, 'executer', 'роль')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_acceptance',
            json={
                'external_id': external_id,
                'required': [
                    {'item_id': uuid()},
                    {'product_id': uuid(), 'count': 27},
                ]
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_has('details.list.1.message')


async def test_order_double_stock(tap, dataset, api, uuid):
    with tap.plan(11, 'Есть дубли остатков'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь')
        tap.eq(user.role, 'executer', 'роль')


        stock = await dataset.stock(
            item=item,
            store=store,
            count=1
        )
        tap.eq(stock.store_id, store.store_id, 'экземпляр создан')
        tap.eq(stock.product_id, item.item_id, 'product_id')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_acceptance',
            json={
                'external_id': external_id,
                'required': [
                    {'item_id': item.item_id},
                    {'product_id': product.product_id, 'count': 27},
                ]
            }
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('details.list.0.item_id', item.item_id)
