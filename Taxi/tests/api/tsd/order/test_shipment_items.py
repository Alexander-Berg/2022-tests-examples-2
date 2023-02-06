from datetime import timedelta


async def test_items(tap, dataset, api, uuid, now, wait_order_status):
    with tap.plan(29, 'создание/выполнение ордера отгрузки'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')


        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(
            store=store,
            data={
                'expiry_date': now().strftime('%F'),
            },
        )
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')
        tap.ok(item.data('expiry_date'), 'expiry_date есть')

        stock = await dataset.stock(store=store, item=item)
        tap.eq(
            (stock.store_id, stock.product_id),
            (store.store_id, item.item_id),
            'экземпляр на складе'
        )

        item_no_stock = await dataset.item(store=store)
        tap.eq(item_no_stock.store_id, store.store_id, 'ещё экземпляр')
        tap.eq(
            item_no_stock.status,
            'active',
            'активен но сток создавать не будем'
        )

        external_id = uuid()

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_shipment_items',
            json={
                'external_id': external_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order created')

        order = await dataset.Order.load(
            [store.store_id, external_id],
            by='external'
        )
        tap.ok(order, 'ордер загружен')
        tap.eq(order.type, 'shipment', 'тип')
        tap.eq(order.source, 'tsd', 'Источник правильный')
        tap.eq(len(order.required), 1, 'один элемент required')
        tap.eq(order.required[0].item_id, item.item_id, 'экземпляр')
        tap.eq(order.company_id, user.company_id, 'идентификатор компании')

        await wait_order_status(order, ('request', 'waiting'))
        tap.ok(await order.ack(user), 'ack')
        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.ok(await item.reload(), 'перегружен')
        tap.eq(item.status, 'inactive', 'экземпляр неактивен')


        await t.post_ok(
            'api_tsd_order_shipment_items',
            json={
                'external_id': external_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order has already created')

        await t.post_ok(
            'api_tsd_order_shipment_items',
            json={
                'external_id': uuid(),
            },
            desc='Повторный запрос с другим external_id',
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_NO_ITEMS_EXPIRED')



async def test_items_errors(tap, dataset, api, uuid, now):
    with tap.plan(18, 'ошибки при запросе ручки'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')


        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_shipment_items',
            json={
                'external_id': uuid(),
            }
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_NO_ITEMS_EXPIRED')
        t.json_is('message', 'There is no item expired')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        stock = await dataset.stock(store=store, item=item)
        tap.eq(
            (stock.store_id, stock.product_id),
            (store.store_id, item.item_id),
            'экземпляр на складе'
        )

        await t.post_ok(
            'api_tsd_order_shipment_items',
            json={
                'external_id': uuid(),
            }
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_NO_ITEMS_EXPIRED')
        t.json_is('message', 'There is no item expired')

        item.data['expiry_date'] = (now() + timedelta(days=3)).strftime('%F')
        tap.ok(await item.save(), 'сохранено expiry_date')
        tap.ok(item.data('expiry_date'), 'expiry_date есть')

        await t.post_ok(
            'api_tsd_order_shipment_items',
            json={
                'external_id': uuid(),
            }
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_NO_ITEMS_EXPIRED')
        t.json_is('message', 'There is no item expired')


# pylint: disable=too-many-locals
async def test_mutli_items(tap, dataset, api, uuid, now, wait_order_status):
    with tap.plan(25, 'создание/выполнение ордера отгрузки'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')


        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(
            store=store,
            data={
                'expiry_date': now().strftime('%F'),
            },
        )
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')
        tap.ok(item.data('expiry_date'), 'expiry_date есть')

        stock = await dataset.stock(store=store, item=item)
        tap.eq(
            (stock.store_id, stock.product_id),
            (store.store_id, item.item_id),
            'экземпляр на складе'
        )

        item_no_stock = await dataset.item(store=store)
        tap.eq(item_no_stock.store_id, store.store_id, 'ещё экземпляр')
        tap.eq(
            item_no_stock.status,
            'active',
            'активен но сток создавать не будем'
        )



        item2 = await dataset.item(
            store=store,
            data={
                'expiry_date': now().strftime('%F'),
            },
        )
        tap.eq(item2.store_id, store.store_id, 'экземпляр создан')
        tap.ok(item2.data('expiry_date'), 'expiry_date есть')

        stock2 = await dataset.stock(store=store, item=item2)
        tap.eq(
            (stock2.store_id, stock2.product_id),
            (store.store_id, item2.item_id),
            'экземпляр на складе'
        )

        external_id = uuid()

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_shipment_items',
            json={
                'external_id': external_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order created')

        order = await dataset.Order.load(
            [store.store_id, external_id],
            by='external'
        )
        tap.ok(order, 'ордер загружен')
        tap.eq(order.type, 'shipment', 'тип')
        tap.eq(len(order.required), 2, 'два элемента required')
        tap.eq(
            {
                order.required[0].item_id,
                order.required[1].item_id
            },
            {
                item.item_id,
                item2.item_id,
            },
            'экземпляры'
        )

        await wait_order_status(order, ('request', 'waiting'))
        tap.ok(await order.ack(user), 'ack')
        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.ok(await item.reload(), 'перегружен экземпляр 1')
        tap.eq(item.status, 'inactive', 'экземпляр неактивен')

        tap.ok(await item2.reload(), 'перегружен экземпляр 2')
        tap.eq(item2.status, 'inactive', 'экземпляр неактивен')
