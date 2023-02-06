# pylint: disable=too-many-lines
import json

import pytest

from stall.model.order import Order
from stall.model.product_components import (
    ProductVariant, ProductComponents
)


@pytest.mark.parametrize('required_attrs', [
    {'count': 21},
    {'weight': 10}
])
async def test_create(tap, dataset, api, uuid, required_attrs):
    with tap.plan(15, 'Создание заказа клиента из диспетчерской'):
        product = await dataset.product()
        store = await dataset.store()

        admin   = await dataset.user(role='admin',      store=store)
        courier = await dataset.user(role='courier',    store=store)

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'order',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    **required_attrs,
                                }
                            ],
                            'approved': True,
                            'ack': admin.user_id,
                            'dispatch_type': 'grocery',
                            'courier_id': courier.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.shelves', [], 'shelves пока не заполнены job')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.dispatch_type', 'grocery')
        t.json_is('order.courier_id', courier.user_id)
        if 'weight' in required_attrs:
            t.json_is('order.required.0.weight', required_attrs['weight'])
        elif 'count' in required_attrs:
            t.json_is('order.required.0.count', required_attrs['count'])


async def test_create_noack(tap, dataset, api, uuid):
    with tap.plan(16):
        product = await dataset.product()
        tap.ok(product, f'Продукт сгенерирован {product.title}')
        store = await dataset.store()
        tap.ok(store, f'Склад сгенерирован {store.title}')

        admin = await dataset.user(store=store, role='admin')
        tap.ok(admin, 'админ сгенерирован')
        tap.eq(admin.store_id, store.store_id, 'Склад назначен')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'order',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 1
                                }
                            ],
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.shelves', [], 'shelves пока не заполнены job')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


@pytest.mark.parametrize('variant,extra', [
    ({
        'count': 21,
        'price': '1512.74',
        'price_unit': 22,
        'valid': '2012-11-10',
    }, {}),
    ({
        'weight': 9999,
        'price': '1512.74',
        'price_unit': 22,
        'valid': '2007-10-10',
    }, {}),
    ({
        'weight': 123,
        'price': '12.73',
        'valid': '2007-10-10',
    }, {}),
    ({
        'count': 21,
        'price': '1512.73',
        'price_unit': 21,
    }, {}),
    ({
        'count': 23,
        'valid': '2012-11-10',
    }, {}),
    ({
        'count': 11,
    }, {}),
    ({
        'count': 11,
    }, {
        'attr': {
            'doc_number': 'doc_1',
            'contractor': 'contractor_1',
            'trust_code': 'trust_code_1',
            'ignore_assortment': True,
        }
    }),
    ({
        'count': 11,
    }, {'attr': {'doc_number': 'doc_1'}}),
])
async def test_create_acceptance(tap, dataset, api, uuid, variant, extra):
    # pylint: disable=too-many-branches, too-many-statements
    with tap.plan(25, 'Создание заказа приёмки из диспетчерской'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        t = await api(user=admin)

        external_id = uuid()

        variant['product_id'] = product.product_id

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'acceptance',
                            'required': [variant],
                            'approved': True,
                            'ack': admin.user_id,
                            **extra,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.shelves', [], 'shelves пока не заполнены job')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.dispatch_type', None)
        t.json_is('order.courier_id', None)
        if 'valid' in variant:
            t.json_is('order.required.0.valid', variant['valid'])
        else:
            t.json_hasnt('order.required.0.valid')
        if 'price' in variant:
            t.json_is('order.required.0.price', variant['price'])
        else:
            t.json_hasnt('order.required.0.price')
        if 'price_unit' in variant:
            t.json_is('order.required.0.price_unit', variant['price_unit'])
        elif 'price' in variant:
            t.json_is('order.required.0.price_unit', 1)
        else:
            t.json_hasnt('order.required.0.price_unit')

        if 'weight' in variant:
            t.json_is('order.required.0.weight', variant['weight'])
        elif 'count' in variant:
            t.json_is('order.required.0.count', variant['count'])

        t.json_is('order.required.0.product_id', variant['product_id'])
        if 'attr' in extra and 'doc_number' in extra['attr']:
            t.json_is('order.attr.doc_number',
                      extra['attr']['doc_number'])
        else:
            t.json_has('order.attr.doc_number')

        if 'attr' in extra and 'contractor' in extra['attr']:
            t.json_is('order.attr.contractor',
                      extra['attr']['contractor'])
        else:
            t.json_hasnt('order.attr.contractor')

        if 'attr' in extra and 'trust_code' in extra['attr']:
            t.json_is('order.attr.trust_code',
                      extra['attr']['trust_code'])
        else:
            t.json_hasnt('order.attr.trust_code')

        if 'attr' in extra and 'ignore_assortment' in extra['attr']:
            t.json_is('order.attr.ignore_assortment',
                      extra['attr']['ignore_assortment'])
        else:
            t.json_hasnt('order.attr.ignore_assortment')


