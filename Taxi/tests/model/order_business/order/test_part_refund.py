import pytest


@pytest.mark.parametrize('count', [8, 9])
async def test_different_stocks(tap, dataset, wait_order_status, count):
    with tap.plan(16, 'возврат в два стока'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        shelf1 = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf1, 'полка 1 создана')
        shelf2 = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf2, 'полка 2 создана')

        stock_product1 = await dataset.stock(
            product=product,
            store=store,
            count=5
        )
        tap.eq(stock_product1.store_id, store.store_id, 'остаток товар')
        tap.eq(stock_product1.product_id, product.product_id, 'product_id')
        tap.eq(stock_product1.left, 5, 'количество')

        stock_product2 = await dataset.stock(
            product=product,
            store=store,
            count=4
        )
        tap.eq(stock_product2.store_id, store.store_id, 'остаток экземпляр')
        tap.eq(stock_product2.product_id, product.product_id, 'product_id')
        tap.eq(stock_product2.left, 4, 'количество')

        order = await dataset.order(
            type='order',
            acks=[user.user_id],
            approved=True,
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 9,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)
        errors, rlist = await order.business.check_part_refund_required(
            [
                {
                    'product_id': product.product_id,
                    'count': count
                }
            ],
        )
        tap.eq(len(errors), 0, 'Ошибок нет')
        tap.eq(len(rlist), 2, 'Два возврата в стоки')

        count_result = sum([el['count'] for el in rlist])
        tap.eq(count_result, count, 'Количество возвращенных товаров совпадает')


@pytest.mark.parametrize('count', [5, 3])
async def test_one_stock_refund(tap, dataset, wait_order_status, count):
    with tap.plan(16, 'возврат в один сток'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        shelf1 = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf1, 'полка 1 создана')
        shelf2 = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf2, 'полка 2 создана')

        stock_product1 = await dataset.stock(
            product=product,
            store=store,
            count=5
        )
        tap.eq(stock_product1.store_id, store.store_id, 'остаток товар')
        tap.eq(stock_product1.product_id, product.product_id, 'product_id')
        tap.eq(stock_product1.left, 5, 'количество')

        stock_product2 = await dataset.stock(
            product=product,
            store=store,
            count=4
        )
        tap.eq(stock_product2.store_id, store.store_id, 'остаток экземпляр')
        tap.eq(stock_product2.product_id, product.product_id, 'product_id')
        tap.eq(stock_product2.left, 4, 'количество')

        order = await dataset.order(
            type='order',
            acks=[user.user_id],
            approved=True,
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 9,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)
        errors, rlist = await order.business.check_part_refund_required(
            [
                {
                    'product_id': product.product_id,
                    'count': count
                }
            ],
        )
        tap.eq(len(errors), 0, 'Ошибок нет')
        tap.eq(len(rlist), 1, 'Один возврат в сток')

        tap.eq(
            rlist[0]['count'],
            count,
            'Количество возвращенных товаров совпадает',
        )


async def test_refund_over_order(tap, dataset, wait_order_status):
    with tap.plan(15, 'Тест возврата большего числа товаров, чем в заказе '):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        shelf1 = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf1, 'полка 1 создана')
        shelf2 = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf2, 'полка 2 создана')

        stock_product1 = await dataset.stock(
            product=product,
            store=store,
            count=5
        )
        tap.eq(stock_product1.store_id, store.store_id, 'остаток товар')
        tap.eq(stock_product1.product_id, product.product_id, 'product_id')
        tap.eq(stock_product1.left, 5, 'количество')

        stock_product2 = await dataset.stock(
            product=product,
            store=store,
            count=4
        )
        tap.eq(stock_product2.store_id, store.store_id, 'остаток экземпляр')
        tap.eq(stock_product2.product_id, product.product_id, 'product_id')
        tap.eq(stock_product2.left, 4, 'количество')

        order = await dataset.order(
            type='order',
            acks=[user.user_id],
            approved=True,
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 7,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)
        result = await order.business.check_part_refund_required(
            [
                {
                    'product_id': product.product_id,
                    'count': 8
                }
            ],
        )
        errors = result[0]
        tap.eq(len(errors), 1, 'Найдена ошибка')
        tap.eq(
            errors[0]['message'],
            f'Wrong count for required#0: {product.product_id}',
            'Ошибка в 0 позиции',
        )
