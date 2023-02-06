# pylint: disable=protected-access,unused-variable

from stall.model.order_business.base import (
    ErrorBusinessTooLow,
)


async def test_reserve_product(tap, uuid, dataset):
    with tap.plan(9, 'Алгоритм резервирования'):

        product = await dataset.product()
        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store, type='store', order=1)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=3,
            valid='2021-01-01',
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=4,
            valid='2021-01-02',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type='order',
        )

        stocks = await order.business._reserve_product(
            product_id=product.product_id,
            count=5,
        )

        tap.eq(len(stocks), 2, 'Два в резерве')

        with stocks[0] as stock:
            tap.eq(stock.stock_id, stock1.stock_id, 'От меньшего СГ')
            tap.eq(stock.count, 3, 'count')
            tap.eq(stock.reserve, 3, 'reserve')
            tap.eq(stock.reserves[order.order_id], 3, 'reserves')

        with stocks[1] as stock:
            tap.eq(stock.stock_id, stock2.stock_id, 'К большему СГ')
            tap.eq(stock.count, 4, 'count')
            tap.eq(stock.reserve, 2, 'reserve')
            tap.eq(stock.reserves[order.order_id], 2, 'reserves')


async def test_partial(tap, uuid, dataset):
    with tap.plan(10, 'Алгоритм частичного резервирования'):

        product = await dataset.product()
        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store, type='store', order=1)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=3,
            valid='2021-01-01',
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=4,
            reserve=3,  # Уже зарезервирована часть
            valid='2021-01-02',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type='order',
        )

        try:
            stocks = await order.business._reserve_product(
                product_id=product.product_id,
                count=5,
            )
        except ErrorBusinessTooLow as ex:
            tap.passed('Получили исключение ErrorBusinessTooLow')
            stocks = ex.stocks
        else:
            tap.failed('Получили исключение ErrorBusinessTooLow')

        tap.eq(len(stocks), 2, 'Два в резерве')

        with stocks[0] as stock:
            tap.eq(stock.stock_id, stock1.stock_id, 'От меньшего СГ')
            tap.eq(stock.count, 3, 'count')
            tap.eq(stock.reserve, 3, 'reserve')
            tap.eq(stock.reserves[order.order_id], 3, 'reserves')

        with stocks[1] as stock:
            tap.eq(stock.stock_id, stock2.stock_id, 'К большему СГ')
            tap.eq(stock.count, 4, 'count')
            tap.eq(stock.reserve, 4, 'reserve')
            tap.eq(stock.reserves[order.order_id], 1, 'reserves')


async def test_none(tap, dataset):
    with tap.plan(2, 'Нечего резервировать'):

        product = await dataset.product()
        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store, type='store', order=1)

        order = await dataset.order(
            store=store,
            type='order',
        )

        try:
            stocks = await order.business._reserve_product(
                product_id=product.product_id,
                count=5,
            )
        except ErrorBusinessTooLow as ex:
            tap.passed('Получили исключение ErrorBusinessTooLow')
            stocks = ex.stocks
        else:
            tap.failed('Получили исключение ErrorBusinessTooLow')

        tap.eq(len(stocks), 0, 'Нет резервов')


async def test_selected(tap, uuid, dataset):
    with tap.plan(14, 'Фильтр по выбранным остаткам'):

        product = await dataset.product()
        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store, type='store', order=1)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=3,
            valid='2021-01-01',
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=4,
            valid='2021-01-02',
            lot=uuid(),
        )

        stock3 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=5,
            valid='2021-01-03',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type='order',
        )

        try:
            stocks = await order.business._reserve_product(
                product_id=product.product_id,
                count=10,
                stock_id=[stock1.stock_id, stock2.stock_id],
            )
        except ErrorBusinessTooLow as ex:
            tap.passed('Получили исключение ErrorBusinessTooLow')
            stocks = ex.stocks
        else:
            tap.failed('Получили исключение ErrorBusinessTooLow')

        tap.eq(len(stocks), 2, 'Два в резерве')

        with stocks[0] as stock:
            tap.eq(stock.stock_id, stock1.stock_id, 'От меньшего СГ')
            tap.eq(stock.count, 3, 'count')
            tap.eq(stock.reserve, 3, 'reserve')
            tap.eq(stock.reserves[order.order_id], 3, 'reserves')

        with stocks[1] as stock:
            tap.eq(stock.stock_id, stock2.stock_id, 'К большему СГ')
            tap.eq(stock.count, 4, 'count')
            tap.eq(stock.reserve, 4, 'reserve')
            tap.eq(stock.reserves[order.order_id], 4, 'reserves')

        with await stock3.reload() as stock:
            tap.eq(stock.stock_id, stock3.stock_id, 'Не трогаем этот сток')
            tap.eq(stock.count, 5, 'count')
            tap.eq(stock.reserve, 0, 'reserve')
            tap.eq(stock.reserves, {}, 'reserves')
