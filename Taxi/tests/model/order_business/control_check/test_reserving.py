async def test_one_acc(tap, dataset, wait_order_status):
    with tap.plan(3, 'одна приемка'):
        acc = await dataset.order(
            type='acceptance',
            required=[
                {'product_id': '111', 'count': 1},
                {'product_id': '222', 'count': 2},
                {'product_id': '333', 'weight': 2231}
            ],
        )
        cc = await dataset.order(
            type='control_check',
            vars={'acceptance_ids': [acc.order_id]},
        )

        await wait_order_status(cc, ('request', 'begin'))
        tap.eq(set(cc.products), {'111', '222'}, 'продукты')
        tap.eq(
            sorted(cc.required, key=lambda r: r.product_id),
            [
                {'product_id': '111', 'count': 1},
                {'product_id': '222', 'count': 2},
            ],
            'req что нада'
        )


async def test_exp(tap, dataset, wait_order_status):
    with tap.plan(3, 'одна приемка'):
        store = await dataset.store(options={'exp_wolf_messing': False})
        acc = await dataset.order(
            type='acceptance',
            required=[
                {'product_id': '111', 'count': 1},
                {'product_id': '222', 'count': 2},
                {'product_id': '333', 'weight': 2231}
            ],
        )
        cc = await dataset.order(
            store=store,
            type='control_check',
            vars={'acceptance_ids': [acc.order_id]},
        )

        await wait_order_status(cc, ('request', 'begin'))
        tap.eq(set(cc.products), {'111', '222'}, 'продукты')
        tap.eq(
            cc.required,
            [],
            'req пустой без экспа'
        )


async def test_two_acc(tap, dataset, cfg, wait_order_status):
    with tap.plan(3, 'две приемки'):
        cfg('cursor.limit', 1)
        single_store = await dataset.store()
        acc1 = await dataset.order(
            store=single_store,
            type='acceptance',
            required=[
                {
                    'product_id': '111',
                    'count': 2,
                },
                {
                    'product_id': '222',
                    'count': 3,
                },
            ],
        )
        acc2 = await dataset.order(
            store=single_store,
            type='acceptance',
            required=[
                {
                    'product_id': '333',
                    'count': 10,
                },
                {
                    'product_id': '222',
                    'count': 12,
                }
            ],
        )
        cc = await dataset.order(
            type='control_check',
            vars={'acceptance_ids': [acc1.order_id, acc2.order_id]},
        )

        await wait_order_status(cc, ('request', 'begin'))
        tap.eq(set(cc.products), {'111', '222', '333'}, 'продукты')
        tap.eq(
            sorted(cc.required, key=lambda r: r.product_id),
            [
                {'product_id': '111', 'count': 2},
                {'product_id': '222', 'count': 15},
                {'product_id': '333', 'count': 10},
            ],
            'req что нада'
        )
