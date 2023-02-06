async def test_cancel(tap, dataset, wait_order_status):
    with tap.plan(5, 'отменяем ордер'):
        acc = await dataset.order(
            type='acceptance',
            required=[
                {
                    'product_id': '111',
                    'count': 1,
                },
                {
                    'product_id': '222',
                    'count': 2,
                }
            ],
        )
        cc = await dataset.order(
            type='control_check',
            vars={'acceptance_ids': [acc.order_id]},
        )
        user = await dataset.user(store_id=cc.store_id)

        await wait_order_status(cc, ('request', 'begin'))
        tap.ok(await cc.ack(user), 'назначили юзера')
        await wait_order_status(cc, ('processing', 'begin'))
        tap.ok(await cc.cancel(user=user), 'отменили')
        await wait_order_status(cc, ('canceled', 'done'))
