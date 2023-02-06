async def test_log(tap, dataset, api):
    with tap.plan(12, 'Запрос за логами стока'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        admin = await dataset.user(store=store)
        tap.eq(admin.store_id, store.store_id, 'Админ создан')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'Остаток на складе создан')

        t = await api(user=admin)

        await t.post_ok('api_admin_stocks_log',
                        json={'stock_id': stock.stock_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('stocks_log.0.stock_id', stock.stock_id)

        t.json_has('stocks_log.0.log_id')
        t.json_has('stocks_log.0.order_id')
        t.json_has('stocks_log.0.order_type')

        t.json_hasnt('stocks_log.1')


async def test_over_permit_out_store(tap, api, dataset):
    with tap.plan(3, 'Чужая лавка'):
        company = await dataset.company()
        store1 = await dataset.store(company=company)
        store2 = await dataset.store(company=company)
        stock = await dataset.stock(store=store1)

        user = await dataset.user(role='admin', store=store2)
        t = await api(user=user)
        with user.role as role:
            role.remove_permit('out_of_store')

            await t.post_ok('api_admin_stocks_log',
                            json={'stock_id': stock.stock_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_over_permit_out_company(tap, api, dataset):
    with tap.plan(3, 'Чужая компания'):
        store1 = await dataset.store()
        store2 = await dataset.store()

        user = await dataset.user(role='admin', company=store1)
        stock = await dataset.stock(store=store2)

        t = await api(user=user)
        await t.post_ok('api_admin_stocks_log',
                        json={'stock_id': stock.stock_id})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
