import datetime

import pytest


async def test_groups(tap, dataset, wait_order_status, cfg):
    with tap.plan(22, 'раскладка генерит заказы'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product1 = await dataset.product()
        tap.ok(product1, 'товар создан')

        product2 = await dataset.product(tags=['freezer'])
        tap.ok(product2, 'товар в морозильник создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        order = await dataset.order(
            type='acceptance',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 22,
                },
                {
                    'product_id': product2.product_id,
                    'count': 7,
                },
                {
                    'item_id': item.item_id,
                    'count': 1,
                }
            ],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'Ордер создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.isa_ok(order.vars['stowage_id'], list, 'список дочек')
        tap.eq(len(order.vars['stowage_id']), 3, 'три дочки')

        found=set()

        for order_id in order.vars['stowage_id']:
            stowage = await dataset.Order.load(order_id)
            tap.eq(stowage.store_id, store.store_id, 'раскладка загружена')
            tap.eq(len(stowage.required), 1, 'одно требование')
            with stowage.required[0] as r:
                if r.product_id == product1.product_id:
                    found.add(product1.product_id)
                    tap.eq(r.count, 22, 'количество')
                    tap.eq(stowage.vars['tag'], None, 'тип warm')
                elif r.product_id == product2.product_id:
                    found.add(product2.product_id)
                    tap.eq(r.count, 7, 'количество')
                    tap.eq(stowage.vars['tag'], 'freezer', 'тип freezer')
                elif r.item_id == item.item_id:
                    found.add(item.item_id)
                    tap.eq(r.count, 1, 'количество')
                    tap.eq(stowage.vars['tag'], 'parcel', 'тип parcel')
        tap.eq(found,
               {product1.product_id, product2.product_id, item.item_id},
               'дочки разные')


async def test_deleted_product_tag(tap, dataset, wait_order_status, cfg):
    with tap.plan(11, 'раскладка для несуществующего продукта'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product(tags=['refrigerator'])
        tap.ok(product, 'товар в холодилник создан')

        order = await dataset.order(
            type='acceptance',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': product.product_id,
                    'count': 3,
                }
            ],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'Ордер создан')
        await wait_order_status(order, ('complete', 'begin'), user_done=user)
        tap.ok(await product.rm(), 'Продукт удален')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.isa_ok(order.vars['stowage_id'], list, 'список дочек')
        tap.eq(len(order.vars['stowage_id']), 1, 'одна дочка')

        order_id = order.vars['stowage_id'][0]
        stowage = await dataset.Order.load(order_id)
        tap.eq(stowage.required[0].count, 3, 'количество')
        tap.eq(hasattr(stowage.vars, 'tag'), False, 'нет типа')


async def test_one_stowage_mixed(tap, dataset, wait_order_status):
    with tap.plan(12, '1 раскладка с разными типами продуктов'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product1 = await dataset.product(tags=['safe'])
        tap.ok(product1, 'товар safe создан')

        product2 = await dataset.product(tags=['freezer'])
        tap.ok(product2, 'товар в морозильник создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        order = await dataset.order(
            type='acceptance',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 22,
                },
                {
                    'product_id': product2.product_id,
                    'count': 7,
                },
                {
                    'item_id': item.item_id,
                    'count': 1,
                }
            ],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'Ордер создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.isa_ok(order.vars['stowage_id'], list, 'список дочек')
        tap.eq(len(order.vars['stowage_id']), 1, 'одна дочка')
        stowage = await dataset.Order.load(order.vars['stowage_id'][0])
        tap.eq(stowage.store_id, store.store_id, 'раскладка загружена')
        tap.eq(len(stowage.required), 3, '3 требования')
        tap.eq(stowage.vars['tag'], 'mixed', 'тип mixed')


async def test_one_stowage_very_cold(tap, dataset, wait_order_status):
    with tap.plan(11, '1 раскладка c типом very_cold'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product1 = await dataset.product(tags=['freezer2_2'])
        tap.ok(product1, 'товар в морозильник -2+2 создан')

        product2 = await dataset.product(tags=['freezer2_2'])
        tap.ok(product2, 'товар')

        order = await dataset.order(
            type='acceptance',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 22,
                },
                {
                    'product_id': product2.product_id,
                    'count': 7,
                },
            ],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'Ордер создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.isa_ok(order.vars['stowage_id'], list, 'список дочек')
        tap.eq(len(order.vars['stowage_id']), 1, 'одна дочка')
        stowage = await dataset.Order.load(order.vars['stowage_id'][0])
        tap.eq(stowage.store_id, store.store_id, 'раскладка загружена')
        tap.eq(len(stowage.required), 2, '2 требования')
        tap.eq(stowage.vars['tag'], 'freezer2_2', 'тип freezer2_2')


# pylint: disable=too-many-locals
@pytest.mark.parametrize(
    'tags_1, tags_2, stowage_tag',
    [(['refrigerator'], [], 'mixed'),
     (['refrigerator'], ['refrigerator'], 'refrigerator')])
