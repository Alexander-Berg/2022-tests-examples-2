async def test_create(tap, dataset, uuid, api):
    with tap.plan(13, 'Апрув командой create'):
        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 123,
                                }
                            ],
                            'store_id': store.store_id
                        },
                        desc='Запрос на создание')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')


        order = await dataset.Order.load(
            (store.store_id, external_id),
            by='external'
        )
        tap.ok(order, 'ордер загружен')
        tap.eq(order.approved, None, 'не апрувлен')
        tap.eq(order.status, 'reserving', 'статус')

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 123,
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                        },
                        desc='Запрос на создание + апрув')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')

        order = await dataset.Order.load(
            (store.store_id, external_id),
            by='external'
        )
        tap.ok(order, 'ордер загружен')
        tap.ne(order.approved, None, 'апрувлен')
        tap.eq(order.status, 'reserving', 'статус')
