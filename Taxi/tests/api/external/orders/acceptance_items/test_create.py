async def test_happy_path(tap, api, dataset, uuid):
    with tap.plan(12, 'создаем приемку с посылками маркета'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        item = await dataset.item(store=store)

        external_id = uuid()
        market_courier = {
            'name': 'Курьер',
            'external_id': uuid(),
        }
        market_orders = [
            {
                'external_id': uuid(),
                'declared_cost': '300',
                'item_ids': [
                    item.item_id,
                ]
            }
        ]

        await t.post_ok(
            'api_external_orders_acceptance_items_create',
            json={
                'store_id': store.store_id,
                'external_id': external_id,
                'delivery_date': '1970-01-01',
                'market_courier': market_courier,
                'market_orders': market_orders,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_has('order.order_id')
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.external_id', external_id)

        acceptance = await dataset.Order.load(
            (store.store_id, external_id), by='external',
        )

        tap.eq(acceptance.source, 'tristero', 'источник должен быть tristero')
        tap.eq(len(acceptance.required), 1, 'одна позиция в приемке')
        tap.eq(acceptance.required[0].item_id, item.item_id, 'это посылка')
        tap.eq(acceptance.vars('market_courier'), market_courier, 'курьер')
        tap.eq(acceptance.vars('market_orders'), market_orders, 'заказы')


async def test_update_required(
    tap, api, dataset, uuid,  now, wait_order_status,
):
    with tap.plan(12, 'обновляем состав приемки'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        await dataset.shelf(store=store, type='incoming')
        item = await dataset.item(store=store)

        market_courier = {
            'name': 'Курьер',
            'external_id': uuid(),
        }
        market_orders = [
            {
                'external_id': uuid(),
                'declared_cost': '300',
                'item_ids': [
                    item.item_id,
                ]
            }
        ]

        acceptance = await dataset.order(
            **{
                'source': 'tristero',
                'type': 'acceptance',
                'store_id': store.store_id,
                'external_id': uuid(),
                'company_id': store.company_id,
                'required': [{'item_id': item.item_id}],
                'status': 'reserving',
                'approved': now(),
                'vars': {
                    'market_courier': market_courier,
                    'market_orders': market_orders,
                },
                'attr': {
                    'doc_date': '1970-01-01',
                    'doc_number': uuid(),
                    'contractor': None,
                    'contractor_id': None,
                }
            }
        )

        await wait_order_status(acceptance, ('request', 'waiting'))

        tap.eq(len(acceptance.required), 1, 'одна позиция в приемке')
        tap.eq(
            acceptance.required[0].item_id, item.item_id, 'это посылка',
        )

        suggests = await dataset.Suggest.list_by_order(acceptance)
        tap.eq(len(suggests), 1, 'одна подсказка')

        item2 = await dataset.item(store=store)
        market_orders[0]['item_ids'] = [
            item.item_id,
            item2.item_id,
        ]

        await t.post_ok(
            'api_external_orders_acceptance_items_create',
            json={
                'store_id': store.store_id,
                'external_id': acceptance.external_id,
                'delivery_date': '1970-01-01',
                'market_courier': market_courier,
                'market_orders': market_orders,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await acceptance.reload()

        tap.eq(len(acceptance.required), 2, 'две позиция в приемке')
        tap.eq(
            {r.item_id for r in acceptance.required},
            {item.item_id, item2.item_id},
            'все посылки',
        )
        tap.eq(
            acceptance.vars('market_orders'),
            market_orders,
            'заказы обновлены',
        )

        await wait_order_status(acceptance, ('request', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(acceptance)
        tap.eq(len(suggests), 2, 'две подсказки')


async def test_update_misc(tap, api, dataset, uuid,  now):
    with tap.plan(4, 'обновляем курьера'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        item = await dataset.item(store=store)

        market_courier = {
            'name': 'Курьер',
            'external_id': uuid(),
        }
        market_orders = [
            {
                'external_id': uuid(),
                'declared_cost': '300',
                'item_ids': [
                    item.item_id,
                ]
            }
        ]

        acceptance = await dataset.order(
            **{
                'source': 'tristero',
                'type': 'acceptance',
                'store_id': store.store_id,
                'external_id': uuid(),
                'company_id': store.company_id,
                'required': [{'item_id': item.item_id}],
                'status': 'reserving',
                'approved': now(),
                'vars': {
                    'market_courier': market_courier,
                    'market_orders': market_orders,
                },
                'attr': {
                    'doc_date': '1970-01-01',
                    'doc_number': uuid(),
                    'contractor': None,
                    'contractor_id': None,
                }
            }
        )

        market_courier = {
            'name': 'Курьер 2',
            'external_id': uuid(),
        }

        await t.post_ok(
            'api_external_orders_acceptance_items_create',
            json={
                'store_id': store.store_id,
                'external_id': acceptance.external_id,
                'delivery_date': '1970-01-01',
                'market_courier': market_courier,
                'market_orders': market_orders,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await acceptance.reload()

        tap.eq(
            acceptance.vars('market_courier'),
            market_courier,
            'курьер обновлен',
        )


async def test_err_not_found(tap, api, dataset, uuid):
    with tap.plan(3, 'у нас нет таких посылок'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()

        external_id = uuid()
        market_courier = {
            'name': 'Курьер',
            'external_id': uuid(),
        }
        market_orders = [
            {
                'external_id': uuid(),
                'declared_cost': '300',
                'item_ids': [uuid()]
            }
        ]

        await t.post_ok(
            'api_external_orders_acceptance_items_create',
            json={
                'store_id': store.store_id,
                'external_id': external_id,
                'delivery_date': '1970-01-01',
                'market_courier': market_courier,
                'market_orders': market_orders,
            }
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


async def test_err_conflict_acceptance(tap, api, dataset, uuid, now):
    with tap.plan(5, 'посылка есть в другой приемке'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        item = await dataset.item(store=store)

        market_courier = {
            'name': 'Курьер',
            'external_id': uuid(),
        }
        market_orders = [
            {
                'external_id': uuid(),
                'declared_cost': '300',
                'item_ids': [
                    item.item_id,
                ]
            }
        ]

        acceptance = await dataset.order(
            **{
                'source': 'tristero',
                'type': 'acceptance',
                'store_id': store.store_id,
                'external_id': uuid(),
                'company_id': store.company_id,
                'required': [{'item_id': item.item_id}],
                'status': 'reserving',
                'approved': now(),
                'vars': {
                    'market_courier': market_courier,
                    'market_orders': market_orders,
                },
                'attr': {
                    'doc_date': '1970-01-01',
                    'doc_number': uuid(),
                    'contractor': None,
                    'contractor_id': None,
                }
            }
        )

        tap.eq(
            acceptance.required[0].item_id,
            item.item_id,
            'одна и таже посылка',
        )

        await t.post_ok(
            'api_external_orders_acceptance_items_create',
            json={
                'store_id': store.store_id,
                'external_id': uuid(),
                'delivery_date': '1970-01-01',
                'market_courier': market_courier,
                'market_orders': market_orders,
            }
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_like('message', 'There are already orders with these items')


async def test_err_conflict_stock(tap, api, dataset, uuid):
    with tap.plan(4, 'посылку уже приняли'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        item = await dataset.item(store=store)

        market_courier = {
            'name': 'Курьер',
            'external_id': uuid(),
        }
        market_orders = [
            {
                'external_id': uuid(),
                'declared_cost': '300',
                'item_ids': [
                    item.item_id,
                ]
            }
        ]

        acceptance = await dataset.order(
            **{
                'source': 'tristero',
                'type': 'acceptance',
                'store_id': store.store_id,
                'external_id': uuid(),
                'company_id': store.company_id,
                'required': [{'item_id': item.item_id}],
                'status': 'complete',
            }
        )

        await dataset.stock(item=item, order=acceptance)

        await t.post_ok(
            'api_external_orders_acceptance_items_create',
            json={
                'store_id': store.store_id,
                'external_id': uuid(),
                'delivery_date': '1970-01-01',
                'market_courier': market_courier,
                'market_orders': market_orders,
            }
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_like('message', 'There are already stocks with these items')