async def test_create_crash(tap, dataset, api, uuid):
    with tap.plan(16, 'Данные прямо взятые из креша'):
        product = await dataset.product()
        tap.ok(product, f'Продукт сгенерирован {product.title}')
        store = await dataset.store()
        tap.ok(store, f'Склад сгенерирован {store.title}')

        admin = await dataset.user(store=store, role='admin')
        tap.ok(admin, 'админ сгенерирован')
        tap.eq(admin.store_id, store.store_id, 'Склад назначен')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'type': 'acceptance',
                            'approved': True,
                            'required': [
                                {
                                    'count': 10,
                                    'product_id': product.product_id,
                                    'valid': '2020-03-31',
                                    'price': '1',
                                    'price_unit': 1
                                }
                            ],
                            'ack': admin.user_id,
                            'external_id': external_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.shelves', [], 'shelves пока не заполнены job')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


async def test_create_check(tap, dataset, api, uuid):
    with tap.plan(20, 'Создание заказа инвентаризации из диспетчерской'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id)
        tap.ok(shelf, 'полка создана')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check',
                'approved': True,
                'required': [{
                    'shelf_id': shelf.shelf_id,
                    'product_id': product.product_id,
                }],
                'ack': admin.user_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'check', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.shelves', [shelf.shelf_id], 'shelves')
        t.json_is('order.products', [product.product_id], 'products')
        t.json_is('order.required.0.shelf_id', shelf.shelf_id)
        t.json_is('order.required.0.product_id', product.product_id)
        t.json_hasnt('order.required.1')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


async def test_create_check_only_product(tap, dataset, api, uuid):
    with tap.plan(4, 'создаем check без полок'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)

        t = await api(user=admin)
        external_id = uuid()
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check',
                'approved': True,
                'required': [{
                    'product_id': product.product_id,
                }],
                'ack': admin.user_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')


async def test_create_check_mix_required(tap, dataset, api, uuid):
    with tap.plan(3, 'создаем check с "разнообразным" required'):
        product = await dataset.product()
        product2 = await dataset.product()
        store = await dataset.store()
        shelf = await dataset.shelf(store=store)

        admin = await dataset.user(role='admin', store=store)

        t = await api(user=admin)
        external_id = uuid()
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check',
                'approved': True,
                'required': [
                    {
                        'shelf_id': shelf.shelf_id,
                        'product_id': product.product_id,
                    },
                    {
                        'product_id': product2.product_id,
                    }
                ],
                'ack': admin.user_id,
            }
        )

        t.status_is(400)
        t.json_is('code', 'ER_BAD_REQUEST')



