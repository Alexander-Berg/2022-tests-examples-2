import datetime as dt
from libstall.util import now
from scripts.cron.clean_stocks_log import clean_stocks_log
from stall.model.stock import Stock
from stall.model.stock_log import StockLog


async def test_rm_logs_of_removed_stocks(tap, dataset, cfg, monkeypatch):
    cfg.set('db_clean.max_age_days', 10)
    cfg.set('db_clean.stocks_log_limit', 3)

    age_old = dt.timedelta(days=11)

    def patched_now():
        return now() + age_old

    stock_to_delete = [
        await dataset.stock(count=0) for _ in range(10)
    ]
    stocks = [
        await dataset.stock(count=10) for _ in range(10)
    ]

    logs_to_delete = await StockLog.list(
        by='full',
        conditions=('stock_id', [s.stock_id for s in stock_to_delete]),
        sort=(),
    )
    logs_to_keep = await StockLog.list(
        by='full',
        conditions=('stock_id', [s.stock_id for s in stocks]),
        sort=(),
    )

    async for item in Stock.ilist(
            by='look',
            conditions=('stock_id', [s.stock_id for s in stock_to_delete]),
    ):
        await item.rm()

    with tap:
        tap.ok(logs_to_delete.list, 'there are logs to delete')
        tap.ok(logs_to_keep.list, 'there are logs to keep')

        monkeypatch.setattr('scripts.cron.clean_stocks_log.now',
                            patched_now)

        await clean_stocks_log()

        logs = await StockLog.list(
            by='full',
            conditions=('stock_id', [s.stock_id for s in stock_to_delete]),
            sort=(),
        )
        tap.eq_ok(len(logs.list), 0, 'logs to delete were deleted')

        logs = await StockLog.list(
            by='full',
            conditions=('stock_id', [s.stock_id for s in stocks]),
            sort=(),
        )
        tap.eq_ok(len(logs.list), len(logs_to_keep.list),
                  'logs to keep were not removed')


async def test_rm_old_logs(tap, dataset, cfg, monkeypatch):
    cfg.set('db_clean.max_age_days', 10)
    cfg.set('db_clean.stocks_log_limit', 3)

    age_old = dt.timedelta(days=11)

    def patched_now():
        return now() + age_old

    stocks = [
        await dataset.stock(count=0) for _ in range(10)
    ]
    logs_to_delete = await StockLog.list(
        by='full',
        conditions=('stock_id', [s.stock_id for s in stocks]),
        sort=(),
    )

    async for item in Stock.ilist(
            by='look',
            conditions=('stock_id', [s.stock_id for s in stocks]),
    ):
        await item.rm()

    with tap:
        tap.ok(logs_to_delete.list, 'there are logs to delete')

        await clean_stocks_log()

        logs = await StockLog.list(
            by='full',
            conditions=('stock_id', [s.stock_id for s in stocks]),
            sort=(),
        )
        tap.eq_ok(len(logs.list), len(logs_to_delete.list),
                  'logs were not removed (they are not old enough)')

        monkeypatch.setattr('scripts.cron.clean_stocks_log.now',
                            patched_now)

        await clean_stocks_log()

        logs = await StockLog.list(
            by='full',
            conditions=('stock_id', [s.stock_id for s in stocks]),
            sort=(),
        )
        tap.eq_ok(len(logs.list), 0, 'logs were deleted')
