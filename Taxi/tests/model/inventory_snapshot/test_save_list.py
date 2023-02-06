import asyncio
import random


async def test_save_list(tap, dataset):
    with tap.plan(15, 'манипуляции с записями снапшотов'):
        products = [ await dataset.product() for i in range(5) ]
        tap.ok(products, 'продукты сгенерированы')

        order = await dataset.order()
        tap.ok(order, 'ордер создан')

        result = {}

        items = await dataset.InventoryRecord.save_list(
            order,
            [
                {
                    'product_id': p.product_id,
                    'shelf_type': 'store',
                    'count': random.randrange(25, 128),
                }
                for p in products
            ]
        )

        result = dict((p.record_id, (p.count, p.lsn, p.revision))
                      for p in items)

        tap.eq(len(items), len(products), 'записей')
        for i, item in enumerate(items):
            with tap.subtest(6, f'запись {i}') as taps:
                taps.isa_ok(item, dataset.InventoryRecord, f'запись {i}')
                taps.eq(item.order_id, order.order_id, 'order_id')

                load = await dataset.InventoryRecord.load(item.record_id)
                taps.ok(load, 'загружена')
                taps.ne(load.count, None, 'count заполнен')
                taps.eq(load.pure_python(), item.pure_python(), 'содержимое')
                taps.eq(load.result_count, None, 'result_count не заполнен')
        saved_updated = items[0].updated
        await asyncio.sleep(1)

        items = await dataset.InventoryRecord.save_list(
            order,
            [
                {
                    'product_id': p.product_id,
                    'shelf_type': 'store',
                    'result_count': random.randrange(25, 128),
                }
                for p in products
            ]
        )
        tap.ok(items[0].updated > saved_updated, 'Обновилось updated')

        tap.eq(len(items), len(products), 'записей')
        for i, item in enumerate(items):
            with tap.subtest(10, f'запись {i}') as taps:
                taps.isa_ok(item, dataset.InventoryRecord, f'запись {i}')
                taps.eq(item.order_id, order.order_id, 'order_id')

                load = await dataset.InventoryRecord.load(item.record_id)
                taps.ok(load, 'загружена')
                taps.eq(load.pure_python(), item.pure_python(), 'содержимое')
                taps.ne(load.count, None, 'count заполнен')
                taps.ne(load.result_count, None, 'result_count заполнен')

                taps.in_ok(load.record_id, result, 'id не поменялись')
                taps.eq(result[load.record_id][0], load.count, 'count предыд')
                taps.ok(result[load.record_id][1] < load.lsn, 'lsn ++')
                taps.ok(result[load.record_id][2] < load.revision,
                        'revision ++')
