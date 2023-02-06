import pytest

@pytest.mark.parametrize('acks',[True, False])
async def test_order(tap, dataset, acks):
    with tap.plan(9, 'Создаём законченный ордер'):
        store = await dataset.store( options=
                                     {'exp_jack_sparrow': True,
                                      'exp_susanin': True}
                                     )
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='admin', store_id=store.store_id)
        tap.eq(user.store_id, store.store_id, 'Админ создан')

        shelf = await dataset.shelf(
            store_id=user.store_id,
            title='Созданная полка 110-230')
        tap.eq(user.store_id, shelf.store_id, 'Полка создана')

        product = await dataset.product(title='Созданный продукт 110-230')
        tap.ok(product, 'Продукт создана')

        product_2 = await dataset.product(title='Созданный продукт 110-230-2')
        tap.ok(product_2, 'Продукт 2 создана')

        stock = await dataset.stock(
            store_id=user.store_id,
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            count=1234)
        tap.eq(stock.store_id, user.store_id, 'остаток создан')

        stock_2 = await dataset.stock(
            store_id=user.store_id,
            shelf_id=shelf.shelf_id,
            product_id=product_2.product_id,
            count=10)
        tap.eq(stock_2.store_id, user.store_id, 'остаток 2 создан')
        if acks:
            acks = [user.user_id]
        else:
            acks=[]
        order = await dataset.order_done(
            type='order',
            store_id=user.store_id,
            acks=acks,
            approved=True,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 2,
                },
                {
                    'product_id': product_2.product_id,
                    'count': 5,
                }
            ],
            vars={
                'dataTest': '110-230-order'
            }

        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('complete', 'done'), 'статус')

