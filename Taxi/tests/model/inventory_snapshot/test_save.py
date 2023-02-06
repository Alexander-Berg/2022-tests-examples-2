async def test_save(tap, dataset):
    with tap.plan(14, 'манипуляции с записями снапшотов'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order()
        tap.ok(order, 'ордер создан')

        item = dataset.InventoryRecord({
            'order_id': order.order_id,
            'shelf_type': 'store',
            'product_id': product.product_id,
        })
        tap.ok(item, 'инстанцирован')

        tap.ok(await item.save(), 'сохранено')
        record_id = item.record_id
        tap.ok(record_id, 'идентификатор назначен')
        tap.eq(item.count, None, 'count пуст')
        tap.eq(item.result_count, None, 'result_count пуст')

        item = dataset.InventoryRecord({
            'order_id': order.order_id,
            'product_id': product.product_id,
            'shelf_type': 'store',
            'count': 27,
        })
        tap.ok(await item.save(), 'сохранено снова')
        tap.eq(item.count, 27, 'количество обновилось')
        tap.eq(item.record_id, record_id, 'record_id тот же')


        item = dataset.InventoryRecord({
            'order_id': order.order_id,
            'product_id': product.product_id,
            'shelf_type': 'store',
            'result_count': 35,
        })
        tap.ok(await item.save(), 'сохранено снова')
        tap.eq(item.count, 27, 'количество обновилось')
        tap.eq(item.result_count, 35, 'результат обновился')
        tap.eq(item.record_id, record_id, 'record_id тот же')
