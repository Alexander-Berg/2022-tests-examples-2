import pytest


async def test_products_without_stocks(tap, dataset, wait_order_status):
    with tap.plan(3, 'Попадаем в failed если продукт не нашли'):
        store = await dataset.full_store(options={'exp_condition_zero': False})
        check_shelf = await dataset.shelf(type='store', store=store)

        product_one = await dataset.product()
        await dataset.stock(store=store, product=product_one, count=0)
        product_two = await dataset.product()
        product_three = await dataset.product()
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
                {
                    'product_id': product_three.product_id,
                    'shelf_id': check_shelf.shelf_id,
                }
            ],
            store=store,
            status='reserving',
            estatus='begin',
        )
        await wait_order_status(order, ('failed', 'done'))
        await order.reload()
        tap.eq(len(order.problems), 2, 'Две проблемы')
        tap.eq(
            {
                (
                    problem.product_id, problem.type
                )
                for problem in order.problems
            },
            {
                (product_two.product_id, 'stock_not_found_for_product'),
                (product_three.product_id, 'stock_not_found_for_product')
            },
            'Правильные проблемы'
        )


@pytest.mark.parametrize('check_shelf, expected_shelves', [
    ('store', {'lost', 'found'}),
    ('kitchen_components', {'kitchen_lost', 'kitchen_found'}),
])
async def test_failed(
        tap, dataset, wait_order_status, check_shelf, expected_shelves):
    with tap.plan(10, 'Статус failed при отсутствии lost'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        check_shelf = await dataset.shelf(type=check_shelf, store=store)
        tap.eq(check_shelf.store_id, store.store_id, 'полка создана')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            type='check',
            shelves=[check_shelf.shelf_id],
            products=[product.product_id],
            required=[{
                'product_id': product.product_id,
                'shelf_id': check_shelf.shelf_id,
            }],
            store=store,
            status='reserving',
            estatus='begin',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')
        tap.eq(order.type, 'check', 'тип')

        await wait_order_status(order, ('failed', 'done'))
        await order.reload()

        tap.eq(
            len(order.problems),
            len(expected_shelves),
            'Нужное количество проблем'
        )
        tap.ok(
            all(p.type == 'shelf_not_found' for p in order.problems),
            'Все проблемы про потерю полки'
        )
        tap.eq(
            {p.shelf_type for p in order.problems},
            set(expected_shelves),
            'Типы полок правильные'
        )

async def test_duplicate_in_required(tap, dataset, wait_order_status):
    with tap.plan(8, 'нахождение дубликатов в required'):

        product = await dataset.product()
        tap.ok(product, 'товар 2 сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'Склад сгенерирован')

        shelf = await dataset.shelf(store=store, type='store')
        tap.ok(shelf, 'полки сгенерированы')

        order = await dataset.order(
            store=store,
            type='check',
            target='complete',
            required=[
                {
                    'product_id': product.product_id,
                    'shelf_id': shelf.shelf_id
                },
                {
                    'product_id': product.product_id,
                    'shelf_id': shelf.shelf_id
                },
            ],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('reserving', 'gen_required'))
        await order.business.order_changed()
        tap.eq(order.fstatus, ('failed', 'begin'), 'обнаружены дубликаты')
        tap.eq(order.problems[0].type, 'required_duplicate',
               'Проблема верно определена')
        tap.ne_ok(len(order.problems), 0, 'проблемы были записаны')


async def test_duplicate_shelves(tap, dataset, wait_order_status):
    with tap.plan(7, 'пустой required, дубликаты в парах полка + продукт'):
        product = await dataset.product()
        tap.ok(product, 'товар 1 сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'Склад сгенерирован')

        shelf = await dataset.shelf(store=store, type='store')
        tap.ok(shelf, 'полки сгенерированы')

        order4 = await dataset.order(
            store=store,
            type='check',
            target='complete',
            shelves=[shelf.shelf_id, shelf.shelf_id],
            products=[product.product_id, product.product_id]
        )
        tap.eq(order4.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order4, ('reserving', 'gen_required'))
        await order4.business.order_changed()
        tap.eq(order4.fstatus, ('failed', 'begin'), 'обнаружены дубликаты')
        tap.ne_ok(len(order4.problems), 0, 'проблемы были записаны')


async def test_diff_length(tap, dataset, wait_order_status):
    with tap.plan(8, 'пустой required, дубликаты в парах полка + продукт'):
        product = await dataset.product()
        tap.ok(product, 'товар 1 сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'Склад сгенерирован')

        shelf = await dataset.shelf(store=store, type='store')
        tap.ok(shelf, 'полки сгенерированы')

        order = await dataset.order(
            store=store,
            type='check',
            target='complete',
            shelves=[shelf.shelf_id, shelf.shelf_id],
            products=[product.product_id]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('reserving', 'gen_required'))
        await order.business.order_changed()
        tap.eq(order.fstatus, ('failed', 'begin'),
               'разная длина у shelves и products')
        tap.eq(order.problems[0].type, 'invalid_order_format',
               'Проблема верно определена')
        tap.ne_ok(len(order.problems), 0, 'проблемы были записаны')


async def test_mixed_required(tap, dataset, uuid, wait_order_status):
    with tap.plan(3, 'проверяем отвал на плохом required'):
        store = await dataset.full_store()
        order = await dataset.order(
            type='check',
            required=[
                {'product_id': uuid()},
                {'product_id': uuid(), 'shelf_id': uuid()},
            ],
            store=store,
            status='reserving',
            estatus='begin',
        )

        await wait_order_status(order, ('failed', 'begin'))
        await order.reload()
        tap.eq(len(order.problems), 1, 'одна проблема')
        tap.eq(order.problems[0].type, 'required_type_mix', 'та самая')


async def test_required_too_big(tap, dataset, cfg, wait_order_status):
    with tap.plan(3, 'проверяем отвал на плохом required'):
        cfg.set('business.order.check.products_count_limit', 5)
        store = await dataset.full_store()
        order = await dataset.order(
            type='check',
            required=[
                {'product_id': str(i)}
                for i in range(6)
            ],
            store=store,
            status='reserving',
            estatus='begin',
        )

        await wait_order_status(order, ('failed', 'begin'))
        await order.reload()
        tap.eq(len(order.problems), 1, 'одна проблема')
        tap.eq(order.problems[0].type, 'required_too_big', 'та самая')
