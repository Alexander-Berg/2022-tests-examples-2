from argparse import Namespace
import logging

import pytest

from stall.scripts.fix_store_stocks import main, log


def create_args(**kwargs) -> Namespace:
    """Сформировать аргументы для тулы с дефолтами"""
    for argument, default in (
            ('apply', False),
            ('store', None),
            ('product_id', None),
            ('verbose', False)
    ):
        kwargs.setdefault(argument, default)

    return Namespace(**kwargs)


@pytest.mark.non_parallel
async def test_all_fine(tap, dataset, caplog):
    with tap:
        log.setLevel(level=logging.INFO)
        caplog.set_level(level=logging.INFO)
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        for i in range(5):
            stock = await dataset.stock(
                store=store,
                shelf_type='kitchen_components'
            )
            tap.eq(
                stock.store_id,
                store.store_id,
                f'Сток {i} в нужном сторе'
            )
        for i in range(10):
            tap.ok(
                await dataset.StoreStock.daemon_cycle(),
                f'Цикл демона {i}'
            )
            cursor = await dataset.StoreStock.list(
                by='full',
                conditions=('store_id', store.store_id)
            )
            if cursor and len(cursor.list) == 5:
                break

        args = create_args(store=store.external_id)

        await main(args)

        result_record = next(
            (
                rec for rec in caplog.records
                if rec.msg == 'Закончили проверку сторстоков'
            ),
            None
        )
        tap.ok(result_record, 'Нашли последнюю запись')
        tap.eq(result_record.ctx['total'], 5, 'Нужное кол-во сторстоков')
        tap.eq(result_record.ctx['count_diff'], 0, 'Нет разницы в количестве')
        tap.eq(result_record.ctx['reserve_diff'], 0, 'Нет разницы в резерве')

        error_record = next(
            (rec for rec in caplog.records if rec.levelno == logging.ERROR),
            None
        )
        tap.eq(error_record, None, 'Не было ошибок')


@pytest.mark.non_parallel
async def test_verbose(tap, dataset, caplog):
    with tap:
        log.setLevel(level=logging.INFO)
        caplog.set_level(level=logging.INFO)
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        stocks = [
            await dataset.stock(store=store, shelf_type='kitchen_components')
            for _ in range(2)
        ]
        store_stocks = []
        for i in range(10):
            tap.ok(
                await dataset.StoreStock.daemon_cycle(),
                f'Цикл демона {i}'
            )
            cursor = await dataset.StoreStock.list(
                by='full',
                conditions=('store_id', store.store_id)
            )
            if cursor and len(cursor.list) == len(stocks):
                store_stocks = cursor.list
                break

        args = create_args(store=store.external_id, verbose=True)

        await main(args)

        record_store_stock_ids = {
            rec.ctx['store_stock_id']
            for rec in caplog.records
            if 'store_stock_id' in rec.ctx
        }
        tap.eq(
            record_store_stock_ids,
            {stock.store_stock_id for stock in store_stocks},
            'Информация о тех же сторстоках'
        )


# pylint: disable=too-many-locals
@pytest.mark.non_parallel
async def test_diff_found(tap, dataset, caplog):
    with tap:
        log.setLevel(level=logging.ERROR)
        caplog.set_level(level=logging.ERROR)
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        stock = await dataset.stock(
            store=store,
            shelf_type='kitchen_components'
        )
        stock = await stock.do_reserve(await dataset.order(), stock.count)
        tap.ok(stock, 'Резерв успешный')
        store_stock = None
        for i in range(10):
            tap.ok(
                await dataset.StoreStock.daemon_cycle(),
                f'Цикл демона {i}'
            )
            cursor = await dataset.StoreStock.list(
                by='full',
                conditions=('store_id', store.store_id)
            )
            if cursor and cursor.list:
                store_stock = cursor.list[0]
                break

        stock_logs = await stock.list_log()
        stock_log = stock_logs.list[-2]
        sl_shard, sl_lsn = stock_log.shardno, stock_log.lsn
        cursor = store_stock.cursor
        cursor[str(sl_shard)] = sl_lsn

        store_stock = await store_stock.load(
            {
                'store_stock_id': store_stock.store_stock_id,
                'delta_count': 0,
                'delta_reserve': 0,
                'cursor': cursor,
                'lsn': store_stock.lsn,
            },
            by='update_by_log',
            db={'shard': sl_shard},
            mode='update',
        )

        tap.ok(store_stock, 'Обновили сторсток')
        old_reserve = store_stock.reserve
        old_count = store_stock.count

        args = create_args(store=store.external_id)

        await main(args)

        error_record = next(
            (rec for rec in caplog.records if rec.levelno == logging.ERROR),
            None
        )
        tap.eq(error_record.ctx['total'], 1, 'Один сторсток')
        tap.eq(error_record.ctx['count_diff'], 0, 'Нет расхождения кол-ва')
        tap.eq(error_record.ctx['reserve_diff'], 1, 'Есть расхождение резерва')

        tap.ok(await store_stock.reload(), 'Перезабрал сторсток')
        tap.eq(store_stock.count, old_count, 'Не изменилось кол-во')
        tap.eq(store_stock.reserve, old_reserve, 'Не изменился резерв')


