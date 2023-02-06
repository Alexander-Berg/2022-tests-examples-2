import pytest


@pytest.mark.parametrize('role', ['admin'])
async def test_create_hand_move(tap, dataset, api, uuid, role):
    with tap.plan(11, 'Создание перемещения'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store()
        tap.ok(store, 'склад создан')


        shelf1 = await dataset.shelf(store=store)
        tap.eq(shelf1.store_id, store.store_id, 'полка 1')

        shelf2 = await dataset.shelf(store=store)
        tap.eq(shelf2.store_id, store.store_id, 'полка 2')


        user = await dataset.user(role=role, store=store)
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'hand_move',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 10,
                                    'src_shelf_id': shelf1.shelf_id,
                                    'dst_shelf_id': shelf2.shelf_id,
                                },
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


        order = await dataset.Order.load(
            [store.store_id, external_id], by='external'
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.ok(len(order.required), 1, 'один элемент')


@pytest.mark.parametrize('role', ['admin'])
async def test_create_er_noshelf(tap, dataset, api, uuid, role):
    with tap.plan(5, 'Несуществующие полки'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'hand_move',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 10,
                                    'src_shelf_id': uuid(),
                                    'dst_shelf_id': uuid(),
                                },
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_SHELF_NOT_FOUND')

@pytest.mark.parametrize('role', ['admin'])
async def test_create_er_dupplicate(tap, dataset, api, uuid, role):
    with tap.plan(7, 'Дубли'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store()
        tap.ok(store, 'склад создан')


        shelf1 = await dataset.shelf(store=store)
        tap.eq(shelf1.store_id, store.store_id, 'полка 1')

        shelf2 = await dataset.shelf(store=store)
        tap.eq(shelf2.store_id, store.store_id, 'полка 2')


        user = await dataset.user(role=role, store=store)
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'hand_move',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 10,
                                    'src_shelf_id': shelf1.shelf_id,
                                    'dst_shelf_id': shelf2.shelf_id,
                                },
                                {
                                    'product_id': product.product_id,
                                    'count': 10,
                                    'src_shelf_id': shelf1.shelf_id,
                                    'dst_shelf_id': shelf2.shelf_id,
                                },
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_DUPLICATE_REQUIRED')


async def test_item_not_found(tap, dataset, uuid, api):
    with tap.plan(8, 'проверка на наличие экземпляров'):
        item = await dataset.item()
        tap.ok(item, 'экземпляр создан')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        tap.ne(store.store_id, item.store_id, 'экземпляр в другом складе')

        shelf1 = await dataset.shelf(store=store)
        tap.eq(shelf1.store_id, store.store_id, 'полка 1')

        shelf2 = await dataset.shelf(store=store)
        tap.eq(shelf2.store_id, store.store_id, 'полка 2')


        user = await dataset.user(store=store)
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'hand_move',
                            'required': [
                                {
                                    'item_id': item.item_id,
                                    'count': 1,
                                    'src_shelf_id': shelf1.shelf_id,
                                    'dst_shelf_id': shelf2.shelf_id,
                                },
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_ITEM_NOT_FOUND')


async def test_create_er_diff_types(tap, dataset, api, uuid):
    with tap.plan(8, 'комбинации src_type,dst_type в required'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        shelf1 = await dataset.shelf(store=store)
        tap.eq(shelf1.store_id, store.store_id, 'полка 1')

        shelf2 = await dataset.shelf(store=store)
        tap.eq(shelf2.store_id, store.store_id, 'полка 2')

        kshelf = await dataset.shelf(store=store, type='kitchen_components')
        tap.eq(kshelf.store_id, store.store_id, 'полка 2')

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'hand_move',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 1,
                                    'src_shelf_id': shelf1.shelf_id,
                                    'dst_shelf_id': shelf2.shelf_id,
                                },
                                {
                                    'product_id': product.product_id,
                                    'count': 10,
                                    'src_shelf_id': shelf1.shelf_id,
                                    'dst_shelf_id': kshelf.shelf_id,
                                },
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUIRED')


async def test_create_er_office(tap, dataset, api, uuid):
    with tap.plan(13, 'создание перемещения с store на office и обрано'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        consumable = await dataset.product(
            vars={
                'imported': {
                    'nomenclature_type': 'consumable',
                }
            }
        )
        tap.ok(product, 'расходник создан')

        store = await dataset.store(options={'exp_illidan': True})
        tap.ok(store, 'склад создан')

        shelf1 = await dataset.shelf(
            store=store,
            type='store'
        )
        tap.eq(shelf1.store_id, store.store_id, 'полка 1')

        shelf2 = await dataset.shelf(
            store=store,
            type='office'
        )
        tap.eq(shelf2.store_id, store.store_id, 'полка 2')

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'hand_move',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 1,
                                    'src_shelf_id': shelf1.shelf_id,
                                    'dst_shelf_id': shelf2.shelf_id,
                                },
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUIRED')
        t.json_is('message', 'Incorrect required record')

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'hand_move',
                            'required': [
                                {
                                    'product_id': consumable.product_id,
                                    'count': 1,
                                    'src_shelf_id': shelf2.shelf_id,
                                    'dst_shelf_id': shelf1.shelf_id,
                                },
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUIRED')
        t.json_is('message', 'Incorrect required record')


async def test_create_er_markdown(tap, dataset, api, uuid):
    with tap.plan(8, 'создание перемещения на markdown'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        shelf1 = await dataset.shelf(
            store=store,
            type='store'
        )
        tap.eq(shelf1.store_id, store.store_id, 'полка 1')

        shelf2 = await dataset.shelf(
            store=store,
            type='markdown'
        )
        tap.eq(shelf2.store_id, store.store_id, 'полка 2')

        user = await dataset.user(role='company_admin', store=store)
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'hand_move',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 1,
                                    'src_shelf_id': shelf1.shelf_id,
                                    'dst_shelf_id': shelf2.shelf_id,
                                },
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUIRED')
        t.json_is('message', 'No move to markdown')
