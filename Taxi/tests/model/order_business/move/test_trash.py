from stall.model.suggest import Suggest


# pylint: disable=too-many-locals, too-many-statements
async def test_success(tap, dataset, uuid, wait_order_status, now):
    with tap.plan(18, 'Перемщение с треша и списание'):
        store = await dataset.store()
        product = await dataset.product()
        trash = await dataset.shelf(
            store=store,
            type='trash'
        )
        stock = await dataset.stock(
            store_id=store.store_id,
            shelf_id=trash.shelf_id,
            count=5,
            shelf_type='trash',
            product_id=product.product_id,
            lot=uuid(),
            vars={
                'reasons': [
                    {
                        uuid():
                            {
                                'count': 3, 'reason_code': 'TRASH_TTL'
                            }
                    },
                    {
                        uuid():
                            {
                                'count': 2, 'reason_code': 'TRASH_OPTIMIZE'
                            }
                    },
            ]
            }
        )
        shelf = await dataset.shelf(store_id=stock.store_id)

        user = await dataset.user()
        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            user_id=user.user_id,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 2,
                    'stock_id': stock.stock_id,
                    'reason_code': 'TRASH_TTL',
                    'src_shelf_id': trash.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                }
            ]
        )
        await wait_order_status(order, ('complete', 'done'))

        # Проверим что наш -2 реазон записался
        await stock.reload()
        diff = 0
        reasons = set()
        for element in stock.vars['reasons']:
            for reason in element.values():
                if reason['count'] < 0:
                    diff += reason['count']
                    reasons.add(reason['reason_code'])
        tap.eq(diff, -2, 'столько было по муву с треша')
        tap.eq(len(reasons), 1, 'только одна отрицательная причина')
        tap.eq(next(iter(reasons)), 'TRASH_TTL', 'причина верная')

        order = await dataset.order(
            store_id=stock.store_id,
            type='writeoff',
            status='reserving',
            estatus='begin',
            target='complete',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(
            order,
            ('processing', 'waiting')
        )

        suggests = await Suggest.list_by_order(order)
        suggests = dict((x.count, x) for x in suggests)

        with suggests[3] as suggest:
            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.product_id, stock.product_id, 'Продукт 1')
            tap.ok(
                await suggest.done('done', count=2),
                'Закрыли'
            )

        tap.ok(
            await order.done('complete', user=user),
            'Заказ выполнен'
        )

        await wait_order_status(
            order,
            ('complete', 'done'),
        )
        await order.business.order_changed()
        await stock.reload()
        logs = (await stock.list_log()).list
        with next(log for log in logs if log.type == 'write_off') as log:
            tap.eq(log.type, 'write_off', f'log type={log.type}')
            tap.ne(log.vars['reasons'], None, "Проставился reason")
            tap.ne(log.vars['write_off'], None, "Проставился write_off")
            tap.eq(log.count, 1, 'остаток')
            tap.eq(log.delta_count, -2, 'delta_count')

            writeoff_count = 0
            for element in log.vars['write_off']:
                for _, writeoff in element.items():
                    writeoff_count += \
                        sum([_dict['count'] for _dict in writeoff])
            tap.eq(writeoff_count, 2, 'сумма как в саджесте')
            reasons_remains = 0
            diff = 0
            for element in log.vars['reasons']:
                for reason in element.values():
                    if reason['count'] > 0:
                        reasons_remains += reason['count']
                    else:
                        diff += reason['count']
            tap.eq(reasons_remains, 1, 'сумма как в остатке')
            tap.eq(diff, -2, 'столько было по муву с треша')
