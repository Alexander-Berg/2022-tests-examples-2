# pylint: disable=too-many-statements


async def test_many_reserve(tap, dataset):
    with tap.plan(144):
        store  = await dataset.store()

        order  = await dataset.order(store=store)
        stock  = await dataset.stock(store=store, order=order, count=9)

        logs = (await stock.list_log()).list
        tap.eq(len(logs), 1, 'Записи лога')

        order1 = await dataset.order(store=store)
        order2 = await dataset.order(store=store)
        order3 = await dataset.order(store=store)

        with await stock.do_reserve(order1, 1) as stock:
            tap.eq(stock.count, 9, f'count={stock.count}')
            tap.eq(stock.reserve, 1, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves[order1.order_id],
                1,
                f'reserves={stock.reserves[order1.order_id]}'
            )

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 2, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 1, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {order1.order_id: 1},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 1,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

        with await stock.do_reserve(order2, 1) as stock:
            tap.eq(stock.count, 9, f'count={stock.count}')
            tap.eq(stock.reserve, 2, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves[order2.order_id],
                1,
                f'reserves={stock.reserves[order2.order_id]}'
            )

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 3, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 2, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {order2.order_id: 1},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 1,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

        with await stock.do_reserve(order3, 1) as stock:
            tap.eq(stock.count, 9, f'count={stock.count}')
            tap.eq(stock.reserve, 3, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves[order3.order_id],
                1,
                f'reserves={stock.reserves[order3.order_id]}'
            )

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 4, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 3, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {order3.order_id: 1},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 1,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

        with await stock.do_reserve(order1, 2) as stock:
            tap.eq(stock.count, 9, f'count={stock.count}')
            tap.eq(stock.reserve, 4, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves[order1.order_id],
                2,
                f'reserves={stock.reserves[order1.order_id]}'
            )

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 6, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 4, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {order1.order_id: 2},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 2,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

            with logs[-2] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 2, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, -1,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, logs[1].log_id, 'корректирующая запись')

        with await stock.do_reserve(order2, 2) as stock:
            tap.eq(stock.count, 9, f'count={stock.count}')
            tap.eq(stock.reserve, 5, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves[order2.order_id],
                2,
                f'reserves={stock.reserves[order2.order_id]}'
            )

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 8, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 5, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {order2.order_id: 2},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 2,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

            with logs[-2] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 3, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, -1,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, logs[2].log_id, 'корректирующая запись')

        with await stock.do_reserve(order3, 2) as stock:
            tap.eq(stock.count, 9, f'count={stock.count}')
            tap.eq(stock.reserve, 6, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves[order3.order_id],
                2,
                f'reserves={stock.reserves[order3.order_id]}'
            )

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 10, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 6, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {order3.order_id: 2},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 2,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

            with logs[-2] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 4, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, -1,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, logs[3].log_id, 'корректирующая запись')

        with await stock.do_reserve(order1, 1) as stock:
            tap.eq(stock.count, 9, f'count={stock.count}')
            tap.eq(stock.reserve, 5, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves[order1.order_id],
                1,
                f'reserves={stock.reserves[order1.order_id]}'
            )

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 12, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 5, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {order1.order_id: 1},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 1,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

            with logs[-2] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 4, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, -2,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, logs[5].log_id, 'корректирующая запись')

        with await stock.do_reserve(order2, 1) as stock:
            tap.eq(stock.count, 9, f'count={stock.count}')
            tap.eq(stock.reserve, 4, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves[order2.order_id],
                1,
                f'reserves={stock.reserves[order2.order_id]}'
            )

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 14, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 4, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {order2.order_id: 1},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 1,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

            with logs[-2] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 3, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, -2,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, logs[7].log_id, 'корректирующая запись')

        with await stock.do_reserve(order3, 1) as stock:
            tap.eq(stock.count, 9, f'count={stock.count}')
            tap.eq(stock.reserve, 3, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves[order3.order_id],
                1,
                f'reserves={stock.reserves[order3.order_id]}'
            )

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 16, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 3, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {order3.order_id: 1},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 1,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

            with logs[-2] as log:
                tap.eq(log.type, 'reserve', f'log type={log.type}')
                tap.eq(log.count, 9, f'log count={log.count}')
                tap.eq(log.reserve, 2, f'log reserve={log.reserve}')
                tap.eq(
                    log.reserves,
                    {},
                    'резервы'
                )
                tap.eq(log.delta_count, 0, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, -2,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, logs[9].log_id, 'корректирующая запись')

        tap.eq(len(stock.reserves), 3, f'{len(stock.reserves)} записей')
        tap.eq(sum(stock.reserves.values()), 3, 'всего резервов')
