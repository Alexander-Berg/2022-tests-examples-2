from stall.model.stock import Stock


# pylint: disable=too-many-locals
async def test_put_get(tap, dataset):
    '''Положить на полку'''
    with tap.plan(28, 'тест put get'):
        product = await dataset.product()
        tap.ok(product, 'продукт сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(
            store_id=store.store_id,
            type='trash'
        )
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        order = await dataset.order(store_id=store.store_id)
        tap.ok(order, 'заказ создан')

        stock = await Stock.do_put(order, shelf, product, 3, vars={
            "reasons": [
                {
                    order.order_id:
                        {
                            'reason_code': 'TRASH_TTL',
                            'count': 3
                        }
                }
            ]

        })
        tap.ok(stock, 'Сохранен')
        tap.eq(stock.count, 3, f'count={stock.count}')
        tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
        tap.eq(stock.product_id, product.product_id, 'product_id')
        tap.eq(stock.company_id, store.company_id, 'company_id')
        tap.eq(stock.store_id, store.store_id, 'store_id')
        tap.eq(stock.shelf_id, shelf.shelf_id, 'shelf_id')
        tap.ok(stock.stock_id, 'id появился')
        tap.eq(stock.shelf_type, shelf.type, 'тип полки попал в сток')
        tap.eq(len(stock.vars['reasons']), 1, 'причина запиана')
        tap.ok('writeoff' not in stock.vars, 'writeoff нет')

        logs = (await stock.list_log()).list
        tap.eq(len(logs), 1, 'Только основная запись')
        with logs[-1] as log:
            tap.eq(log.type, 'put', f'log type={log.type}')
            tap.eq(log.count, 3, f'log count={log.count}')
            tap.eq(log.reserve, 0, f'log reserve={log.reserve}')
            tap.eq(log.delta_count, 3, f'log delta_count={log.delta_count}')
            tap.eq(log.delta_reserve, 0,
                   f'log delta_reserve={log.delta_reserve}')
            tap.eq(log.recount, None, 'основная запись')
            tap.eq(log.quants, 1, 'дефолтный квант')

        order = await dataset.order(
            tap='write_off',
            store_id=store.store_id
        )
        tap.ok(order, 'заказ создан')

        with await stock.do_reserve(order, 2) as stock:
            tap.eq(stock.reserve, 2, f'reserve={stock.reserve}')

        await stock.do_write_off(
            order,
            count=2,
            vars=stock.vars,
        )

        await stock.reload()

        writeoff_count = 0
        for element in stock.vars['write_off']:
            for _, writeoff in element.items():
                writeoff_count += \
                    sum([_dict['count'] for _dict in writeoff])
        tap.eq(writeoff_count, 2, 'сумма как в саджесте')
        reasons_remains = 0
        for element in stock.vars['reasons']:
            for reason in element.values():
                reasons_remains += reason['count']

        tap.eq(reasons_remains, 1, 'сумма как в остатке')
