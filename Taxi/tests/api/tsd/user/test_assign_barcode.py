async def test_assign_barcode(tap, api, dataset, uuid):
    with tap.plan(23, 'Тест обращения к barcode от ранее логинившегося'):
        product = await dataset.product(
            barcode=[uuid()],
            products_scope=['russia'],
        )
        tap.ok(product, 'товар создан')

        company = await dataset.company(products_scope=['russia'])
        store   = await dataset.store(company=company)
        user    = await dataset.user(store=store, role='executer')
        tap.ok(user, 'пользователь создан')

        token = user.token()

        t = await api(spec=('doc/api/tsd/user.yaml', 'doc/api/tsd.yaml'))

        t.set_token(token)
        await t.post_ok('api_tsd_barcode',
                        json={'barcode': product.barcode[0]},
                        desc='barcode от залогиненного')
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'product')
        t.json_is('found.0.product_id', product.product_id)

        t.set_token(None)
        await t.post_ok('api_tsd_barcode',
                        json={'barcode': product.barcode[0]},
                        desc='barcode от незалогиненного')
        t.status_is(401, diag=True)

        device = uuid()
        await t.post_ok('api_tsd_user_assign_device',
                        json={
                            'device': device,
                            'barcode': user.qrcode
                        },
                        desc='Пользователь логинится')
        t.status_is(200, diag=True)
        tap.ok(await user.reload(), 'пользователь перегружен')
        tap.eq(user.device, [device], 'device у него поменялся')
        tap.ne(user.token(), token, 'токен изменился')

        t.set_token(user.token())
        await t.post_ok('api_tsd_barcode',
                        json={'barcode': product.barcode[0]},
                        desc='barcode от залогиненного')
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'product')
        t.json_is('found.0.product_id', product.product_id)

        t.set_token(token)
        await t.post_ok('api_tsd_barcode',
                        json={'barcode': product.barcode[0]},
                        desc='barcode от залогиненного ранее')
        t.status_is(401, diag=True)