async def test_create_check_error(tap, dataset, api, uuid):
    with tap.plan(15, 'Невалидный shelf_id, product_id'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id)
        tap.ok(shelf, 'полка создана')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check',
                'approved': True,
                'required': [{
                    'shelf_id': uuid(),
                    'product_id': product.product_id,
                }],
                'ack': admin.user_id,
            })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUIRED')
        t.json_is('details.errors.0.message', 'Shelf not found')

        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check',
                'approved': True,
                'required': [{
                    'shelf_id': shelf.shelf_id,
                    'product_id': uuid(),
                }],
                'ack': admin.user_id,
            })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUIRED')
        t.json_is('details.errors.0.message', 'Product not found')

        product.components = ProductComponents(
            [[ProductVariant(product_id=product.product_id, count=1)]]
        )
        await product.save()
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check',
                'approved': True,
                'required': [{
                    'shelf_id': shelf.shelf_id,
                    'product_id': product.product_id,
                }],
                'ack': admin.user_id,
            }
        )
        t.status_is(400)
        t.json_is('code', 'ER_BAD_REQUIRED')
        t.json_is('details.errors.0.message', 'Product in kitchen assortment')


# pylint: disable=invalid-name
async def test_create_check_product_on_shelf(tap, dataset, api, uuid):
    with tap.plan(17, 'Создание заказа инвентаризации продукта'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id)
        tap.ok(shelf, 'полка создана')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'check_product_on_shelf',
                            'approved': True,
                            'product_id': product.product_id,
                            'shelf_id': shelf.shelf_id,
                            'ack': admin.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'check_product_on_shelf', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.shelves', [shelf.shelf_id], 'shelves')
        t.json_is('order.products', [product.product_id], 'products')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


async def test_create_check_product_on_shelf_required(tap, dataset, api, uuid):
    with tap.plan(18, 'Создание заказа инвентаризации продукта'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id)
        tap.ok(shelf, 'полка создана')

        t = await api(user=admin)

        external_id = uuid()
        required = [{
            'shelf_id': shelf.shelf_id,
            'product_id': product.product_id,
            'update_valids': False,
        }]
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'check_product_on_shelf',
                            'approved': True,
                            'ack': admin.user_id,
                            'required': required
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'check_product_on_shelf', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.required.0.shelf_id', shelf.shelf_id)
        t.json_is('order.required.0.product_id', product.product_id)
        t.json_is('order.required.0.update_valids', False)



@pytest.mark.parametrize('update_valids', [True, False])
async def test_create_check_product_on_shelf_valids(tap,
                                                    dataset,
                                                    api,
                                                    uuid,
                                                    update_valids):
    with tap.plan(20, 'Создание заказа инвентаризации продукта'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id)
        tap.ok(shelf, 'полка создана')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'check_product_on_shelf',
                            'approved': True,
                            'product_id': product.product_id,
                            'shelf_id': shelf.shelf_id,
                            'update_valids': update_valids,
                            'ack': admin.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'check_product_on_shelf', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.shelves', [shelf.shelf_id], 'shelves')
        t.json_is('order.products', [product.product_id], 'products')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)

        t.json_is('order.required.0.product_id', product.product_id)
        t.json_is('order.required.0.shelf_id', shelf.shelf_id)
        t.json_is('order.required.0.update_valids', update_valids)


async def test_create_check_product_on_shelf_error(tap, dataset, api, uuid):
    with tap.plan(16, 'Создание заказа инвентаризации продукта: ошибка'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id)
        tap.ok(shelf, 'полка создана')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'check_product_on_shelf',
                            'approved': True,
                            'product_id': uuid(),
                            'shelf_id': shelf.shelf_id,
                            'ack': admin.user_id,
                        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_BAD_PRODUCTS_OR_SHELVES')
        t.json_is('details.errors.0.message', 'Product not found')
        t.json_is('details.errors.0.path', 'body.product_id')

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'check_product_on_shelf',
                            'approved': True,
                            'product_id': product.product_id,
                            'shelf_id': uuid(),
                            'ack': admin.user_id,
                        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_BAD_PRODUCTS_OR_SHELVES')
        t.json_is('details.errors.0.message', 'Shelf not found')
        t.json_is('details.errors.0.path', 'body.shelf_id')

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'check_product_on_shelf',
                            'approved': True,
                            'required': [{'product_id': product.product_id}],
                            'ack': admin.user_id,
                        })
        t.status_is(400)
        t.json_is('code', 'BAD_REQUEST')


