import random
import pytest


@pytest.mark.parametrize('attempts', [1, 2, 5])
async def test_flap(tap, dataset, uuid, attempts):
    with tap.plan(14 * attempts, 'Обнаружили флапы'):
        for attempt in range(1, attempts + 1):
            order = await dataset.order()
            tap.ok(order, f'ордер создан, попытка {attempt}')

            stock = await dataset.stock(order=order,
                                        count = random.randrange(200, 500),
                                        lot=uuid())
            count = stock.count
            tap.ok(stock, 'остаток создан')

            stock2 = await dataset.stock(order=order,
                                         count = random.randrange(200, 500),
                                         lot=uuid(),
                                         product_id=stock.product_id,
                                         shelf_id=stock.shelf_id)
            tap.ok(stock2, 'остаток создан')
            tap.ne(stock2.stock_id, stock.stock_id, 'разные остатки')
            tap.eq(stock2.product_id, stock.product_id, 'одинаковые продукты')
            tap.eq(stock2.shelf_id, stock.shelf_id, 'Полка одна и та же')
            tap.eq(stock2.company_id, stock.company_id, 'одина компания')
            tap.eq(stock2.store_id, stock.store_id, 'один склад')
            count2 = stock2.count

            tap.ok(await stock.do_take(order, 15),
                   'забрали 15 на первом стоке')
            tap.ok(await stock.reload(), 'перегрузили первый сток')

            tap.ok(await stock2.do_take(order, 17),
                   'забрали 17 на втором стоке')
            tap.ok(await stock.reload(), 'перегрузили второй сток')

            tap.eq(stock.count, count - 15, 'количество на первом')
            tap.eq(stock2.count, count2 - 17, 'количество на втором')
