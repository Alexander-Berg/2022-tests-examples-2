async def test_cancel(tap, dataset):
    with tap.plan(18, 'отмена саджестов'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'Заказ создан')
        tap.eq(order.fstatus, ('processing', 'waiting'), 'статус')

        shelf = await dataset.shelf(store_id=order.store_id)
        tap.eq(shelf.store_id, order.store_id, 'полка создана')

        suggest = dataset.Suggest({
            'type': 'box2shelf',
            'order_id': order.order_id,
            'store_id': order.store_id,
            'shelf_id': shelf.shelf_id,
            'status': 'done',
            'count': 27,
            'result_count': 123,
            'valid': '2020-10-11',
            'result_valid': '2020-11-11',
        })
        tap.ok(await suggest.save(), 'саджест сохранён')

        with suggest as s:
            tap.eq(s.status, 'done', 'status')
            tap.ok(s.valid, 'valid')
            tap.ok(s.result_valid, 'result_valid')
            tap.ok(s.count, 'count')
            tap.ok(s.result_count, 'result_count')

        with tap.raises(suggest.ErSuggestIsNotCancelable,
                        'саджест не разрешено отменять'):
            await suggest.done(status='cancel')

        suggest.conditions = {'cancelable': True}
        tap.ok(await suggest.save(), 'пересохранён')

        tap.ok(await suggest.done(status='cancel'), 'отменён')


        with suggest as s:
            tap.eq(s.status, 'request', 'status')
            tap.ok(s.valid, 'valid')
            tap.ok(not s.result_valid, 'result_valid сбросился')
            tap.ok(s.count, 'count')
            tap.ok(not s.result_count, 'result_count сбросился')

        with tap.raises(suggest.ErSuggestIsNotDone,
                        'саджест не завершён, чтоб его отменять'):
            await suggest.done(status='cancel')
