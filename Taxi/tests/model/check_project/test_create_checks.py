from datetime import timedelta

import pytz

from stall.model.check_project import job_main
from stall.model.order import Order


async def get_orders_by_project(check_project_id, store_id=None):
    conditions = [('type', 'check')]
    if store_id:
        conditions.append(('store_id', store_id))
    orders = (await Order.list(by='full', conditions=conditions)).list
    if isinstance(check_project_id, str):
        orders = [
            o
            for o in orders
            if o.vars.get('check_project_id') == check_project_id
        ]
    elif isinstance(check_project_id, list):
        orders = [
            o
            for o in orders
            if any(
                o.vars.get('check_project_id') == cp_id
                for cp_id in check_project_id
            )
        ]
    return orders


async def test_create_checks_happy_flow(tap, dataset, now, wait_order_status):
    with tap.plan(6, 'тестим хеппи флоу'):
        store = await dataset.store(options={'exp_big_brother': True})
        stock = await dataset.stock(store=store)
        _now = now()
        cp = await dataset.check_project(
            product_id=stock.product_id,
            store_id=store.store_id,
            schedule={
                'timetable': [{
                    'type': 'everyday',
                    'begin': _now.time().replace(
                        minute=0, second=0, microsecond=0,
                    ),
                    'end': _now.time().replace(
                        minute=0, second=0, microsecond=0,
                    ),
                }],
                'begin': _now,
                'end': _now + timedelta(days=2),
            }
        )

        await job_main(_now, [cp.check_project_id])

        created_order = await get_orders_by_project(
            cp.check_project_id, store.store_id,
        )
        tap.eq(len(created_order), 1, 'найден один ордер')
        created_order = created_order[0]

        tap.eq(created_order.type, 'check', 'нужный тип')
        tap.eq(created_order.source, 'internal', 'нужный сорс')
        tap.eq(
            created_order.required,
            [{'product_id': stock.product_id}],
            'нужный required',
        )

        user = await dataset.user(store_id=stock.store_id)
        await wait_order_status(created_order, ('request', 'waiting'))
        await created_order.ack(user)
        await wait_order_status(
            created_order, ('complete', 'done'), user_done=user,
        )


async def test_create_checks_filter(tap, dataset, now, uuid):
    with tap.plan(2, 'проверяем фильтрацию и закрытие проектов'):
        store = await dataset.store(options={'exp_big_brother': True})
        _now = now()
        now_yesterday = _now - timedelta(days=1)
        now_tommorow = now_yesterday + timedelta(days=2)
        cp1 = await dataset.check_project(
            store_id=store.store_id,
            product_id=uuid(),
            schedule={
                'timetable': [],
                'begin': now_yesterday,
                'end': now_yesterday,
            },
        )
        cp2 = await dataset.check_project(
            store_id=store.store_id,
            product_id=uuid(),
            schedule={
                'timetable': [],
                'begin': now_tommorow,
                'end': now_tommorow,
            },
        )

        cp_ids = [cp.check_project_id for cp in (cp1, cp2)]
        await job_main(_now, cp_ids)

        created_order = await get_orders_by_project(cp_ids, store.store_id)
        tap.eq(len(created_order), 0, 'ордеров нет')

        await cp1.reload()
        tap.eq(cp1.status, 'disabled', 'выключили проект')


async def test_create_checks_day(tap, dataset, now):
    with tap.plan(1, 'тестим попадание в день'):
        _now = now()
        store = await dataset.store(options={'exp_big_brother': True})
        stock = await dataset.stock(store=store)
        cps = [
            await dataset.check_project(
                store_id=store.store_id,
                product_id=stock.product_id,
                schedule={
                    'timetable': [{
                        'type': 'everyday',
                        'begin': _now.time(),
                        'end': _now.time(),
                    }],
                    'begin': _now + timedelta(days=i),
                    'end': _now + timedelta(days=i),
                },
            )
            for i in (-1, 0, 1)
        ]

        cp_ids = [cp.check_project_id for cp in cps]
        await job_main(_now, cp_ids)

        created_order = await get_orders_by_project(cp_ids, store.store_id)
        tap.eq(len(created_order), 1, 'один ордер: i=0')


