import pytest

from stall.model.product_components import (
    ProductComponents, ProductVariant
)


async def test_problem(tap, dataset):
    with tap.plan(15, 'Пустые shelves/products'):
        order = await dataset.order(
            type='check',
            status='processing',
            estatus='begin')
        tap.ok(order, 'ордер создан')
        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'precheck_shelves_products', 'estatus')
        tap.eq(order.target, 'complete', 'target')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'failed', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        tap.eq(len(order.problems), 2, 'две проблемы')
        tap.eq(order.problems[0].type, 'empty_products', 'проблема 1')
        tap.eq(order.problems[1].type, 'empty_shelves', 'проблема 2')

async def test_problem_wrong_product(tap, dataset, uuid):
    with tap.plan(15, 'Продукт не найден'):
        order = await dataset.order(
            type='check',
            status='processing',
            estatus='begin',
            products=[uuid()])
        tap.ok(order, 'ордер создан')
        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'precheck_shelves_products', 'estatus')
        tap.eq(order.target, 'complete', 'target')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'failed', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        tap.eq(len(order.problems), 1, 'количество проблем')
        tap.eq(order.problems[0].type, 'product_not_found', 'проблема 1')
        tap.eq(order.problems[0].product_id, order.products[0], 'товар')

async def test_problem_wrong_shelf(tap, dataset, uuid):
    with tap.plan(14, 'Полка не найдена'):
        order = await dataset.order(
            type='check',
            status='processing',
            estatus='begin',
            shelves=[uuid()])
        tap.ok(order, 'ордер создан')
        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'precheck_shelves_products', 'estatus')
        tap.eq(order.target, 'complete', 'target')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.estatus, 'begin', 'estatus')

        tap.eq(len(order.problems), 1, 'количество проблем')
        tap.eq(order.problems[0].type, 'shelf_not_found', 'проблема 1')
        tap.eq(order.problems[0].shelf_id, order.shelves[0], 'полка')

async def test_problem_wrong_shelf_exists(tap, dataset):
    with tap.plan(17, 'Полка не принадлежит складу'):
        shelf = await dataset.shelf()
        tap.ok(shelf, 'полка создана')

        order = await dataset.order(
            type='check',
            status='processing',
            estatus='begin',
            shelves=[shelf.shelf_id])
        tap.ok(order, 'ордер создан')
        tap.ne(shelf.store_id, order.store_id, 'в разных складах')
        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'precheck_shelves_products', 'estatus')
        tap.eq(order.target, 'complete', 'target')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'failed', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        tap.eq(len(order.problems), 1, 'количество проблем')
        tap.eq(order.problems[0].type, 'shelf_not_found', 'проблема 1')
        tap.eq(order.problems[0].shelf_id, order.shelves[0], 'полка')


async def test_problem_check_kitchen(tap, dataset, wait_order_status):
    with tap.plan(3, 'проверяем что не можем пересчитать кухню'):
        product = await dataset.product()
        product.components = ProductComponents(
            [[ProductVariant(product_id=product.product_id, count=1)]]
        )
        await product.save()
        store = await dataset.full_store()

        user = await dataset.user(store=store)
        shelf = await dataset.shelf(store=store)
        order = await dataset.order(
            type='check',
            acks=[user.user_id],
            products=[product.product_id],
            shelves=[shelf.shelf_id],
            required=[{
                'product_id': product.product_id,
                'shelf_id': shelf.shelf_id,
            }],
            store_id=user.store_id,
        )

        await wait_order_status(
            order, ('failed', 'begin'), user_done=user.user_id
        )
        tap.eq(len(order.problems), 1, 'одна проблема')
        tap.eq(
            order.problems[0].type,
            'no_check_kitchen_product',
            'нужный тип',
        )


async def test_no_problem(tap, dataset):
    with tap.plan(15, 'Корректный товар'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            type='check',
            status='processing',
            estatus='begin',
            products=[product.product_id])
        tap.ok(order, 'ордер создан')
        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'precheck_shelves_products', 'estatus')
        tap.eq(order.target, 'complete', 'target')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'suggests_generate', 'estatus')
        tap.eq(order.target, 'complete', 'target')

        tap.eq(len(order.problems), 0, 'количество проблем')


@pytest.mark.parametrize(
    'shelf_type', ['store', 'kitchen_components'],
)
async def test_no_problem_shelf(tap, dataset, shelf_type):
    with tap.plan(15, 'Корректная полка'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type=shelf_type)
        tap.ok(shelf, 'полка создана')

        order = await dataset.order(
            store_id=store.store_id,
            type='check',
            status='processing',
            estatus='begin',
            shelves=[shelf.shelf_id])
        tap.ok(order, 'ордер создан')
        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'precheck_shelves_products', 'estatus')
        tap.eq(order.target, 'complete', 'target')

        tap.ok(await order.business.order_changed(), 'стейт машина отработала')
        tap.ok(await order.reload(), 'перегружен')

        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'suggests_generate', 'estatus')
        tap.eq(order.target, 'complete', 'target')

        tap.eq(len(order.problems), 0, 'количество проблем')
