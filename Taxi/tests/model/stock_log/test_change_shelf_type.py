import pytest


@pytest.mark.parametrize('shelf_type', ['parcel', 'store', None])
async def test_change_shelf_type(tap, dataset, shelf_type):
    with tap.plan(6, 'Смена типа полки стоклога'):
        stock = await dataset.stock(shelf_type='lost')
        tap.ok(stock, 'Сток создан')
        cursor = await stock.list_log()
        stocklog = cursor.list[0]
        tap.ok(stocklog, 'Создан стоклог')
        tap.eq(stocklog.shelf_type, 'lost', 'Тип полки lost')
        old_lsn = stocklog.lsn

        new_stocklog = await stocklog.change_shelf_type(shelf_type)

        await new_stocklog.reload()

        tap.eq(stocklog, new_stocklog, 'Тот же стоклог вернулся')
        tap.eq(stocklog.shelf_type, shelf_type, 'Тип полки изменен')
        tap.ok(stocklog.lsn > old_lsn, 'lsn подвинул')


async def test_change_shelf_type_failed(tap, dataset):
    with tap.plan(5, 'Смена типа полки только на валидные'):
        stock = await dataset.stock(shelf_type='lost')
        tap.ok(stock, 'Сток создан')
        cursor = await stock.list_log()
        stocklog = cursor.list[0]
        old_lsn = stocklog.lsn

        tap.ok(stocklog, 'Создался стоклог')

        with tap.raises(AssertionError, 'Не меняется на неправильный тип'):
            await stocklog.change_shelf_type('x')
        await stocklog.reload()
        tap.eq(stocklog.shelf_type, 'lost', 'Тип полки не изменился')
        tap.eq(old_lsn, stocklog.lsn, 'lsn не изменился')