async def test_create_checks_timezones(tap, dataset, now):
    # pylint: disable=too-many-locals
    with tap.plan(4, 'тестим выбор запускаемых локалок'):
        tz1 = pytz.timezone('Europe/London')
        tz2 = pytz.timezone('America/New_York')
        now1 = now(tz1)
        now2 = now1.astimezone(tz2)

        store1 = await dataset.store(
            tz=str(tz1), options={'exp_big_brother': True},
        )
        store2 = await dataset.store(
            tz=str(tz2), options={'exp_big_brother': True},
        )
        store3 = await dataset.store(options={'exp_big_brother': True})
        product = await dataset.product()

        cps = [
            await dataset.check_project(
                store_id=store1.store_id,
                product_id=product.product_id,
                schedule={
                    'timetable': [{
                        'type': 'everyday',
                        'begin': now1.time(),
                        'end': now1.time(),
                    }],
                    'begin': now() - timedelta(days=3),
                    'end': now() + timedelta(days=3),
                }
            ),
            await dataset.check_project(
                stores={
                    'store_id': [s.store_id for s in (store2, store3)],
                },
                product_id=product.product_id,
                schedule={
                    'timetable': [],
                    'begin': now2,
                    'end': now2,
                }
            ),
        ]

        cp_ids = [cp.check_project_id for cp in cps]
        await job_main(now1, cp_ids)

        created_order = await get_orders_by_project(
            cp_ids, [s.store_id for s in (store1, store2, store3)],
        )
        tap.eq(len(created_order), 2, 'создано два ордера')
        tap.eq(
            {o.store_id for o in created_order},
            {s.store_id for s in (store1, store2)},
            'по локалке на 1 и 2 лавку',
        )
        store1_order = [
            o for o in created_order if o.store_id == store1.store_id
        ][0]
        store2_order = [
            o for o in created_order if o.store_id == store2.store_id
        ][0]
        tap.eq(
            store1_order.vars['check_project_id'],
            cps[0].check_project_id,
            'нужный проект'
        )
        tap.eq(
            store2_order.vars['check_project_id'],
            cps[1].check_project_id,
            'нужный проект',
        )


async def test_create_orders_double(tap, dataset, now):
    with tap.plan(8, 'не создаем ордер если уже есть, а старый пересоздаем'):
        store = await dataset.store(options={'exp_big_brother': True})
        store2 = await dataset.store()
        stock = await dataset.stock(store=store)
        stock2 = await dataset.stock(store=store2)
        _now = now()
        cp = await dataset.check_project(
            product_id=stock.product_id,
            stores={'store_id': [stock.store_id, stock2.store_id]},
            schedule={
                'timetable': [{
                    'type': 'everyday',
                    'begin': _now.time(),
                    'end': _now.time(),
                }],
                'begin': _now,
            },
        )

        cp_id = cp.check_project_id
        await job_main(_now, [cp_id])

        old_order = await get_orders_by_project(cp_id, store.store_id)
        tap.eq(len(old_order), 1, 'ордер создался')
        old_order = old_order[0]

        options = store2.options.copy()
        options['exp_big_brother'] = True
        store2.options = options
        await store2.save()
        await store2.reload()
        tap.ok(store2.options.get('exp_big_brother'), 'эксперимент включен')
        await job_main(_now, [cp_id])

        created_order1 = await get_orders_by_project(cp_id, store.store_id)
        created_order2 = await get_orders_by_project(cp_id, store2.store_id)
        tap.eq(len(created_order1), 1, 'найден один ордер для первой лавки')
        created_order = created_order1[0]
        tap.eq(created_order.order_id, old_order.order_id, 'тот же ордер')
        tap.eq(len(created_order2), 1, 'для другой лавки тоже создался')

        await job_main(_now + timedelta(days=1), [cp_id])
        created_order1 = await get_orders_by_project(cp_id, store.store_id)
        tap.eq(len(created_order1), 2, 'найдено два ордер для первой лавки')
        created_order1 = [o for o in created_order1 if o.target != 'canceled']
        tap.eq(len(created_order1), 1, 'но только один не в отмене')
        await old_order.reload()
        tap.eq(old_order.target, 'canceled', 'а старый в отмене')


async def test_create_orders_shelf_type(tap, dataset, now, wait_order_status):
    with tap.plan(17, 'тестируем прокидывание shelf_types'):
        store = await dataset.store(options={'exp_big_brother': True})
        stock_store = await dataset.stock(store=store)
        stock_office = await dataset.stock(store=store, shelf_type='office')
        _now = now()
        cps = [
            await dataset.check_project(
                products={
                    'product_id': [
                        stock_store.product_id, stock_office.product_id
                    ],
                },
                stores={'store_id': [store.store_id]},
                schedule={
                    'timetable': [{
                        'type': 'everyday',
                        'begin': _now.time(),
                        'end': _now.time(),
                    }],
                    'begin': _now,
                },
                shelf_types=st,
            )
            for st in ([], ['store'], ['kitchen_on_demand'])
        ]

        await job_main(_now, [cp.check_project_id for cp in cps])

        orders = [
            await get_orders_by_project(cp.check_project_id, store.store_id)
            for cp in cps
        ]
        tap.ok(all(o for o in orders), 'везде найдены ордера')
        tap.eq(sum(len(o) for o in orders), 3, 'создано три ордера')
        all_order = orders[0][0]
        store_order = orders[1][0]
        fail_order = orders[2][0]
        user = await dataset.user(store=store)

        await wait_order_status(all_order, ('request', 'waiting'))
        await all_order.ack(user)
        await wait_order_status(
            all_order, ('processing', 'suggests_generate'), user_done=user,
        )
        await wait_order_status(
            all_order, ('processing', 'waiting'), user_done=user,
        )
        suggests = await dataset.Suggest.list_by_order(all_order)
        tap.eq(len(suggests), 2, 'два саджеста')
        tap.eq(
            {s.shelf_id for s in suggests},
            {stock_store.shelf_id, stock_office.shelf_id},
            'все полки',
        )
        await wait_order_status(
            all_order, ('complete', 'done'), user_done=user,
        )

        await wait_order_status(store_order, ('request', 'waiting'))
        await store_order.ack(user)
        await wait_order_status(
            store_order, ('processing', 'suggests_generate'), user_done=user,
        )
        await wait_order_status(
            store_order, ('processing', 'waiting'), user_done=user,
        )
        suggests = await dataset.Suggest.list_by_order(store_order)
        tap.eq(len(suggests), 1, 'один саджеста')
        tap.eq(suggests[0].shelf_id, stock_store.shelf_id, 'store полка')
        await wait_order_status(
            store_order, ('complete', 'done'), user_done=user,
        )

        await wait_order_status(fail_order, ('request', 'waiting'))
        await fail_order.ack(user)
        await wait_order_status(
            fail_order, ('processing', 'suggests_generate'), user_done=user,
        )
        with tap.raises(AssertionError):
            await wait_order_status(
                fail_order, ('processing', 'waiting'), user_done=user,
            )


