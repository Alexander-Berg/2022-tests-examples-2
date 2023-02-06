# pylint: disable=too-many-locals, too-many-statements

from stall.model.suggest import Suggest


async def test_no_errors(tap, dataset):
    with tap.plan(13, 'Ошибок нет'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='store')

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='processing',
            estatus='suggests_resolve',
            required = [
                {'product_id': product1.product_id, 'count': 1},
                {'product_id': product3.product_id, 'count': 3},
                {'product_id': product2.product_id, 'count': 2},
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_resolve', 'suggests_resolve')
        tap.eq(order.target, 'complete', 'target: complete')

        for product in (product1, product2, product3):
            suggest = await dataset.suggest(
                order,
                type='box2shelf',
                shelf_id=shelf.shelf_id,
                product_id=product.product_id,
            )
            tap.ok(suggest, f'suggest_id={suggest.suggest_id}')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')


async def test_error_like_shelf(tap, dataset):
    with tap.plan(23, 'Выбрали другую полку'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        shelf1 = await dataset.shelf(store=store, type='store')
        shelf2 = await dataset.shelf(store=store, type='store')
        shelf2_new = await dataset.shelf(store=store, type='store')
        shelf3 = await dataset.shelf(store=store, type='store')

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='processing',
            estatus='suggests_resolve',
            required = [
                {'product_id': product1.product_id, 'count': 1},
                {'product_id': product2.product_id, 'count': 2},
                {'product_id': product3.product_id, 'count': 3},
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_resolve', 'suggests_resolve')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest1 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf1.shelf_id,
            product_id=product1.product_id,
        )
        tap.ok(suggest1, f'suggest_id={suggest1.suggest_id}')

        suggest2 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf2.shelf_id,
            product_id=product2.product_id,
            status='error',
            reason={'code': 'LIKE_SHELF', 'shelf_id': shelf2_new.shelf_id},
        )
        tap.ok(suggest2, f'suggest_id={suggest2.suggest_id}')

        suggest3 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf3.shelf_id,
            product_id=product3.product_id,
        )
        tap.ok(suggest3, f'suggest_id={suggest3.suggest_id}')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')
        suggests = dict((s.product_id, s) for s in suggests)

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.suggest_id, suggest1.suggest_id, 'Саджест 1')
            tap.eq(suggest.status, 'request', 'Статус не менялся')
            tap.eq(suggest.shelf_id, shelf1.shelf_id, 'Полка не менялась')

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.suggest_id, suggest2.suggest_id, 'Саджест 2')
            tap.eq(suggest.status, 'request', 'Статус вернулся в request')
            tap.eq(suggest.reason, None, 'Ризон очищен')
            tap.eq(suggest.shelf_id, shelf2_new.shelf_id, 'Новая полка')

        with suggests[product3.product_id] as suggest:
            tap.eq(suggest.suggest_id, suggest3.suggest_id, 'Саджест 3')
            tap.eq(suggest.status, 'request', 'Статус не менялся')
            tap.eq(suggest.shelf_id, shelf3.shelf_id, 'Полка не менялась')


async def test_error_like_shelf_bad(tap, dataset):
    with tap.plan(23, 'Выбрали другую полку, но она не подходит'):

        product1 = await dataset.product()
        product2 = await dataset.product(tags=['freezer'])
        product3 = await dataset.product()

        store = await dataset.store()
        shelf1 = await dataset.shelf(store=store, type='store')
        shelf2 = await dataset.shelf(
            store=store,
            type='store',
            tags=['freezer'],
        )
        shelf2_new = await dataset.shelf(
            store=store,
            type='store',
            tags=['refrigerator']
        )
        shelf3 = await dataset.shelf(store=store, type='store')

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='processing',
            estatus='suggests_resolve',
            required = [
                {'product_id': product1.product_id, 'count': 1},
                {
                    'product_id': product2.product_id,
                    'count': 2,
                },
                {'product_id': product3.product_id, 'count': 3},
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_resolve', 'suggests_resolve')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest1 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf1.shelf_id,
            product_id=product1.product_id,
        )
        tap.ok(suggest1, f'suggest_id={suggest1.suggest_id}')

        suggest2 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf2.shelf_id,
            product_id=product2.product_id,
            status='error',
            reason={'code': 'LIKE_SHELF', 'shelf_id': shelf2_new.shelf_id},
        )
        tap.ok(suggest2, f'suggest_id={suggest2.suggest_id}')

        suggest3 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf3.shelf_id,
            product_id=product3.product_id,
        )
        tap.ok(suggest3, f'suggest_id={suggest3.suggest_id}')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')

        suggests = dict((s.product_id, s) for s in suggests)

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.suggest_id, suggest1.suggest_id, 'Саджест 1')
            tap.eq(suggest.status, 'request', 'Статус не менялся')
            tap.eq(suggest.shelf_id, shelf1.shelf_id, 'Полка не менялась')

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.suggest_id, suggest2.suggest_id, 'Саджест 2')
            tap.eq(suggest.status, 'request', 'Статус вернулся в request')
            tap.eq(suggest.reason, None, 'Ризон очищен')
            tap.eq(suggest.shelf_id, shelf2.shelf_id, 'Новая полка')

        with suggests[product3.product_id] as suggest:
            tap.eq(suggest.suggest_id, suggest3.suggest_id, 'Саджест 3')
            tap.eq(suggest.status, 'request', 'Статус не менялся')
            tap.eq(suggest.shelf_id, shelf3.shelf_id, 'Полка не менялась')


