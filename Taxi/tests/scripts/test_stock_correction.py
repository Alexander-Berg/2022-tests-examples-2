from scripts.dev.correct_stock import correct_manually


async def test_correct_manually(tap, dataset):
    with tap:
        user = await dataset.user()
        stock = await dataset.stock(count=300, reserve=100)
        tap.ok(stock, 'остаток создан')

        await correct_manually(stock.stock_id, 7, user.user_id)

        await stock.reload()
        tap.eq(stock.count, 300 + 7, f'count={stock.count}')
        tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')


async def test_correct_manually_negative(tap, dataset):
    with tap:
        user = await dataset.user()
        stock = await dataset.stock(count=300, reserve=100)
        tap.ok(stock, 'остаток создан')

        await correct_manually(stock.stock_id, -7, user.user_id)

        await stock.reload()
        tap.eq(stock.count, 300 - 7, f'count={stock.count}')
        tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')