async def test_create_checks_big_req(tap, dataset, now, cfg):
    with tap.plan(1, 'проверяем что не создается чек с большим required'):
        cfg.set('business.order.check.products_count_limit', 3)
        store = await dataset.store(options={'exp_big_brother': True})
        _now = now()
        products = [await dataset.product() for _ in range(4)]

        cp = await dataset.check_project(
            products={
                'product_id': [product.product_id for product in products],
            },
            stores={'store_id': [store.store_id]},
            schedule={
                'timetable': [{
                    'type': 'everyday',
                    'begin': _now.time(),
                    'end': _now.time(),
                }],
                'begin': _now,
            },
        )
        await job_main(_now, [cp.check_project_id])
        created_orders = await get_orders_by_project(
            cp.check_project_id, store.store_id,
        )
        tap.ok(not created_orders, 'ордеры не созданы')


async def test_checks_removed_products(tap, dataset, now, cfg):
    with tap.plan(1, 'Если продукты стали удалены, то документ не создается'):
        cfg.set('business.order.check.products_count_limit', 5)
        store = await dataset.store(options={'exp_big_brother': True})
        _now = now()
        products = [
            await dataset.product(status='removed')
            for _ in range(3)
        ]

        cp = await dataset.check_project(
            products={
                'product_id': [product.product_id for product in products],
            },
            stores={'store_id': [store.store_id]},
            schedule={
                'timetable': [{
                    'type': 'everyday',
                    'begin': _now.time(),
                    'end': _now.time(),
                }],
                'begin': _now,
            },
        )
        await job_main(_now, [cp.check_project_id])
        created_orders = await get_orders_by_project(
            cp.check_project_id, store.store_id,
        )
        tap.ok(not created_orders, 'ордеры не созданы')


async def test_checks_scope_products(tap, dataset, now, cfg):
    with tap.plan(1, 'Если продукты не в скоупе, то документ не создается'):
        cfg.set('business.order.check.products_count_limit', 5)
        company = await dataset.company(products_scope=['russia'])
        store = await dataset.store(
            options={'exp_big_brother': True},
            company=company,
        )
        _now = now()
        products = [
            await dataset.product(products_scope=['israel'])
            for _ in range(3)
        ]

        cp = await dataset.check_project(
            products={
                'product_id': [product.product_id for product in products],
            },
            stores={'store_id': [store.store_id]},
            schedule={
                'timetable': [{
                    'type': 'everyday',
                    'begin': _now.time(),
                    'end': _now.time(),
                }],
                'begin': _now,
            },
        )
        await job_main(_now, [cp.check_project_id])
        created_orders = await get_orders_by_project(
            cp.check_project_id, store.store_id,
        )
        tap.ok(not created_orders, 'ордеры не созданы')


async def test_checks_kitchen_products(tap, dataset, now, cfg):
    with tap.plan(
        1,
        'Если продукты получили рецепты, то документ не создается'
    ):
        cfg.set('business.order.check.products_count_limit', 5)
        store = await dataset.store(options={'exp_big_brother': True})
        _now = now()
        component = await dataset.product()
        products = [
            await dataset.product(components=[[
                {'product_id': component.product_id, 'count': 1}
            ]])
            for _ in range(3)
        ]

        cp = await dataset.check_project(
            products={
                'product_id': [product.product_id for product in products],
            },
            stores={'store_id': [store.store_id]},
            schedule={
                'timetable': [{
                    'type': 'everyday',
                    'begin': _now.time(),
                    'end': _now.time(),
                }],
                'begin': _now,
            },
        )
        await job_main(_now, [cp.check_project_id])
        created_orders = await get_orders_by_project(
            cp.check_project_id, store.store_id,
        )
        tap.ok(not created_orders, 'ордеры не созданы')