async def test_error_shelf_is_full(tap, dataset):
    with tap.plan(24, 'Полка полна, подбираем новую полку'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        shelf1 = await dataset.shelf(store=store, type='store')
        shelf2 = await dataset.shelf(store=store, type='store')
        shelf3 = await dataset.shelf(store=store, type='store')

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='processing',
            estatus='suggests_resolve',
            required = [
                {'product_id': product1.product_id, 'count': 1},
                {'product_id': product2.product_id, 'count': 2},
                {'product_id': product3.product_id, 'count': 3},
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_resolve', 'suggests_resolve')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest1 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf1.shelf_id,
            product_id=product1.product_id,
        )
        tap.ok(suggest1, f'suggest_id={suggest1.suggest_id}')

        suggest2 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf2.shelf_id,
            product_id=product2.product_id,
            status='error',
            reason={'code': 'SHELF_IS_FULL'},
        )
        tap.ok(suggest2, f'suggest_id={suggest2.suggest_id}')

        suggest3 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf3.shelf_id,
            product_id=product3.product_id,
        )
        tap.ok(suggest3, f'suggest_id={suggest3.suggest_id}')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')

        suggests = dict((s.product_id, s) for s in suggests)

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.suggest_id, suggest1.suggest_id, 'Саджест 1')
            tap.eq(suggest.status, 'request', 'Статус не менялся')
            tap.eq(suggest.shelf_id, shelf1.shelf_id, 'Полка не менялась')

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.suggest_id, suggest2.suggest_id, 'Саджест 2')
            tap.eq(suggest.status, 'request', 'Статус вернулся в request')
            tap.eq(suggest.reason, None, 'Ризон очищен')
            tap.in_ok(
                suggest.shelf_id,
                [shelf1.shelf_id, shelf3.shelf_id],
                'Новая полка'
            )

        with suggests[product3.product_id] as suggest:
            tap.eq(suggest.suggest_id, suggest3.suggest_id, 'Саджест 3')
            tap.eq(suggest.status, 'request', 'Статус не менялся')
            tap.eq(suggest.shelf_id, shelf3.shelf_id, 'Полка не менялась')

        with suggests[product2.product_id] as suggest:
            # Полки в которых уже подбирали
            #             excluded = [shelf2.shelf_id, suggest.shelf_id]

            suggest.status = 'error'
            suggest.reason = {'code': 'SHELF_IS_FULL'}
            tap.ok(await suggest.save(), 'Опять заполнена')

# TODO: сделать сохранение уже опробованных полок и расскоментировать этот
# тест
#         with order:
#             order.rehash(estatus='suggests_resolve')
#             await order.save()
#
#         await order.business.order_changed()
#
#         tap.ok(await order.reload(), 'Перезабрали заказ')
#         tap.eq(order.status, 'processing', 'processing')
#         tap.eq(order.estatus, 'waiting', 'waiting')
#         tap.eq(order.target, 'complete', 'target: complete')
#
#         tap.eq(len(order.problems), 0, 'Нет проблем')
#
#         suggests = await Suggest.list_by_order(order)
#         tap.eq(len(suggests), 3, 'Список саджестов')
#
#         with suggests[1] as suggest:
#             tap.eq(suggest.suggest_id, suggest2.suggest_id, 'Саджест 2')
#             tap.eq(suggest.status, 'request', 'Статус вернулся в request')
#             tap.eq(suggest.reason, None, 'Ризон очищен')
#             tap.not_in_ok(suggest.shelf_id, excluded, 'Новая полка')
