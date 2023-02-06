import pytest

async def test_suggests(tap, dataset, wait_order_status):
    with tap.plan(18, 'Генерация саджестов'):
        store = await dataset.store(estatus='inventory')
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        product = await dataset.product()
        tap.ok(product, 'товар сгенерирован')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка сгенерирована')
        tap.ok(await dataset.shelf(
            store=store,
            type='lost',
        ), 'полка lost')

        tap.ok(await dataset.shelf(
            store=store,
            type='found',
        ), 'полка found')

        order = await dataset.order(
            store=store,
            type='inventory_check_product_on_shelf',
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': product.product_id,
                    'count': 27,
                }
            ],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'fstatus')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.eq(s.type, 'check', 'проверка')
            tap.eq(s.order_id, order.order_id, 'order_id')
            tap.eq(s.store_id, store.store_id, 'store_id')
            tap.eq(s.product_id, product.product_id, 'product_id')

            tap.ok(s.conditions.all, 'conditions.all')
            tap.ok(s.conditions.editable, 'conditions.editable')
            tap.ok(not s.conditions.need_valid, 'conditions.need_valid')
            tap.eq(s.count, 27, 'count из required')


async def test_err_product(tap, dataset, wait_order_status, uuid):
    with tap.plan(11, 'Неверный товар'):
        store = await dataset.store(estatus='inventory')
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка сгенерирована')
        tap.ok(await dataset.shelf(
            store=store,
            type='lost',
        ), 'полка lost')

        tap.ok(await dataset.shelf(
            store=store,
            type='found',
        ), 'полка found')

        order = await dataset.order(
            store=store,
            type='inventory_check_product_on_shelf',
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': uuid(),
                    'count': 27,
                }
            ],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'fstatus')

        await wait_order_status(order, ('failed', 'done'))
        tap.eq(len(order.problems), 1, 'одна проблема')
        with order.problems[0] as p:
            tap.eq(p.type, 'product_not_found', 'тип проблемы')
            tap.ok(p.product_id, 'product_id заполнен')


async def test_error_shelf(tap, dataset, wait_order_status, uuid):
    with tap.plan(13, 'Неверный номер полки'):
        store = await dataset.store(estatus='inventory')
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        product = await dataset.product()
        tap.ok(product, 'товар сгенерирован')
        tap.ok(await dataset.shelf(
            store=store,
            type='lost',
        ), 'полка lost')

        tap.ok(await dataset.shelf(
            store=store,
            type='found',
        ), 'полка found')

        order = await dataset.order(
            store=store,
            type='inventory_check_product_on_shelf',
            required=[
                {
                    'shelf_id': uuid(),
                    'product_id': product.product_id,
                    'count': 27,
                }
            ],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'fstatus')

        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'fstatus')

        await wait_order_status(order, ('failed', 'done'))
        tap.eq(len(order.problems), 1, 'одна проблема')
        with order.problems[0] as p:
            tap.eq(p.type, 'shelf_not_found', 'тип проблемы')
            tap.ok(p.shelf_id, 'shelf_id заполнен')


@pytest.mark.parametrize('problem_shelves, create_shelves, check_shelf', [
    (
        ['lost', 'found'],
        [],
        'store',
    ),
    (
        ['kitchen_lost'],
        ['kitchen_found'],
        'kitchen_components',
    ),
])
async def test_required_shelves(
        tap, dataset, wait_order_status,
        problem_shelves, create_shelves, check_shelf
):
    with tap:
        tap.note('Проверка необходимых полок')
        store = await dataset.store(estatus='inventory')
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        product = await dataset.product()
        tap.ok(product, 'товар сгенерирован')
        for shelf_type in create_shelves:
            shelf = await dataset.shelf(store=store, type=shelf_type)
            tap.ok(shelf, f'Создана полка типа {shelf_type}')

        check_shelf = await dataset.shelf(store=store, type=check_shelf)

        order = await dataset.order(
            store=store,
            type='inventory_check_product_on_shelf',
            required=[
                {
                    'shelf_id': check_shelf.shelf_id,
                    'product_id': product.product_id,
                    'count': 27,
                }
            ],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'fstatus')

        await wait_order_status(order, ('failed', 'done'))
        tap.ok(
            all(p.type == 'shelf_not_found' for p in order.problems),
            'Все проблемы про ненайденные полки'
        )
        tap.eq(len(order.problems), len(problem_shelves), 'Кол-во проблем')
        tap.eq(
            {problem.shelf_type for problem in order.problems},
            set(problem_shelves),
            'Типы полок верные'
        )