# pylint: disable=too-many-locals
@pytest.mark.non_parallel
async def test_diff_found_apply(tap, dataset, caplog):
    with tap:
        log.setLevel(level=logging.ERROR)
        caplog.set_level(level=logging.ERROR)
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        stock = await dataset.stock(
            store=store,
            shelf_type='kitchen_components',
            count=33
        )
        order = await dataset.order()
        stock = await stock.do_reserve(order, stock.count)
        tap.ok(stock, 'Резерв успешный')
        stock = await stock.do_get(order, stock.count)
        store_stock = None
        for i in range(10):
            tap.ok(
                await dataset.StoreStock.daemon_cycle(),
                f'Цикл демона {i}'
            )
            cursor = await dataset.StoreStock.list(
                by='full',
                conditions=('store_id', store.store_id)
            )
            if cursor and cursor.list:
                store_stock = cursor.list[0]
                break

        stock_logs = await stock.list_log()
        stock_log = stock_logs.list[-2]
        sl_shard, sl_lsn = stock_log.shardno, stock_log.lsn
        cursor = store_stock.cursor
        cursor[str(sl_shard)] = sl_lsn

        store_stock = await store_stock.load(
            {
                'store_stock_id': store_stock.store_stock_id,
                'delta_count': 0,
                'delta_reserve': 0,
                'cursor': cursor,
                'lsn': store_stock.lsn,
            },
            by='update_by_log',
            db={'shard': sl_shard},
            mode='update',
        )

        tap.ok(store_stock, 'Обновили сторсток')
        old_reserve = store_stock.reserve
        old_count = store_stock.count

        args = create_args(store=store.external_id, apply=True)

        await main(args)

        error_record = next(
            (rec for rec in caplog.records if rec.levelno == logging.ERROR),
            None
        )
        tap.eq(error_record.ctx['total'], 1, 'Один сторсток')
        tap.eq(error_record.ctx['count_diff'], 1, 'Расхождение кол-ва')
        tap.eq(error_record.ctx['reserve_diff'], 1, 'Расхождение резерва')

        tap.ok(await store_stock.reload(), 'Перезабрал сторсток')
        tap.eq(store_stock.reserve, old_reserve+33, 'Изменился резерв')
        tap.eq(store_stock.count, old_count+33, 'Изменилось кол-во')


async def test_store_not_found(tap, caplog, uuid):
    with tap.plan(2, 'Не найден склад'):
        log.setLevel(level=logging.WARNING)
        caplog.set_level(level=logging.WARNING)
        fake_external_id = uuid()
        args = create_args(store=fake_external_id)

        await main(args)

        record = next(
            (rec for rec in caplog.records if rec.msg == 'Не найден склад'),
            None
        )
        tap.ok(record, 'Запись о ненайденном складе')
        tap.eq(
            record.ctx['external_id'],
            fake_external_id,
            'В записи правильный meta_order_id'
        )


async def test_product_not_found(tap, caplog, uuid):
    with tap.plan(2, 'Не найден продукт'):
        log.setLevel(level=logging.WARNING)
        caplog.set_level(level=logging.WARNING)
        fake_product_id = uuid()
        args = create_args(product_id=fake_product_id)

        await main(args)

        record = next(
            (rec for rec in caplog.records if rec.msg == 'Не найден продукт'),
            None
        )
        tap.ok(record, 'Запись о ненайденном продукте')
        tap.eq(
            record.ctx['product_id'],
            fake_product_id,
            'В записи правильный product_id'
        )
