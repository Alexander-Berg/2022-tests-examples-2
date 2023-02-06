async def test_no_products_acc(tap, dataset, wait_order_status):
    with tap.plan(2, 'нет продуктов в приемке'):
        acc = await dataset.order(
            type='acceptance',
            required=[],
        )
        cc = await dataset.order(
            type='control_check',
            vars={'acceptance_ids': [acc.order_id]},
        )

        await wait_order_status(cc, ('failed', 'done'))
        tap.eq(cc.problems[0].type, 'empty_products', 'нет продуктов')


async def test_no_counts_acc(tap, dataset, wait_order_status):
    with tap.plan(2, 'нет количества'):
        acc = await dataset.order(
            type='acceptance',
            required=[{'product_id': '111'}, {'product_id': '222'}],
        )
        cc = await dataset.order(
            type='control_check',
            vars={'acceptance_ids': [acc.order_id]},
        )

        await wait_order_status(cc, ('failed', 'done'))
        tap.eq(cc.problems[0].type, 'empty_products', 'нет продуктов')


async def test_no_accs(tap, dataset, wait_order_status):
    with tap.plan(2, 'нет приемок'):
        cc = await dataset.order(type='control_check')

        await wait_order_status(cc, ('failed', 'done'))
        tap.eq(cc.problems[0].type, 'empty_products', 'нет продуктов')
