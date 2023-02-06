from datetime import timedelta, date


async def test_valid(tap, dataset):
    '''Корректировка срока годности'''
    with tap.plan(9):
        stock = await dataset.stock(count=1, valid=date(2020, 1, 1))
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.valid, date(2020, 1, 1), 'Срок годности')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, stock.store_id, 'на складе')

        lsn = stock.lsn

        with await stock.do_valid(order, date(2021, 11, 23)) as stock:
            tap.eq(stock.valid, date(2021, 11, 23), f'valid={stock.valid}')
            tap.ok(stock.lsn > lsn, 'lsn увеличился')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'valid', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')


async def test_is_valid(tap, dataset):
    with tap.plan(1, 'На дату'):
        product = await dataset.product(valid=1, write_off_before=0)
        stock4 = await dataset.stock(product=product, valid='2020-05-26')
        with stock4 as stock:
            tap.eq(await stock.is_valid(product, date(2020, 5, 26)), False,
                   'на дату - не валиден')


async def test_is_valid_today(tap, now, dataset):
    with tap.plan(5, 'Поведение на текущий день'):
        product = await dataset.product(valid=1, write_off_before=None)

        stock0 = await dataset.stock(
            product=product,
            valid=now()+timedelta(days=2)
        )
        with stock0 as stock:
            tap.eq(await stock.is_valid(product), True,
                   'послезавтра - валиден')
        stock1 = await dataset.stock(
            product=product,
            valid=now() + timedelta(days=1)
        )
        with stock1 as stock:
            tap.eq(await stock.is_valid(product), False, 'завтра - не валиден')

        stock2 = await dataset.stock(product=product, valid=now())
        with stock2 as stock:
            tap.eq(await stock.is_valid(product), False,
                   'сегодня - не валиден')

        stock3 = await dataset.stock(
            product=product,
            valid=now()-timedelta(days=1)
        )
        with stock3 as stock:
            tap.eq(await stock.is_valid(product), False, 'вчера - не валиден')

        stock4 = await dataset.stock(
            product=product,
            valid=now()-timedelta(days=2)
        )
        with stock4 as stock:
            tap.eq(await stock.is_valid(product), False,
                   'позавчера - не валиден')


async def test_is_valid_none(tap, now, dataset):
    with tap.plan(1, 'Если у остатка нет даты'):
        product = await dataset.product(valid=1, write_off_before=0)
        stock = await dataset.stock(product=product, valid=None)
        tap.eq(
            await stock.is_valid(
                product,
                now()-timedelta(days=1),
            ),
            False,
            'Остаток без срока годности не валиден'
        )
