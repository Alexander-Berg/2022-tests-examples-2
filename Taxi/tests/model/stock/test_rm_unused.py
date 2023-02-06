from stall.model.stock import Stock
from stall.model.stock_log import StockLog


async def test_unused(tap, dataset):
    with tap.plan(4, 'удаляем протухшие нулевые остатки'):
        store = await dataset.store()
        product = await dataset.product()

        stocks = [
            await dataset.stock(store=store, product=product, count=0)
            for _ in range(3)
        ]

        tap.ok(stocks, 'создали остатки')
        tap.eq(stocks[0].count, 0, 'нулевые')

        logs = await StockLog.list(
            by='look',
            conditions=('stock_id', [s.stock_id for s in stocks])
        )
        tap.ok(logs.list, 'у протухших остатков есть логи')

        # минус 30 дней, в бд нельзя задать поле updated руками
        await Stock.rm_unused(ttl=-30, store_id=store.store_id)

        unused_stocks = await Stock.list_by_product(
            product_id=product.product_id, store_id=store.store_id,
        )

        tap.eq(len(unused_stocks), 0, 'удалили все протухшие остатки')


async def test_count(tap, dataset):
    with tap.plan(5, 'оставляем протухшие не нулевые остатки'):
        store = await dataset.store()
        product = await dataset.product()

        stocks = [
            await dataset.stock(store=store, product=product, count=1)
            for _ in range(3)
        ]

        tap.ok(stocks, 'создали остатки')
        tap.eq(stocks[0].count, 1, 'не нулевые')

        logs = await StockLog.list(
            by='look',
            conditions=('stock_id', [s.stock_id for s in stocks])
        )
        tap.ok(logs.list, 'у протухших остатков есть логи')

        # минус 30 дней, в бд нельзя задать поле updated руками
        await Stock.rm_unused(ttl=-30, store_id=store.store_id)

        ok_stocks = await Stock.list_by_product(
            product_id=product.product_id, store_id=store.store_id,
        )

        tap.eq(len(ok_stocks), 3, 'ничего не удалили')
        logs_after_clean = await StockLog.list(
            by='look',
            conditions=('stock_id', [s.stock_id for s in stocks])
        )
        tap.eq(len(logs_after_clean.list), len(logs.list),
               'логи протухших остатков не удалены')


async def test_updated(tap, dataset):
    with tap.plan(5, 'оставляем свежие нулевые остатки'):
        store = await dataset.store()
        product = await dataset.product()

        stocks = [
            await dataset.stock(store=store, product=product, count=0)
            for _ in range(3)
        ]

        tap.ok(stocks, 'создали остатки')
        tap.eq(stocks[0].count, 0, 'нулевые')

        logs = await StockLog.list(
            by='look',
            conditions=('stock_id', [s.stock_id for s in stocks])
        )
        tap.ok(logs.list, 'у остатков есть логи')

        await Stock.rm_unused(ttl=30, store_id=store.store_id)

        ok_stocks = await Stock.list_by_product(
            product_id=product.product_id, store_id=store.store_id,
        )
        tap.eq(len(ok_stocks), 3, 'ничего не удалили')

        logs_after_clean = await StockLog.list(
            by='look',
            conditions=('stock_id', [s.stock_id for s in stocks])
        )
        tap.eq(len(logs_after_clean.list), len(logs.list),
               'логи остатков не удалены')
