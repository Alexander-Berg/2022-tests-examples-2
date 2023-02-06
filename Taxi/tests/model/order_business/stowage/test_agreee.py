import pytest


# pylint: disable=too-many-locals
@pytest.mark.parametrize('count_done', [11, 0])
async def test_agree(tap, dataset, wait_order_status, count_done, cfg):
    cfg.set(
        'business.order.stowage.suggest_conditions.need_valid.testing',
        False
    )
    cfg.set(
        'business.order.stowage.suggest_conditions.need_valid.local',
        False
    )
    with tap.plan(25, 'Раскладка после доверительной приёмки'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        p1, p2 = await dataset.product(), await dataset.product()
        tap.ok(p1, 'товар 1')
        tap.ok(p2, 'товар 2')

        order = await dataset.order(
            type='stowage',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            store=store,

            required=[
                {
                    'product_id': p1.product_id,
                    'count': 26,
                },
                {
                    'product_id': p2.product_id,
                    'count': 35,
                    'maybe_count': True,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.isa_ok(suggests, list, 'саджесты получены')
        tap.eq(len(suggests), 2, 'их два')

        s1 = [s for s in suggests if s.product_id == p1.product_id]
        tap.ok(s1, 'по первому продукту')
        s2 = [s for s in suggests if s.product_id == p2.product_id]
        tap.ok(s2, 'по второму продукту')

        for s in s1:
            tap.eq(s.type, 'box2shelf', 'тип саджеста 1')
            tap.eq(s.count, 26, 'количество')
            tap.eq(s.conditions.all, False, 'точное')
            with tap.raises(dataset.Suggest.ErAccessSuggestCount,
                            'нельзя неправильно закрывать'):
                await s.done(count=27)
            tap.ok(await s.reload(), 'перегрузили')
            tap.eq(s.status, 'request', 'не исполнен ещё')
            tap.ok(await s.done(count=26), 'завершили саджест')

        for s in s2:
            tap.eq(s.type, 'box2shelf', 'тип саджеста 2')
            tap.eq(s.count, 35, 'количество')
            tap.eq(s.conditions.all, True, 'точное')
            tap.eq(s.conditions.max_count, False, 'НЕ ограничено сверху')

            # with tap.raises(dataset.Suggest.ErSuggestCount,
            #                 'нельзя закрыть на большое значение'):
            #     await s.done(count=1122)
            tap.ok(await s.done(count=count_done), 'завершили саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('product_id', [p1.product_id, p2.product_id]),
                ('shelf_type', ['markdown', 'store']),
            ],
            sort=(),
        )
        result = {}
        for s in stocks:
            if s.product_id not in result:
                result[s.product_id] = {'count': 0, 'reserve': 0}

            result[s.product_id]['count'] += s.count
            result[s.product_id]['reserve'] += s.reserve

        tap.eq(result[p1.product_id],
               {'count': 26, 'reserve': 0},
               'итого остатки по товару 1')

        tap.eq(result.get(p2.product_id, {'count': 0, 'reserve': 0}),
               {'count': count_done, 'reserve': 0},
               'итого остатки по товару 2')
