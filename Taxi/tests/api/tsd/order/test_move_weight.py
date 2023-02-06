# pylint: disable=too-many-locals,too-many-statements
from easytap.pytest_plugin import PytestTap
import tests.dataset as dt


async def test_non_weight_move(tap: PytestTap, dataset: dt, api, uuid,
                               wait_order_status):
    with tap.plan(10, 'Тест перемещения невесового товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='barcode_executer', store=store)
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

        external_id = uuid()
        dst_shelf_id = free_shelves[1].shelf_id
        await t.post_ok('api_tsd_order_move', json={
            'order_id': external_id,
            'move': [
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
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        order = await dataset.Order.load(
            (store.store_id, external_id),
            by='external',
        )
        r = await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.ok(r, 'Перемещение выполнено')


async def test_weight_move(tap: PytestTap, dataset: dt, api, uuid,
                           wait_order_status):
    with tap.plan(12, 'Тест перемещения весового товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='barcode_executer', store=store)
        tap.eq_ok(user.store_id, store.store_id, 'пользователь создан')

        children_weights = [
            [0, 10],
            [10, 20],
            [20, 30]
        ]

        _, *products = await dataset.weight_products(
            children=children_weights)
        tap.eq_ok(len(products), 3, '3 детей создано')

        shelves = [await dataset.shelf(store=store) for _ in range(3)]
        free_shelves = [await dataset.shelf(store=store) for _ in range(3)]
        tap.eq_ok(len(shelves + free_shelves), 6, 'несколько полок создано')
        trash_shelf = await dataset.Shelf.get_one(store_id=store.store_id,
                                                  type='trash')
        tap.ok(trash_shelf, 'Полка для списаний')

        stocks_to_generate = [
            [products[0], shelves[0], 5],
            [products[1], shelves[1], 7],
            [products[0], shelves[2], 3]
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
                5,
                'Переместим часть весовой группы на свободную полку'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            await t.post_ok('api_tsd_order_move', json={
                'order_id': external_id,
                'move': [
                    {
                        'product_id': products[0].product_id,
                        'count': 1,
                        'src_shelf_id': shelves[0].shelf_id,
                        'dst_shelf_id': free_shelves[0].shelf_id,
                    },
                ]
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external',
            )
            r = await wait_order_status(order, ('complete', 'done'), tap=taps,
                                        user_done=user)
            taps.ok(r, 'Перемещение выполнено')

        with tap.subtest(
                5,
                'Переместим часть весовой группы на полку, '
                'занятую этой же весовой группой'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            await t.post_ok('api_tsd_order_move', json={
                'order_id': external_id,
                'move': [
                    {
                        'product_id': products[0].product_id,
                        'count': 1,
                        'src_shelf_id': shelves[0].shelf_id,
                        'dst_shelf_id': shelves[2].shelf_id,
                    },
                ],
            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external'
            )
            r = await wait_order_status(order, ('complete', 'done'), tap=taps,
                                        user_done=user)
            check_stocks = {
                (s.product_id, s.shelf_id): s.count
                for s in await dataset.Stock.list_by_shelf(
                    shelf_id=shelves[2].shelf_id,
                    store_id=store.store_id
                )
            }
            taps.eq(
                check_stocks,
                {
                    (products[0].product_id, shelves[2].shelf_id): 4,
                },
                'Перемещение выполнено'
            )

        with tap.subtest(
                8,
                'Переместим часть весовой группы на полку, '
                'занятую другой весовой группой'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            dst_shelf_id = shelves[1].shelf_id
            await t.post_ok('api_tsd_order_move', json={
                'order_id': external_id,
                'move': [
                    {
                        'product_id': products[0].product_id,
                        'count': 1,
                        'src_shelf_id': shelves[0].shelf_id,
                        'dst_shelf_id': dst_shelf_id,
                    },
                ],
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external',
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
            await t.post_ok('api_tsd_order_move', json={
                'order_id': external_id,
                'move': [
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
                5,
                'Переместим две разные весовые группы на полку списания'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            dst_shelf_id = trash_shelf.shelf_id
            await t.post_ok('api_tsd_order_move', json={
                'order_id': external_id,
                'move': [
                    {
                        'product_id': products[0].product_id,
                        'count': 1,
                        'src_shelf_id': shelves[0].shelf_id,
                        'dst_shelf_id': dst_shelf_id,
                        'reason': {'code': 'TRASH_DAMAGE'},
                    },
                    {
                        'product_id': products[1].product_id,
                        'count': 1,
                        'src_shelf_id': shelves[1].shelf_id,
                        'dst_shelf_id': dst_shelf_id,
                        'reason': {'code': 'TRASH_DAMAGE'},
                    },
                ],
            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external'
            )

            r = await wait_order_status(order, ('complete', 'done'), tap=taps,
                                        user_done=user)
            check_stocks = {
                (s.product_id, s.shelf_id): s.count
                for s in await dataset.Stock.list_by_shelf(
                    shelf_id=dst_shelf_id,
                    store_id=store.store_id
                )
            }
            taps.eq(
                check_stocks,
                {
                    (products[0].product_id, dst_shelf_id): 1,
                    (products[1].product_id, dst_shelf_id): 1,
                },
                'Перемещение выполнено'
            )

        with tap.subtest(
                5,
                'Переместим две части весовой группы на одну полку'
        ) as taps:
            t.tap = taps
            external_id = uuid()
            dst_shelf_id = free_shelves[2].shelf_id
            await t.post_ok('api_tsd_order_move', json={
                'order_id': external_id,
                'move': [
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
            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            order = await dataset.Order.load(
                [store.store_id, external_id],
                by='external'
            )
            r = await wait_order_status(order, ('complete', 'done'), tap=taps,
                                        user_done=user)
            # TODO: Add check stocks
            taps.ok(r, 'Перемещение выполнено')
