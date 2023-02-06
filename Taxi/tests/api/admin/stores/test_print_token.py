async def test_print_token_access(tap, dataset, api, uuid):
    with tap.plan(10):
        t = await api(role='executer')

        store = await dataset.store()
        tap.ok(store, 'тестовый склад создан')
        tap.ok(store.print_id, 'идентификатор принтера у него есть')

        await t.post_ok('api_admin_stores_printer_token_load',
                        json={'store_id': store.store_id})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


        await t.post_ok('api_admin_stores_printer_token_load',
                        json={'store_id': uuid()})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')



async def test_print_token(tap, dataset, api):
    with tap.plan(6):
        t = await api(role='admin')

        store = await dataset.store()
        tap.ok(store, 'тестовый склад создан')
        tap.ok(store.print_id, 'идентификатор принтера у него есть')

        await t.post_ok('api_admin_stores_printer_token_load',
                        json={'store_id': store.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('printer_token', store.printer_token, 'значение токена')



async def test_print_token_change(tap, dataset, api):
    with tap.plan(7):
        t = await api(role='admin')

        store = await dataset.store()
        tap.ok(store, 'тестовый склад создан')
        tap.ok(store.print_id, 'идентификатор принтера у него есть')

        await t.post_ok('api_admin_stores_printer_token_change',
                        json={'store_id': store.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('printer_token', 'значение токена есть')
        t.json_isnt('printer_token',
                    store.printer_token,
                    'значение токена изменилось')