async def test_perishable_product(
    tap, dataset, wait_order_status, cfg, tags_1, tags_2, stowage_tag
):
    with tap.plan(
        23, f'раскладка скоропортящихся товаров с тегом {stowage_tag}'
    ):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        store = await dataset.full_store(options={'exp_perishable_food': True})
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product1 = await dataset.product(tags=['freezer2_2'])
        tap.ok(product1, 'товар создан')

        product2 = await dataset.product(valid=3, tags=tags_1)
        tap.ok(product2, 'товар с маленьким сроком годности создан')

        product3 = await dataset.product(tags=tags_2)
        tap.ok(product3, 'товар создан')

        order = await dataset.order(
            type='acceptance',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 22,
                },
                {
                    'product_id': product2.product_id,
                    'count': 7,
                },
                {
                    'product_id': product3.product_id,
                    'count': 3,
                    'valid': (datetime.datetime.now().date()
                              + datetime.timedelta(days=1)),
                },
            ],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'Ордер создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.isa_ok(order.vars['stowage_id'], list, 'список дочек')
        tap.eq(len(order.vars['stowage_id']), 2, 'две дочки')

        found=set()

        for order_id in order.vars['stowage_id']:
            stowage = await dataset.Order.load(order_id)
            tap.eq(stowage.store_id, store.store_id, 'раскладка загружена')
            for r in stowage.required:
                if r.product_id == product1.product_id:
                    found.add(product1.product_id)
                    tap.eq(r.count, 22, 'количество')
                    tap.eq(stowage.vars['tag'],
                           'freezer2_2',
                           'freezer2_2')
                    tap.not_in_ok(
                        'addition_tag', stowage.vars, 'no addition_tag')
                elif r.product_id == product2.product_id:
                    found.add(product2.product_id)
                    tap.eq(r.count, 7, 'количество')
                    tap.eq(
                        stowage.vars['tag'],
                        stowage_tag,
                        'теги для perishable не склеиваются')
                    tap.eq(
                        stowage.vars['addition_tag'],
                        'perishable',
                        'скоропортящиеся'
                    )
                elif r.product_id == product3.product_id:
                    found.add(product3.product_id)
                    tap.eq(r.count, 3, 'количество')
                    tap.eq(
                        stowage.vars['tag'],
                        stowage_tag,
                        'теги для perishable не склеиваются')
                    tap.eq(
                        stowage.vars['addition_tag'],
                        'perishable',
                        'скоропортящиеся'
                    )
        tap.in_ok(product1.product_id, found, '1 продукт есть')
        tap.in_ok(product2.product_id, found, '2 продукт есть')
        tap.in_ok(product3.product_id, found, '3 продукт есть')


# pylint: disable=too-many-locals
@pytest.mark.parametrize(
    'tags_1, tags_2, stowage_tag',
    [(['refrigerator'], [], 'mixed'),
     (['refrigerator'], ['refrigerator'], 'refrigerator')])
async def test_office_stowage(
    tap, dataset, wait_order_status, cfg, tags_1, tags_2, stowage_tag
):
    with tap.plan(
        20, f'раскладка товаров внутренних нужд с тегом {stowage_tag}'
    ):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        store = await dataset.full_store(
            options={
                'exp_perishable_food': True,
                'exp_illidan': True,
            }
        )
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product1 = await dataset.product(
            tags=['freezer2_2'],
            vars={'imported': {'nomenclature_type': 'product'}}
        )

        product2 = await dataset.product(
            tags=tags_1,
            vars={'imported': {'nomenclature_type': 'consumable'}}
        )

        product3 = await dataset.product(
            tags=tags_2,
            vars={'imported': {'nomenclature_type': 'consumable'}}
        )

        order = await dataset.order(
            type='acceptance',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 22,
                },
                {
                    'product_id': product2.product_id,
                    'count': 7,
                },
                {
                    'product_id': product3.product_id,
                    'count': 3,
                },
            ],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'Ордер создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.isa_ok(order.vars['stowage_id'], list, 'список дочек')
        tap.eq(len(order.vars['stowage_id']), 2, 'две дочки')

        found = set()

        for order_id in order.vars['stowage_id']:
            stowage = await dataset.Order.load(order_id)
            tap.eq(stowage.store_id, store.store_id, 'раскладка загружена')
            for r in stowage.required:
                if r.product_id == product1.product_id:
                    found.add(product1.product_id)
                    tap.eq(r.count, 22, 'количество')
                    tap.eq(stowage.vars['tag'],
                           'freezer2_2',
                           'freezer2_2')
                    tap.not_in_ok(
                        'addition_tag', stowage.vars, 'no addition_tag')
                elif r.product_id == product2.product_id:
                    found.add(product2.product_id)
                    tap.eq(r.count, 7, 'количество')
                    tap.eq(
                        stowage.vars['tag'],
                        stowage_tag,
                        'теги для office не склеиваются')
                    tap.eq(
                        stowage.vars['addition_tag'],
                        'office',
                        'товары для внутренних нужд'
                    )
                elif r.product_id == product3.product_id:
                    found.add(product3.product_id)
                    tap.eq(r.count, 3, 'количество')
                    tap.eq(
                        stowage.vars['tag'],
                        stowage_tag,
                        'теги для office не склеиваются')
                    tap.eq(
                        stowage.vars['addition_tag'],
                        'office',
                        'товары для внутренних нужд'
                    )
        tap.in_ok(product1.product_id, found, '1 продукт есть')
        tap.in_ok(product2.product_id, found, '2 продукт есть')
        tap.in_ok(product3.product_id, found, '3 продукт есть')