async def test_create_check_final(tap, dataset, api, uuid):
    with tap.plan(17, 'проверяем создание check_final'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        stock = await dataset.stock(store=store, count=123)

        t = await api(user=user)
        external_id = uuid()
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check_final',
                'approved': True,
                'required': [{
                    'shelf_id': stock.shelf_id,
                    'product_id': stock.product_id,
                }],
                'ack': user.user_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'check_final', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.shelves', [stock.shelf_id], 'shelves')
        t.json_is('order.products', [stock.product_id], 'products')
        t.json_is('order.required.0.shelf_id', stock.shelf_id)
        t.json_is('order.required.0.product_id', stock.product_id)
        t.json_hasnt('order.required.1')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [user.user_id], 'acks')
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


async def test_create_check_final_error(tap, dataset, api, uuid):
    with tap.plan(14, 'ошибки при создании check_final'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        stock = await dataset.stock(store=store, count=123)

        t = await api(user=user)
        external_id = uuid()
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check_final',
                'approved': True,
                'required': [{
                    'product_id': stock.product_id,
                }],
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')

        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check_final',
                'approved': True,
                'required': [{
                    'product_id': uuid(),
                    'shelf_id': uuid(),
                }],
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUIRED')
        t.json_is('message', 'Bad required')
        res_json = t.res
        tap.eq(
            len(json.loads(res_json['body'])['details']['errors']),
            2,
            '2 ошибки'
        )

        t = await api(user=user)
        external_id = uuid()
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check_final',
                'approved': True,
                'required': [
                    {
                        'product_id': stock.product_id,
                        'shelf_id': stock.shelf_id,
                    },
                    {
                        'product_id': stock.product_id,
                        'shelf_id': stock.shelf_id,
                    },
                ],
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        # just for fun
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'check_final',
                'approved': True,
                'required': [],
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')


@pytest.mark.parametrize(
    'shelf_type',
    [
        'store',
        'office',
        'markdown',
        'kitchen_components',
    ]
)
async def test_create_check_more(tap, dataset, api, uuid, shelf_type):
    with tap.plan(18, 'Создание заказа слепой инвентаризации'):
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id,
                                    type=shelf_type)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.type, shelf_type, f'тип полки {shelf_type}')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'check_more',
                            'approved': True,
                            'shelves': [shelf.shelf_id],
                            'ack': admin.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'check_more', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.shelves', [shelf.shelf_id], 'shelves')
        t.json_is('order.products', [], 'products')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


@pytest.mark.parametrize(
    'order_type',
    [
        'check_valid_short',
        'check_valid_regular',
        'writeoff_prepare_day',
        'visual_control'
    ]
)
async def test_create_check_valid(tap, dataset, api, uuid, order_type):
    with tap.plan(19, 'Создание заказа КСГ'):
        store = await dataset.store(
            options = {'check_valid_use_markdown': True},
        )

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id)
        tap.ok(shelf, 'полка создана')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': order_type,
                            'approved': True,
                            'ack': admin.user_id,
                            'mode': 'store2markdown',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', order_type, 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.required', [], 'required')
        t.json_is('order.shelves', [], 'shelves')
        t.json_is('order.products', [], 'products')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.vars.mode', 'store2markdown')


async def test_create_stoplist(tap, dataset, api, uuid):
    with tap.plan(15, 'Создание заказа стоплист из диспетчерской'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id)
        tap.ok(shelf, 'полка создана')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'stop_list',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'shelf_id': shelf.shelf_id,
                                },
                            ],
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'stop_list', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.required.0.shelf_id', shelf.shelf_id, 'shelves')
        t.json_is('order.required.0.product_id',
                  product.product_id,
                  'products')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


