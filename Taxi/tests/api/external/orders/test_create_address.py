async def test_create(tap, dataset, api, uuid, now):
    with tap.plan(12, 'Заполнение delivery_promise и client_address'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')


        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 123,
                                }
                            ],
                            'store_id': store.store_id,
                            'client_address': {
                                'fullname': 'Москва, Льва Толстого, 16',
                                'lat': 55.733969,
                                'lon': 37.587093,
                            },
                            'delivery_promise': 123,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        order = await dataset.Order.load(
            [store.store_id, external_id],
            by='external'
        )
        tap.ok(order, 'ордер загружен')
        tap.ok(order.delivery_promise, 'delivery_promise установлен')
        tap.ok(
            order.delivery_promise.timestamp() > now().timestamp() + 110 * 60,
            'значение delivery_promise'
        )

        tap.ok(order.client_address, 'Адрес заполнен')
        tap.eq(
            order.client_address.fullname,
            'Москва, Льва Толстого, 16',
            'адрес'
        )
        tap.eq(order.client_address.lon, 37.587093, 'lon')
        tap.eq(order.client_address.lat, 55.733969, 'lat')


async def test_negative_time(tap, dataset, api, uuid, now):
    with tap.plan(12, 'Заполнение delivery_promise и client_address'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')


        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 123,
                                }
                            ],
                            'store_id': store.store_id,
                            'client_address': {
                                'fullname': 'Москва, Льва Толстого, 16',
                                'lat': 55.733969,
                                'lon': 37.587093,
                            },
                            'delivery_promise': -123,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        order = await dataset.Order.load(
            [store.store_id, external_id],
            by='external'
        )
        tap.ok(order, 'ордер загружен')
        tap.ok(order.delivery_promise, 'delivery_promise установлен')
        tap.ok(
            order.delivery_promise.timestamp() < now().timestamp(),
            'значение delivery_promise'
        )

        tap.ok(order.client_address, 'Адрес заполнен')
        tap.eq(
            order.client_address.fullname,
            'Москва, Льва Толстого, 16',
            'адрес'
        )
        tap.eq(order.client_address.lon, 37.587093, 'lon')
        tap.eq(order.client_address.lat, 55.733969, 'lat')
