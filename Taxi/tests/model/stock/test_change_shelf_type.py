from datetime import timedelta
import pytest


@pytest.mark.parametrize('shelf_type', ['parcel', 'store'])
async def test_change_shelf_type(tap, dataset, shelf_type, now):
    with tap.plan(7, 'Смена типа полки стока'):
        stock = await dataset.stock(
            shelf_type='lost',
            updated=now() - timedelta(seconds=2)
        )
        tap.ok(stock, 'Создался сток')
        tap.eq(stock.shelf_type, 'lost', 'Тип полки lost')
        logs = await stock.list_log()
        log_ids = {log.log_id for log in logs}
        old_updated = stock.updated
        old_lsn = stock.lsn

        new_stock = await stock.change_shelf_type(shelf_type)

        await stock.reload()

        tap.eq(stock, new_stock, 'Тот же сток вернулся')
        tap.eq(stock.shelf_type, shelf_type, 'Тип полки изменен')
        logs = await stock.list_log()
        tap.eq(
            {log.log_id for log in logs},
            log_ids,
            'Не появилось новых логов'
        )
        tap.ok(stock.updated > old_updated, 'updated подвинул')
        tap.ok(stock.lsn > old_lsn, 'lsn подвинул')


async def test_change_shelf_type_failed(tap, dataset, now):
    with tap.plan(5, 'Смена типа полки на невалидное значение'):
        stock = await dataset.stock(
            shelf_type='lost',
            updated=now() - timedelta(seconds=2)
        )
        old_updated = stock.updated
        old_lsn = stock.lsn
        tap.ok(stock, 'Создался сток')

        with tap.raises(AssertionError, 'Не меняется на неправильный тип'):
            await stock.change_shelf_type('x')
        await stock.reload()
        tap.eq(stock.shelf_type, 'lost', 'Тип полки остался старым')
        tap.eq(stock.updated, old_updated, 'updated не изменился')
        tap.eq(stock.lsn, old_lsn, 'lsn не изменился')
