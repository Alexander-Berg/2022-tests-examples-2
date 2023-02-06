# pylint: disable=too-many-locals,too-many-statements
from easytap.pytest_plugin import PytestTap
import tests.dataset as dt


async def test_hand_move(tap: PytestTap, dataset: dt, uuid, api,
                         wait_order_status):
    with tap.plan(6, 'Тест ручного перемещения обычного товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        products = [await dataset.product() for _ in range(3)]
        tap.eq(len(products), 3, '3 обычных товара создано')

        shelves = [await dataset.shelf(store=store) for _ in range(3)]
        free_shelves = [await dataset.shelf(store=store) for _ in range(3)]
        tap.eq(len(shelves + free_shelves), 6, 'несколько полок создано')

        stocks_to_generate = [
            [products[0], shelves[0], 3],
            [products[1], shelves[1], 5],
            [products[0], shelves[2], 1]
        ]
        used = {}
        for product, shelf, count in stocks_to_generate:
            await dataset.stock(product=product, shelf=shelf,
                                store=store, count=count)
            used[(product.product_id, shelf.shelf_id)] = count

        stocks = {
            (s.product_id, s.shelf_id): s.count
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
            if s.count
        }
        tap.eq_ok(stocks, used, 'полки заполнены')

        t = await api(user=user)

        with tap.subtest(
                4,
                'Переместим два разных товара на одну полку'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            dst_shelf_id = free_shelves[1].shelf_id
            await t.post_ok('api_disp_orders_create',
                            json={
                                'external_id': external_id,
                                'type': 'hand_move',
                                'required': [
                                    {
                                        'product_id': products[0].product_id,
                                        'count': 1,
                                        'src_shelf_id': shelves[0].shelf_id,
                                        'dst_shelf_id': dst_shelf_id,
                                    },
                                    {
                                        'product_id': products[1].product_id,
                                        'count': 1,
                                        'src_shelf_id': shelves[1].shelf_id,
                                        'dst_shelf_id': dst_shelf_id,
                                    },
                                ],
                                'approved': True,
                                'ack': user.user_id,
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external'
            )

            await wait_order_status(order, ('processing', 'waiting'), tap=taps)


async def test_weight_hand_move(tap: PytestTap, dataset: dt, uuid, api,
                                wait_order_status):
    with tap.plan(10, 'Тест ручного перемещения весового товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        children_weights = [
            [0, 10],
            [10, 20],
            [20, 30]
        ]

        _, *products = await dataset.weight_products(
            children=children_weights)
        tap.eq(len(products), 3, '3 детей создано')

        shelves = [await dataset.shelf(store=store) for _ in range(3)]
        free_shelves = [await dataset.shelf(store=store) for _ in range(3)]
        tap.eq(len(shelves + free_shelves), 6, 'несколько полок создано')

        stocks_to_generate = [
            [products[0], shelves[0], 3],
            [products[1], shelves[1], 5],
            [products[0], shelves[2], 1]
        ]
        used = {}
        for product, shelf, count in stocks_to_generate:
            await dataset.stock(product=product, shelf=shelf,
                                store=store, count=count)
            used[(product.product_id, shelf.shelf_id)] = count

        stocks = {
            (s.product_id, s.shelf_id): s.count
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
            if s.count
        }
        tap.eq_ok(stocks, used, 'полки заполнены')

        t = await api(user=user)

        with tap.subtest(
                4,
                'Переместим часть весовой группы на свободную полку'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            dst_shelf_id = free_shelves[0].shelf_id
            await t.post_ok('api_disp_orders_create',
                            json={
                                'external_id': external_id,
                                'type': 'hand_move',
                                'required': [
                                    {
                                        'product_id': products[0].product_id,
                                        'count': 1,
                                        'src_shelf_id': shelves[0].shelf_id,
                                        'dst_shelf_id': dst_shelf_id,
                                    },
                                ],
                                'approved': True,
                                'ack': user.user_id,
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external'
            )
            await wait_order_status(order, ('processing', 'waiting'), tap=taps)

        with tap.subtest(
                4,
                'Переместим часть весовой группы на полку, '
                'занятую этой же весовой группой'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            await t.post_ok('api_disp_orders_create',
                            json={
                                'external_id': external_id,
                                'type': 'hand_move',
                                'required': [
                                    {
                                        'product_id': products[0].product_id,
                                        'count': 1,
                                        'src_shelf_id': shelves[0].shelf_id,
                                        'dst_shelf_id': shelves[2].shelf_id,
                                    },
                                ],
                                'approved': True,
                                'ack': user.user_id,
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external'
            )
            await wait_order_status(order, ('processing', 'waiting'), tap=taps)

        with tap.subtest(
                8,
                'Переместим часть весовой группы на полку, '
                'занятую другой весовой группой'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            dst_shelf_id = shelves[1].shelf_id
            await t.post_ok('api_disp_orders_create',
                            json={
                                'external_id': external_id,
                                'type': 'hand_move',
                                'required': [
                                    {
                                        'product_id': products[0].product_id,
                                        'count': 1,
                                        'src_shelf_id': shelves[0].shelf_id,
                                        'dst_shelf_id': dst_shelf_id,
                                    },
                                ],
                                'approved': True,
                                'ack': user.user_id,
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external'
            )

            await wait_order_status(order, ('failed', 'done'), tap=taps)
            await order.reload()
            taps.eq_ok(len(order.problems), 1, 'найдена одна ошибка')
            with order.problems[0] as p:
                taps.eq_ok(p.type, 'shelf_conflict_weight_product',
                           'тип ошибки верный')
                taps.eq_ok(p.shelf_id, dst_shelf_id, 'в ошибка верная полка')
                taps.eq_ok(p.product_id, products[0].product_id,
                           'в ошибке верный продукт')

        with tap.subtest(
                6 + 2 * 2,
                'Переместим две разные весовые группы на одну полку'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            dst_shelf_id = free_shelves[1].shelf_id
            await t.post_ok('api_disp_orders_create',
                            json={
                                'external_id': external_id,
                                'type': 'hand_move',
                                'required': [
                                    {
                                        'product_id': products[0].product_id,
                                        'count': 1,
                                        'src_shelf_id': shelves[0].shelf_id,
                                        'dst_shelf_id': dst_shelf_id,
                                    },
                                    {
                                        'product_id': products[1].product_id,
                                        'count': 1,
                                        'src_shelf_id': shelves[1].shelf_id,
                                        'dst_shelf_id': dst_shelf_id,
                                    },
                                ],
                                'approved': True,
                                'ack': user.user_id,
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external'
            )

            await wait_order_status(order, ('failed', 'done'), tap=taps)
            await order.reload()
            taps.eq_ok(len(order.problems), 2, 'найдено две ошибки')

            problem_products = set()
            for problem in order.problems:
                taps.eq_ok(problem.type, 'shelf_conflict_weight_product',
                           'тип ошибки верный')
                taps.eq_ok(problem.shelf_id, dst_shelf_id,
                           'в ошибке верная полка')
                problem_products.add(problem.product_id)
            taps.eq_ok(
                problem_products,
                {products[0].product_id, products[1].product_id},
                'для каждого товара сгенерировалась ошибка'
            )

        with tap.subtest(
                4,
                'Переместим две части весовой группы на одну полку'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            dst_shelf_id = free_shelves[2].shelf_id
            await t.post_ok('api_disp_orders_create',
                            json={
                                'external_id': external_id,
                                'type': 'hand_move',
                                'required': [
                                    {
                                        'product_id': products[0].product_id,
                                        'count': 1,
                                        'src_shelf_id': shelves[0].shelf_id,
                                        'dst_shelf_id': dst_shelf_id,
                                    },
                                    {
                                        'product_id': products[0].product_id,
                                        'count': 1,
                                        'src_shelf_id': shelves[2].shelf_id,
                                        'dst_shelf_id': dst_shelf_id,
                                    },
                                ],
                                'approved': True,
                                'ack': user.user_id,
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external'
            )
            await wait_order_status(order, ('processing', 'waiting'), tap=taps)


async def test_hand_move_by_collect(tap, dataset, wait_order_status):
    with tap.plan(11, 'Проверим успешное перемещние нескольких весовоых групп '
                      'на одну полку во время сборки в РЦ'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        children_weights = [
            [0, 10],
            [10, 20],
            [20, 30]
        ]

        _, *products = await dataset.weight_products(
            children=children_weights)
        tap.eq(len(products), 3, '3 детей создано')

        shelves = [await dataset.shelf(store=store) for _ in range(3)]
        free_shelves = [await dataset.shelf(store=store) for _ in range(3)]
        tap.eq(len(shelves + free_shelves), 6, 'несколько полок создано')

        stocks_to_generate = [
            [products[0], shelves[0], 3],
            [products[1], shelves[1], 5],
            [products[0], shelves[2], 1]
        ]
        used = {}
        for product, shelf, count in stocks_to_generate:
            await dataset.stock(product=product, shelf=shelf,
                                store=store, count=count)
            used[(product.product_id, shelf.shelf_id)] = count

        stocks = {
            (s.product_id, s.shelf_id): s.count
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
            if s.count
        }
        tap.eq_ok(stocks, used, 'полки заполнены')

        collect = await dataset.order(
            type='collect',
            store=store,
            required=[
                {
                    'product_id': products[0].product_id,
                    'count': 3,
                },
                {
                    'product_id': products[1].product_id,
                    'count': 5,
                }
            ]
        )
        await wait_order_status(collect, ('processing', 'waiting_stocks'))

        tap.eq(
            await collect.business.make_wave(split=False),
            1,
            'make_wave создала один ордер'
        )

        children = [
            await dataset.Order.load(oid)
            for oid in collect.vars('hand_move', [])
        ]

        tap.eq(len(children), 1, 'один дочерний ордер')
        with children[0] as hand_move_order:
            tap.eq(hand_move_order.parent, [collect.order_id], 'parent')
            tap.eq(hand_move_order.type, 'hand_move', 'type')
            await wait_order_status(hand_move_order, ('request', 'waiting'))
