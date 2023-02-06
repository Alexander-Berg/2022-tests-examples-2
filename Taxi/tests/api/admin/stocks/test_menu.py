

async def test_list(tap, dataset, api):
    with tap.plan(5, 'Запрос с выдачей и фильтрами'):
        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.StoreStock.update_kitchen_menu(store, {
            product1.product_id: 10,
            product2.product_id: 20,
        })

        t = await api(user=user)

        await t.post_ok('api_admin_stocks_menu', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('menu')

        menu = t.res['json']['menu']
        tap.eq(len(menu), 2, 'Меню получено')


async def test_list_by_status(tap, dataset, api):
    with tap.plan(6, 'Запрос с выдачей и фильтру по статусу блюда(продукта)'):
        product1 = await dataset.product(status='active')
        product2 = await dataset.product(status='disabled')

        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.StoreStock.update_kitchen_menu(store, {
            product1.product_id: 10,
            product2.product_id: 20,
        })

        t = await api(user=user)

        await t.post_ok('api_admin_stocks_menu', json={'status': 'active'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('menu')

        menu = t.res['json']['menu']
        tap.eq(len(menu), 1, 'Меню получено')
        tap.eq(
            menu[0]['product_id'],
            product1.product_id,
            'Продукт в меню активный',
        )


async def test_empty_menu(tap, dataset, api):
    with tap.plan(5, 'Запрос с выдачей пустого меню'):

        store = await dataset.store()
        user = await dataset.user(store=store)

        t = await api(user=user)

        await t.post_ok('api_admin_stocks_menu', json={'status': 'active'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('menu')

        menu = t.res['json']['menu']
        tap.eq(len(menu), 0, 'Меню нет')
