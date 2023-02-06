# pylint: disable=too-many-statements
async def test_save(tap, dataset):
    '''Проверяем создание лога при заполнении полки'''
    with tap.plan(63):

        stock = await dataset.stock(count=103, reserve=0)
        tap.ok(stock, 'остаток создан')
        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')

        with await stock.list_log() as cursor:
            tap.ok(cursor, 'Список')
            tap.eq(len(cursor.list), 1, f'размер списка={len(cursor.list)}')
            tap.eq(cursor.list[-1].stock_id, stock.stock_id, 'Выбран нужный')
            tap.eq(cursor.list[-1].count, 103,
                   f'count={cursor.list[-1].count}')
            tap.eq(cursor.list[-1].reserve, 0,
                   f'reserve={cursor.list[-1].reserve}')
            tap.eq(cursor.list[-1].delta_count, 103,
                   f'delta_count={cursor.list[-1].delta_count}')
            tap.eq(cursor.list[-1].delta_reserve, 0,
                   f'delta_reserve={cursor.list[-1].delta_reserve}')
            tap.eq(cursor.list[-1].type, 'put', 'тип операции в логе')
            tap.ok(cursor.list[-1].shelf_type, stock.shelf_type, 'shelf_type')
            tap.ok(cursor.list[-1].lsn, 'lsn')

        with await stock.do_take(order, 7) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 96, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

        with await stock.list_log() as cursor:
            tap.ok(cursor, 'Список')
            tap.eq(len(cursor.list), 2, f'размер списка={len(cursor.list)}')
            tap.eq(cursor.list[-1].stock_id, stock.stock_id, 'Выбран нужный')
            tap.eq(cursor.list[-1].count, 96,
                   f'count={cursor.list[-1].count}')
            tap.eq(cursor.list[-1].reserve, 0,
                   f'reserve={cursor.list[-1].reserve}')
            tap.eq(cursor.list[-1].delta_count, -7,
                   f'delta_count={cursor.list[-1].delta_count}')
            tap.eq(cursor.list[-1].delta_reserve, 0,
                   f'delta_reserve={cursor.list[-1].delta_reserve}')
            tap.eq(cursor.list[-1].type, 'take', 'тип операции в логе')

        with await stock.do_reserve(order, 2) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 96, f'count={stock.count}')
            tap.eq(stock.reserve, 2, f'reserve={stock.reserve}')

        with await stock.list_log() as cursor:
            tap.ok(cursor, 'Список')
            tap.eq(len(cursor.list), 3, f'размер списка={len(cursor.list)}')
            tap.eq(cursor.list[-1].stock_id, stock.stock_id, 'Выбран нужный')
            tap.eq(cursor.list[-1].count, 96,
                   f'count={cursor.list[-1].count}')
            tap.eq(cursor.list[-1].reserve, 2,
                   f'reserve={cursor.list[-1].reserve}')
            tap.eq(cursor.list[-1].delta_count, 0,
                   f'delta_count={cursor.list[-1].delta_count}')
            tap.eq(cursor.list[-1].delta_reserve, 2,
                   f'delta_reserve={cursor.list[-1].delta_reserve}')
            tap.eq(cursor.list[-1].type, 'reserve', 'тип операции в логе')

        with await stock.do_reserve(order, 1) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 96, f'count={stock.count}')
            tap.eq(stock.reserve, 1, f'reserve={stock.reserve}')

        with await stock.list_log() as cursor:
            tap.ok(cursor, 'Список')
            tap.eq(len(cursor.list), 5, f'размер списка={len(cursor.list)}')

            tap.eq(cursor.list[-2].stock_id, stock.stock_id, 'Выбран нужный')
            tap.eq(cursor.list[-2].count, 96,
                   f'count={cursor.list[-1].count}')
            tap.eq(cursor.list[-2].reserve, 0,
                   f'reserve={cursor.list[-1].reserve}')
            tap.eq(cursor.list[-2].delta_count, 0,
                   f'delta_count={cursor.list[-1].delta_count}')
            tap.eq(cursor.list[-2].delta_reserve, -2,
                   f'delta_reserve={cursor.list[-1].delta_reserve}')
            tap.eq(cursor.list[-2].type, 'reserve', 'тип операции в логе')
            tap.eq(cursor.list[-2].stock_id, stock.stock_id, 'Выбран нужный')
            tap.eq(
                cursor.list[-2].recount,
                cursor.list[-3].log_id,
                'Перерасчет'
            )

            tap.eq(cursor.list[-1].stock_id, stock.stock_id, 'Выбран нужный')
            tap.eq(cursor.list[-1].count, 96,
                   f'count={cursor.list[-1].count}')
            tap.eq(cursor.list[-1].reserve, 1,
                   f'reserve={cursor.list[-1].reserve}')
            tap.eq(cursor.list[-1].delta_count, 0,
                   f'delta_count={cursor.list[-1].delta_count}')
            tap.eq(cursor.list[-1].delta_reserve, 1,
                   f'delta_reserve={cursor.list[-1].delta_reserve}')
            tap.eq(cursor.list[-1].type, 'reserve', 'тип операции в логе')

        with await stock.do_sale(order, 1) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 95, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

        with await stock.list_log() as cursor:
            tap.ok(cursor, 'Список')
            tap.eq(len(cursor.list), 6, f'размер списка={len(cursor.list)}')
            tap.eq(cursor.list[-1].stock_id, stock.stock_id, 'Выбран нужный')
            tap.eq(cursor.list[-1].count, 95,
                   f'count={cursor.list[-1].count}')
            tap.eq(cursor.list[-1].reserve, 0,
                   f'reserve={cursor.list[-1].reserve}')
            tap.eq(cursor.list[-1].delta_count, -1,
                   f'delta_count={cursor.list[-1].delta_count}')
            tap.eq(cursor.list[-1].delta_reserve, -1,
                   f'delta_reserve={cursor.list[-1].delta_reserve}')


async def test_product_quants(tap, dataset):
    with tap.plan(4, 'Кванты прорастают из стока'):
        stock = await dataset.stock()
        tap.eq(stock.quants, 1, 'дефолтный квант')

        logs = (await stock.list_log()).list
        with logs[-1] as log:
            tap.eq(log.quants, 1, 'дефолтный квант')

        stock = await dataset.stock(quants=33)
        tap.eq(stock.quants, 33, 'кванты используются')

        logs = (await stock.list_log()).list
        with logs[-1] as log:
            tap.eq(log.quants, 33, 'кванты проросли из стока')