async def test_create_stoplist_br(tap, dataset, api, uuid):
    with tap.plan(5, 'некорректный required'):
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'stop_list',
                            'required': [
                                {
                                    'product_id': None,
                                    'shelf_id': None,
                                },
                            ],
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUIRED')


@pytest.mark.parametrize('shelf_count', [0, 1, 2])
async def test_create_writeoff(tap, dataset, api, uuid, shelf_count):
    with tap.plan(12, 'Ордер списания'):
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        t = await api(user=admin)

        shelves = []

        with tap.subtest(None, 'Создаём полки списания') as taps:
            for _ in range(shelf_count):
                trash = await dataset.shelf(store=store, type='trash')
                taps.eq(trash.store_id, store.store_id, 'полка создана')
                taps.eq(trash.type, 'trash', 'полка списания')

                if shelf_count == 2:
                    shelves = [trash.shelf_id]

        external_id = uuid()

        args = {}

        if shelves:
            args['shelves'] = shelves

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'writeoff',
                            **args,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'writeoff')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        if shelf_count != 2:
            t.json_is('order.shelves', [], 'пустой shelves')
        else:
            t.json_has('order.shelves.0', 'Одна полка в shelves')


async def test_er_create_in_inventory_mode(tap, dataset, api, uuid):
    with tap.plan(4, 'Создание заказа в режиме инвентаризации'):
        product = await dataset.product()
        store = await dataset.store(estatus='inventory')

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'order',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 21
                                }
                            ],
                            'approved': True,
                            'ack': admin.user_id,
                        })
        t.status_is(423, diag=True)


async def test_create_inventory(tap, dataset, api, uuid):
    with tap.plan(14, 'Создание ордера инвентаризации из диспетчерской'):
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        admin = await dataset.user(role='admin', store=store)
        tap.eq(admin.store_id, store.store_id, 'админ создан')

        t = await api(user=admin)
        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'inventory',
                            'approved': True,
                            'ack': admin.user_id,
                            'final_inventory': True,
                        })
        t.status_is(200, diag=True)
        t.json_is('order.external_id', external_id)

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'inventory',
                            'approved': True,
                            'ack': admin.user_id,
                            'final_inventory': True,
                        },
                        desc='Идемпотентность')
        t.status_is(200, diag=True)
        t.json_is('order.external_id', external_id)
        t.json_is('order.vars.shelf_types', [])
        t.json_is('order.vars.third_party_assistance', False)
        t.json_is('order.vars.final_inventory', True)

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': uuid(),
                            'type': 'inventory',
                            'approved': True,
                            'ack': admin.user_id,
                            'final_inventory': False,
                        },
                        desc='Новый ордер создать не даст')
        t.status_is(423, diag=True)
        t.json_is('code', 'ER_INVENTORY_EXISTS')


@pytest.mark.parametrize('shelf_types', [
    ['store'],
    ['store', 'markdown'],
    ['trash', 'kitchen_trash', 'repacking'],
])
async def test_create_inventory_shelf_types(
        tap, dataset, api, uuid, shelf_types):
    with tap.plan(6, 'Создание ордера инвентаризации с типами полок'):
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        admin = await dataset.user(role='admin', store=store)
        tap.eq(admin.store_id, store.store_id, 'админ создан')

        t = await api(user=admin)
        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'inventory',
                            'approved': True,
                            'ack': admin.user_id,
                            'shelf_types': shelf_types
                        })
        t.status_is(200, diag=True)
        t.json_is('order.external_id', external_id)
        order_id = t.res['json']['order']['order_id']
        order = await dataset.Order.load(order_id)
        tap.eq(order.vars['shelf_types'], shelf_types, 'Типы полок')


