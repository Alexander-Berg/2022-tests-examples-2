import pytest

from stall.model.order import Order
from stall.model.product_components import (
    ProductComponents, ProductVariant
)


async def test_check_barcode_executer(tap, dataset, api, uuid):
    with tap.plan(10, 'Создание ордера инвентаризации'):
        _, user, shelves, products = await generate_stocks(
            tap,
            dataset,
            role='barcode_executer'
        )

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_check',
                        json={
                            'order_id': external_id,
                            'check': {
                                'shelves': [s.shelf_id for s in shelves],
                                'products': [p.product_id for p in products],
                            }
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_check_executer(tap, dataset, api, uuid):
    with tap.plan(16, 'Создание ордера инвентаризации'):
        store, user, shelves, products = await generate_stocks(
            tap,
            dataset,
            role='executer'
        )

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_check',
                        json={
                            'order_id': external_id,
                            'check': {
                                'shelves': [s.shelf_id for s in shelves],
                                'products': [p.product_id for p in products],
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'check')
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.source', 'tsd')


async def test_check_product_on_shelf_be(tap, dataset, api, uuid):
    with tap.plan(10, 'Создание ордера инвентаризации'):
        _, user, shelves, products = await generate_stocks(
            tap,
            dataset,
            role='barcode_executer'
        )

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_check',
                        json={
                            'order_id': external_id,
                            'check': {
                                'shelves': [s.shelf_id for s in shelves],
                                'products': [p.product_id for p in products],
                            },
                            'mode': 'check_product_on_shelf',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_check_product_on_shelf_e(tap, dataset, api, uuid):
    with tap.plan(16, 'Создание ордера инвентаризации'):
        store, user, shelves, products = await generate_stocks(
            tap,
            dataset,
            role='executer'
        )

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_check',
                        json={
                            'order_id': external_id,
                            'check': {
                                'shelves': [s.shelf_id for s in shelves],
                                'products': [p.product_id for p in products],
                            },
                            'mode': 'check_product_on_shelf',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'check_product_on_shelf')
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.source', 'tsd')


async def test_check_inv_prd_on_shelf_be(tap, dataset, api, uuid):
    with tap.plan(10, 'Создание ордера инвентаризации'):
        _, user, shelves, products = await generate_stocks(
            tap,
            dataset,
            estatus='inventory',
            role='barcode_executer'
        )

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_check',
                        json={
                            'order_id': external_id,
                            'check': {
                                'shelves': [s.shelf_id for s in shelves],
                                'products': [p.product_id for p in products],
                            },
                            'mode': 'check_product_on_shelf',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_check_inv_prd_on_shelf_e(tap, dataset, api, uuid):
    with tap.plan(16, 'Создание ордера инвентаризации'):
        store, user, shelves, products = await generate_stocks(
            tap,
            dataset,
            estatus='inventory',
            role='stocktaker'
        )

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_check',
                        json={
                            'order_id': external_id,
                            'check': {
                                'shelves': [s.shelf_id for s in shelves],
                                'products': [p.product_id for p in products],
                            },
                            'mode': 'check_product_on_shelf',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'inventory_check_product_on_shelf')
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.source', 'tsd')


@pytest.mark.parametrize(
    'role, result_status',
    [
        ('stocktaker', 200),
        ('executer', 403),
        ('barcode_executer', 403),
        ('chief_audit', 200),
        ('company_admin', 403),
        ('admin', 200),
    ]
)
async def test_access_to_inv_check(tap, dataset, api, uuid,
                                   role, result_status):
    with tap.plan(9, 'Создание ордера инвентаризации'):
        _, user, shelves, products = await generate_stocks(
            tap,
            dataset,
            estatus='inventory',
            role=role
        )

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_check',
                        json={
                            'order_id': external_id,
                            'check': {
                                'shelves': [s.shelf_id for s in shelves],
                                'products': [p.product_id for p in products],
                            },
                            'mode': 'check_product_on_shelf',
                        })
        t.status_is(result_status, diag=True)


@pytest.mark.parametrize(
    'store_estatus,order_status,order_vars,parent_added,exp_vars',
    [
        # инва старая, склад работает, никаких родителей
        (
            'processing',
            'complete',
            {},
            False,
            {}
        ),

        # инва уже закончилась, режим инвы, ничего не получили
        (
            'inventory',
            'complete',
            {'third_party_assistance': True},
            False,
            {}
        ),

        # инва в самом разгаре, наследовали родителя и его признак
        (
            'inventory',
            'processing',
            {'third_party_assistance': True},
            True,
            {'third_party_assistance': True},
        ),

        # инва в самом разгаре, наследовали родителя и его признак
        (
            'inventory',
            'processing',
            {'third_party_assistance': False},
            True,
            {'third_party_assistance': False},
        )
    ]
)
async def test_check_inv_parent(  # pylint: disable=too-many-arguments
        tap, dataset, api, uuid, store_estatus,
        order_status, order_vars, parent_added, exp_vars):
    # pylint: disable=too-many-locals
    with tap.plan(7, 'Во время инвы пророс родитель'):
        store = await dataset.store(estatus=store_estatus)
        user = await dataset.user(store=store)
        stock = await dataset.stock(store=store, count=137)
        inventory_order = await dataset.order(
            type='inventory',
            status=order_status,
            estatus='begin',
            store=store,
            vars=order_vars,
        )
        t = await api(user=user)
        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_check',
            json={
                'order_id': external_id,
                'check': {
                    'shelves': [stock.shelf_id],
                    'products': [stock.product_id],
                },
                'mode': 'check_product_on_shelf',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        order_id = t.res['json']['order']['order_id']

        new_order = await inventory_order.load(order_id)
        tap.ok(new_order, 'Создан ордер')
        tap.eq(new_order.external_id, external_id, 'Правильный external')
        tap.is_ok(
            inventory_order.order_id in new_order.parent,
            parent_added,
            'Родитель добавился' if parent_added else 'Родитель не добавился'
        )
        tap.eq(
            new_order.vars,
            exp_vars,
            'Варсы правильные'
        )


async def test_parent(tap, dataset, api, uuid):
    with tap.plan(4, 'передача идентификаторов родителей'):
        store       = await dataset.store()
        user        = await dataset.user(role='executer', store=store)
        product     = await dataset.product()
        shelf       = await dataset.shelf(store=store)

        parent = await dataset.order(
            store=store,
            type='check_product_on_shelf',
            status='complete',
            estatus='done',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_check',
            json={
                'order_id': uuid(),
                'mode': 'check_product_on_shelf',
                'check': {
                    'shelves': [shelf.shelf_id],
                    'products': [product.product_id],
                },
                'parent': [parent.order_id],
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.parent', [parent.order_id])


async def test_parent_unavailable(tap, dataset, api, uuid, now):
    with tap.plan(3, 'Не создать с закрытой приемкой'):
        store = await dataset.store()
        user = await dataset.user(role='executer', store=store)
        product = await dataset.product()
        shelf = await dataset.shelf(store=store)

        parent = await dataset.order(
            store=store,
            type='acceptance',
            status='complete',
            estatus='done',
            vars={'all_children_done': now()},
        )

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_check',
            json={
                'order_id': uuid(),
                'mode': 'check_product_on_shelf',
                'check': {
                    'shelves': [shelf.shelf_id],
                    'products': [product.product_id],
                },
                'parent': [parent.order_id],
            })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')


async def test_parent_request_type(tap, dataset, api, uuid):
    with tap.plan(3, 'наследуем request_type'):
        store = await dataset.store()
        user = await dataset.user(role='executer', store=store)
        product = await dataset.product()
        shelf = await dataset.shelf(store=store)

        parent = await dataset.order(
            store=store,
            type='acceptance',
            status='complete',
            estatus='done',
            attr={'request_type': 'smth'}
        )
        await dataset.order(
            type='sale_stowage',
            store=store,
            status='complete',
            estatus='done',
            parent=[parent.order_id],
        )

        check_external_id = uuid()

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_check',
            json={
                'order_id': check_external_id,
                'mode': 'check_product_on_shelf',
                'check': {
                    'shelves': [shelf.shelf_id],
                    'products': [product.product_id],
                },
                'parent': [parent.order_id],
            }
        )
        t.status_is(200, diag=True)

        check = await dataset.Order.load(
            (store.store_id, check_external_id), by='external',
        )

        tap.eq(
            check.attr['request_type'],
            parent.attr['request_type'],
            'прокинули request_type'
        )


async def test_parent_unknown(tap, dataset, api, uuid):
    with tap.plan(3, 'неизвестный идентификатор родителя'):
        store       = await dataset.store()
        user        = await dataset.user(role='executer', store=store)
        product     = await dataset.product()
        shelf       = await dataset.shelf(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_check',
            json={
                'order_id': uuid(),
                'mode': 'check_product_on_shelf',
                'check': {
                    'shelves': [shelf.shelf_id],
                    'products': [product.product_id],
                },
                'parent': [uuid()],
            })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_parent_access(tap, dataset, api, uuid):
    with tap.plan(3, 'родитель не может быть из другой лавки'):
        store1      = await dataset.store()
        store2      = await dataset.store()
        user        = await dataset.user(role='executer', store=store1)
        product     = await dataset.product()
        shelf       = await dataset.shelf(store=store1)

        parent = await dataset.order(
            store=store2,
            type='acceptance',
            status='complete',
            estatus='done',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_check',
            json={
                'order_id': uuid(),
                'mode': 'check_product_on_shelf',
                'check': {
                    'shelves': [shelf.shelf_id],
                    'products': [product.product_id],
                },
                'parent': [parent.order_id],
            })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def generate_stocks(tap, dataset, estatus='processing', role=None):
    store = await dataset.store(estatus=estatus)
    tap.ok(store, 'склад создан')
    tap.eq(store.estatus, estatus, f'в режиме {estatus}')

    user = await dataset.user(role=role, store=store)
    tap.ok(user, 'пользователь создан')
    tap.eq(user.store_id, store.store_id, 'на складе')

    products = [await dataset.product() for _ in range(3)]
    tap.ok(products, 'продукты сгенерированы')

    shelves = [await dataset.shelf(store_id=user.store_id)
               for _ in range(3)]
    tap.ok(shelves, 'полки сгенерированы')

    stocks = [
        await dataset.stock(shelf=s, product=p, count=521)
        for s in shelves
        for p in products
    ]

    tap.eq(len(stocks), 9, 'Сгенерированы остатки')
    return store, user, shelves, products


async def test_check_product_parent_acc(
        tap, dataset, api, uuid, wait_order_status
):
    with tap.plan(17, 'проверка наличия товара в ассортименте'):
        store = await dataset.full_store(options={'exp_schrodinger': True})
        user = await dataset.user(role='admin', store=store)
        product = await dataset.product()
        shelf = await dataset.shelf(store=store)
        parent_order = await dataset.order(
            store=store,
            type='acceptance',
            attr={'contractor_id': uuid()},
            status='complete',
            estatus='done',
        )
        await dataset.order(
            type='sale_stowage',
            store=store,
            status='complete',
            estatus='done',
            parent=[parent_order.order_id],
        )

        t = await api(user=user)
        json_order_check = {
            'order_id': uuid(),
            'mode': 'check_product_on_shelf',
            'check': {
                'shelves': [shelf.shelf_id],
                'products': [product.product_id],
            },
            'parent': [parent_order.order_id],
        }
        await t.post_ok('api_tsd_order_check', json=json_order_check)
        t.status_is(200, diag=True)

        order = await Order.load(
            (store.store_id, json_order_check['order_id']),
            by='external',
        )
        await wait_order_status(order, ('failed', 'done'))
        await order.reload()
        tap.eq(
            order.problems[0].type,
            'assortment_contractor_not_found',
            'проблема появилась'
        )

        product2 = await dataset.product()
        assortment = await dataset.assortment_contractor(
            store=store, contractor_id=parent_order.attr['contractor_id']
        )
        await dataset.assortment_contractor_product(
            assortment=assortment, product=product
        )
        json_order_check['order_id'] = uuid()
        json_order_check['check']['products'].append(product2.product_id)
        json_order_check['check']['shelves'].append(shelf.shelf_id)
        await t.post_ok('api_tsd_order_check', json=json_order_check)
        t.status_is(200)

        order = await Order.load(
            (store.store_id, json_order_check['order_id']),
            by='external',
        )
        await wait_order_status(order, ('failed', 'done'))
        await order.reload()
        tap.eq(
            order.problems[0].type,
            'assortment_contractor_product_not_found',
            'проблема появилась'
        )
        tap.eq(
            order.problems[0].product_id,
            product2.product_id,
            'продукт тот'
        )

        parent_order.required = [
            {'product_id': p.product_id, 'count': 300}
            for p in [product, product2]
        ]
        await parent_order.save()
        json_order_check['order_id'] = uuid()
        await t.post_ok('api_tsd_order_check', json=json_order_check)
        t.status_is(200)

        order = await Order.load(
            (store.store_id, json_order_check['order_id']),
            by='external',
        )
        await wait_order_status(order, ('complete', 'done'), user_done=user)
        await order.reload()
        tap.eq(order.problems, [], 'проблем нет')

        parent_order.required = []
        await parent_order.save()
        await dataset.assortment_contractor_product(
            assortment=assortment, product=product2
        )
        json_order_check['order_id'] = uuid()
        await t.post_ok('api_tsd_order_check', json=json_order_check)
        t.status_is(200)

        order = await Order.load(
            (store.store_id, json_order_check['order_id']),
            by='external',
        )
        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()
        tap.eq(order.problems, [], 'проблем нет')


async def test_check_no_contractor_acc(
        tap, api, dataset, uuid, wait_order_status
):
    with tap.plan(8, 'проверяем запрет на пересчет с лишними товарами'):
        store = await dataset.full_store(options={'exp_schrodinger': True})
        user = await dataset.user(role='admin', store=store)
        product = await dataset.product()
        shelf = await dataset.shelf(store=store)
        parent_order = await dataset.order(
            store=store,
            type='acceptance',
            attr={},
            status='complete',
            estatus='done',
        )
        await dataset.order(
            type='sale_stowage',
            store=store,
            status='complete',
            estatus='done',
            parent=[parent_order.order_id],
        )

        t = await api(user=user)
        json_order_check = {
            'order_id': uuid(),
            'mode': 'check_product_on_shelf',
            'check': {
                'shelves': [shelf.shelf_id],
                'products': [product.product_id],
            },
            'parent': [parent_order.order_id],
        }
        await t.post_ok('api_tsd_order_check', json=json_order_check)
        t.status_is(200)

        order = await Order.load(
            (store.store_id, json_order_check['order_id']),
            by='external',
        )
        await wait_order_status(order, ('failed', 'done'))
        await order.reload()
        tap.eq(
            order.problems[0].type,
            'check_product_not_in_acceptance',
            'проблема появилась'
        )

        parent_order.required = [
            {
                'product_id': product.product_id,
                'count': 1
            },
        ]
        await parent_order.save()
        json_order_check['order_id'] = uuid()
        await t.post_ok('api_tsd_order_check', json=json_order_check)
        t.status_is(200)

        order = await Order.load(
            (store.store_id, json_order_check['order_id']),
            by='external',
        )
        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()
        tap.eq(order.problems, [], 'проблем нет')


async def test_check_shelf_and_product(
        tap, dataset, api, uuid, estatus='processing'):

    with tap.plan(14, 'Создание ордера инвентаризации '
                      'c 1 полкой и 1 товаром'):
        store = await dataset.store(estatus=estatus)
        tap.ok(store, 'склад создан')
        tap.eq(store.estatus, estatus, f'в режиме {estatus}')

        user = await dataset.user(role='executer', store=store)
        tap.ok(user, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'продукт сгенерирован')

        shelf = await dataset.shelf(store_id=user.store_id)
        tap.ok(shelf, 'полка сгенерированы')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok('api_tsd_order_check',
                        json={
                            'order_id': external_id,
                            'check': {
                                'shelf_id': shelf.shelf_id,
                                'product_id': product.product_id,
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'check')
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.source', 'tsd')


async def test_check_kitchen_assortment(tap, dataset, api, uuid):
    with tap.plan(3, 'проверяем запрет пересчета готовой еды'):
        store = await dataset.store()
        user = await dataset.user(role='executer', store=store)
        product = await dataset.product()
        product.components = ProductComponents([
            [ProductVariant(product_id=product.product_id, count=1)]
        ])
        await product.save()

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_check',
            json={
                'order_id': uuid(),
                'check': {'product_id': product.product_id},
            }
        )
        t.status_is(400)
        t.json_is(
            'details.errors.0',
            {
                'message': 'Product in kitchen assortment',
                'code': 'ER_PRODUCTS_IN_KITCHEN_ASSORTMENT',
                'product_id': product.product_id,
            }
        )


async def test_check_inventory_locked(tap, dataset, api, uuid):
    with tap.plan(3, 'Склад в переходном статусе'):
        store       = await dataset.store(estatus='inventory_locked')
        user        = await dataset.user(role='executer', store=store)
        product     = await dataset.product()
        shelf       = await dataset.shelf(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_check',
            json={
                'order_id': uuid(),
                'mode': 'check_product_on_shelf',
                'check': {
                    'shelves': [shelf.shelf_id],
                    'products': [product.product_id],
                },
            })
        t.status_is(423, diag=True)
        t.json_is('code', 'ER_STORE_MODE')
