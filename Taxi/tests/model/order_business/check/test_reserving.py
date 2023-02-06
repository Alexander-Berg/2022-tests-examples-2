import pytest


async def test_noack(tap, dataset, wait_order_status):
    with tap.plan(10, 'Переходы до request без ack в старте'):
        store = await dataset.store()
        stock = await dataset.stock(store=store)
        order = await dataset.order(
            store=store,
            type='check',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': stock.shelf_id,
                    'product_id': stock.product_id,
                }
            ]
        )

        lf = await dataset.shelf(type='lost',
                                 store_id=order.store_id)
        tap.eq(lf.store_id, order.store_id, 'полка lost создана')
        tap.eq(lf.type, 'lost', 'тип')
        found = await dataset.shelf(type='found',
                                    store_id=order.store_id)
        tap.eq(found.store_id, order.store_id, 'полка lost создана')
        tap.eq(found.type, 'found', 'тип')

        tap.ok(order, 'ордер создан')
        tap.eq(order.status, 'reserving', 'резервируется')
        tap.eq(order.estatus, 'begin', 'начало')
        tap.eq(order.type, 'check', 'тип')

        await wait_order_status(order, ('reserving', 'processing_ack'))
        await wait_order_status(order, ('request', 'begin'))


async def test_ack(tap, dataset, wait_order_status):
    with tap.plan(10, 'Переходы до processing с ack в старте'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')

        stock = await dataset.stock(store=store)
        order = await dataset.order(
            store=store,
            type='check',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': stock.shelf_id,
                    'product_id': stock.product_id,
                }
            ],
            acks=[user.user_id]
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.status, 'reserving', 'резервируется')
        tap.eq(order.estatus, 'begin', 'начало')
        tap.eq(order.type, 'check', 'тип')
        tap.eq(order.store_id, user.store_id, 'на складе')

        lf = await dataset.shelf(type='lost',
                                 store_id=order.store_id)
        tap.eq(lf.store_id, order.store_id, 'полка lost создана')
        tap.eq(lf.type, 'lost', 'тип')

        found = await dataset.shelf(type='found',
                                    store_id=order.store_id)
        tap.eq(found.store_id, order.store_id, 'полка lost создана')
        tap.eq(found.type, 'found', 'тип')

        await wait_order_status(order, ('processing', 'begin'))


@pytest.mark.parametrize('req_shelf_type, created_shelves, problem_shelves', [
    (
        'store',
        ['store', 'kitchen_lost', 'found'],
        {'lost'},
    ),
    (
        'kitchen_components',
        ['kitchen_components', 'lost', 'found'],
        {'kitchen_lost', 'kitchen_found'},
    ),
])
async def test_fail_shelf(
        tap, dataset, wait_order_status,
        req_shelf_type, created_shelves, problem_shelves):
    with tap.plan(10, 'Проверяем необходимые полки'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')
        check_shelf = await dataset.shelf(type='store', store=store)
        tap.ok(check_shelf, 'Полка создана для проверки')

        shelves = []
        for shelf_type in created_shelves:
            shelf = await dataset.shelf(type=shelf_type, store=store)
            tap.eq(
                shelf.store_id,
                store.store_id,
                f'Создана полка {shelf_type}'
            )
            shelves.append(shelf.shelf_id)
        stock = await dataset.stock(store=store, shelf_type=req_shelf_type)
        order = await dataset.order(
            store=store,
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': stock.shelf_id,
                    'product_id': stock.product_id,
                }
            ],
            type='check',
            acks=[user.user_id],
        )

        await wait_order_status(order, ('failed', 'done'))

        tap.eq(
            len(order.problems),
            len(problem_shelves),
            'Найдено нужное количество проблем'
        )
        tap.ok(
            all(p.type == 'shelf_not_found' for p in order.problems),
            'Все типы проблем shelf_not_found'
        )
        tap.eq(
            {p.shelf_type for p in order.problems},
            problem_shelves,
            'В проблемах правильные типы полок'
        )


async def test_products_with_stocks(
        tap, dataset, wait_order_status):
    with tap.plan(3, 'Проверка продуктов проходит успешно'):
        store = await dataset.full_store()
        check_shelf = await dataset.shelf(type='store', store=store)
        product_one = await dataset.product()
        await dataset.stock(store=store, product=product_one, count=0)
        product_two = await dataset.product()
        await dataset.stock(store=store, product=product_two, count=2)
        order = await dataset.order(
            type='check',
            required=[
                {
                    'product_id': product_one.product_id,
                    'shelf_id': check_shelf.shelf_id,
                },
                {
                    'product_id': product_two.product_id,
                    'shelf_id': check_shelf.shelf_id,
                },
            ],
            store=store,
            status='reserving',
            estatus='begin',
        )
        await wait_order_status(order, ('request', 'waiting'))
        tap.eq(len(order.problems), 0, 'Проблем нет')
        tap.eq(order.status, 'request', 'Успешно прошли резерв')


async def test_products_no_stocks_parent(tap, dataset, wait_order_status):
    with tap.plan(3, 'Проверки продуктов нет из-за родителя'):
        store = await dataset.full_store()
        check_shelf = await dataset.shelf(type='store', store=store)
        product_one = await dataset.product()
        product_two = await dataset.product()
        parent_order = await dataset.order(type='check_product_on_shelf')
        order = await dataset.order(
            type='check',
            required=[
                {
                    'product_id': product_one.product_id,
                    'shelf_id': check_shelf.shelf_id,
                },
                {
                    'product_id': product_two.product_id,
                    'shelf_id': check_shelf.shelf_id,
                },
            ],
            store=store,
            status='reserving',
            estatus='begin',
            parent=[parent_order.order_id]
        )
        await wait_order_status(order, ('request', 'waiting'))
        await order.reload()
        tap.eq(len(order.problems), 0, 'Проблем нет')
        tap.eq(order.status, 'request', 'Успешно прошли резерв')


async def test_child_product_assortment(
        tap, dataset, uuid, wait_order_status
):
    with tap.plan(2, 'родительский товар в ассортименте'):
        store = await dataset.full_store(options={'exp_schrodinger': True})
        shelf = await dataset.shelf(store=store)
        parent_order = await dataset.order(
            store=store,
            type='acceptance',
            attr={'contractor_id': uuid()}
        )
        parent_product = await dataset.product()
        product = await dataset.product(parent_id=parent_product.product_id)
        assortment = await dataset.assortment_contractor(
            store=store, contractor_id=parent_order.attr['contractor_id']
        )
        await dataset.assortment_contractor_product(
            assortment=assortment, product=parent_product
        )
        order = await dataset.order(
            store_id=store.store_id,
            parent=[parent_order.order_id],
            type='check',
            required=[{
                'shelf_id': shelf.shelf_id,
                'product_id': product.product_id,
            }]
        )
        await wait_order_status(order, ('request', 'waiting'))
        await order.reload()
        tap.eq(
            order.problems,
            [],
            'Проблем нет, нашли в ассортименте'
        )