@pytest.mark.parametrize('shelf_types', [
    [],
    None,
    ['lost'],
    ['lost', 'found']
])
async def test_create_inventory_wrong_shelf_types(
        tap, dataset, api, uuid, shelf_types):
    with tap.plan(4, 'Создание инвентаризации с неправильными полками'):
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        admin = await dataset.user(role='admin', store=store)
        tap.eq(admin.store_id, store.store_id, 'админ создан')

        t = await api(user=admin)
        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'inventory',
                            'approved': True,
                            'ack': admin.user_id,
                            'shelf_types': shelf_types
                        })
        t.status_is(400, diag=True)


async def test_create_inventory_third_party(tap, dataset, api, uuid):
    with tap.plan(6, 'Создание специального ордера инвентаризации'):
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        admin = await dataset.user(role='admin', store=store)
        tap.eq(admin.store_id, store.store_id, 'админ создан')

        t = await api(user=admin)
        external_id = uuid()
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'inventory',
                'third_party_assistance': True
            }
        )
        t.status_is(200, diag=True)
        t.json_is('order.external_id', external_id)
        order_id = t.res['json']['order']['order_id']
        order = await dataset.Order.load(order_id)
        tap.eq(order.vars['third_party_assistance'], True, 'Флаг на месте')


@pytest.mark.parametrize(
    'role,permitted,prohibited',
    [
        [
            'support',
            ['writeoff', 'writeoff_prepare_day', 'order',
             'check_valid_regular', 'check_valid_short'],
            ['acceptance', 'inventory']
        ],
        [
            'support_ro',
            [],
            ['writeoff', 'writeoff_prepare_day', 'check_valid_regular',
             'check_valid_short', 'acceptance', 'order', 'inventory']
        ],
        [
            'store_admin',
            [],
            ['writeoff', 'writeoff_prepare_day', 'check_valid_regular',
             'check_valid_short', 'acceptance', 'order', 'inventory']
        ],
    ]
)
async def test_create_order(tap, dataset, api, uuid,
                            role, permitted, prohibited):
    with tap.plan(21, 'Создание заказа клиента из диспетчерской'):
        product = await dataset.product()
        store = await dataset.store()

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)

        for order_type in permitted:
            external_id = uuid()
            await t.post_ok('api_disp_orders_create',
                            json={
                                'external_id': external_id,
                                'type': order_type,
                                'required': [
                                    {
                                        'product_id': product.product_id,
                                        'count': 21
                                    }
                                ],
                                'approved': True,
                                'ack': user.user_id,
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        for order_type in prohibited:
            external_id = uuid()
            await t.post_ok('api_disp_orders_create',
                            json={
                                'external_id': external_id,
                                'type': order_type,
                                'required': [
                                    {
                                        'product_id': product.product_id,
                                        'count': 21
                                    }
                                ],
                                'approved': True,
                                'ack': user.user_id,
                            })
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('role', ['admin'])
async def test_create_shipment(tap, dataset, api, uuid, role):
    with tap.plan(5, 'Создание отгрузки'):
        product = await dataset.product()
        store = await dataset.store()

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'shipment',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 10,
                                    'price_type': 'store',
                                },
                                {
                                    'product_id': product.product_id,
                                    'count': 20,
                                    'price_type': 'markdown',
                                },
                                {
                                    'product_id': product.product_id,
                                    'count': 30,
                                    'price_type': 'office',
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


@pytest.mark.parametrize('study', [True, False, None])
async def test_order_study(tap, dataset, api, uuid, study):
    with tap.plan(6, 'поддержка study в .order'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store=store)
        t = await api(user=user)

        external_id = uuid()

        study_d = {}
        if study is not None:
            study_d = {'study': study}
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'order',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 21
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                            **study_d
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.store_id', store.store_id)
        t.json_has('order.study')
        t.json_is('order.study', study if study is not None else True)



async def test_create_with_contractor_id(tap, dataset, api, uuid):
    with tap.plan(6, 'Создание acceptance заказа с contractor_id'):
        product = await dataset.product()
        store = await dataset.store()

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'acceptance',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 21
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                            'attr': {
                                'doc_number': '700303-000005',
                                'doc_date': '1970-03-03',
                                'contractor': 'some_contractor',
                                'contractor_id': 'some_contractor_id',
                            },
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_has('order.attr.contractor_id')
        t.json_is('order.attr.contractor_id', 'some_contractor_id')


async def test_create_weight_stowage(tap, dataset, api, uuid):
    with tap.plan(14, 'Создание раскладки весового товара'):
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        product = await dataset.product(type_accounting='weight')
        tap.ok(product, 'вес товар создан')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'weight_stowage',
                            'ack': admin.user_id,
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 1,
                                    'weight': 100,
                                }
                            ],
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'weight_stowage', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


async def test_create_sale_stowage(tap, dataset, api, uuid):
    with tap.plan(14, 'Создание раскладки весового товара'):
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'sale_stowage',
                            'ack': admin.user_id,
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 1,
                                }
                            ],
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'sale_stowage', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


async def test_check_reserving_for_duplicate_in_required(
        tap, dataset, api, uuid):
    with tap.plan(6, 'Создание заказа инвентаризации c дубликатами'):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(store_id=admin.store_id)
        tap.ok(shelf, 'полка создана')

        t = await api(user=admin)

        external_id = uuid()
        required = [
            {
                'shelf_id': shelf.shelf_id,
                'product_id': product.product_id
            },
            {
                'shelf_id': shelf.shelf_id,
                'product_id': product.product_id
            },

        ]
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'check_product_on_shelf',
                            'approved': True,
                            'ack': admin.user_id,
                            'required': required
                        })
        t.status_is(400, diag=True)
        t.json_is('message', 'required содержит дубликаты')


async def test_create_repacking(tap, dataset, api, wait_order_status, uuid):
    with tap.plan(26, 'Создание перефасовки'):
        store = await dataset.full_store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(
            store=store,
            type='repacking',
        )

        stock = await dataset.stock(shelf=shelf)
        tap.ok(stock, 'остаток создан')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'repacking',
                            'ack': admin.user_id,
                            'required': [
                                {
                                    'product_id': stock.product_id,
                                    'shelf_id': shelf.shelf_id,
                                }
                            ],
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.type', 'repacking', 'тип')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'dispatcher')
        t.json_is('order.acks', [admin.user_id], 'acks')
        t.json_is('order.user_id', admin.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.shelves', [shelf.shelf_id])
        t.json_is('order.products', [stock.product_id])

        order = await Order.load((store.store_id, external_id), by='external')
        tap.ok(order, 'заказ найден')

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        suggest = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggest), 1, '1 саджест shelf2box')
        await suggest[0].done(count=3)

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился 2ой саджест')
        await suggests[0].done()

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился 3ий саджест')
        await suggests[0].done(count=3)

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился 4ый саджест')
        await suggests[0].done()

        await wait_order_status(order, ('complete', 'done'), user_done=admin)


async def test_create_repacking_two_products(tap, dataset, api, uuid):
    with tap.plan(7, 'Создание перефасовки с двумя продуктами в условии'):
        store = await dataset.store()

        admin = await dataset.user(role='admin', store=store)
        tap.ok(admin, 'админ создан')
        tap.ok(admin.store_id, 'склад у него есть')

        shelf = await dataset.shelf(
            store=store,
            type='repacking',
        )

        stock1 = await dataset.stock(shelf=shelf)
        tap.ok(stock1, 'первый остаток создан')

        stock2 = await dataset.stock(shelf=shelf)
        tap.ok(stock2, 'второй остаток создан')

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'repacking',
                            'ack': admin.user_id,
                            'required': [
                                {
                                    'product_id': stock1.product_id,
                                    'shelf_id': shelf.shelf_id,
                                },
                                {
                                    'product_id': stock2.product_id,
                                    'shelf_id': shelf.shelf_id,
                                },
                            ],
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
