import pytest


async def test_trash_no_trash_suggests(tap, dataset, wait_order_status):
    with tap.plan(13, 'Саджесты списания не генерим'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            type='stowage',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 127,
                    'maybe_count': True,
                    'valid': '2022-01-02',
                }
            ],
            status='reserving',
            estatus='begin',
            store=store,
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'с начала')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.count, 127, 'количество')
            tap.eq(s.type, 'box2shelf', 'тип')

            tap.ok(await s.done(count=127), 'закрыт саджест')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест и остался')


# pylint: disable=too-many-statements
@pytest.mark.parametrize('counts', [
    {
        'count': 127,
        'done': 103,
        'trash': 7,
        'desc': 'Есть все варианты',
        'number_of_tests': 22,
    },
    {
        'count': 127,
        'done': 0,
        'trash': 7,
        'desc': 'нет движения на полку',
        'number_of_tests': 22,
    },

    {
        'count': 127,
        'done': 102,
        'trash': 0,
        'desc': 'нет движения на списание',
        'number_of_tests': 21,
    },
    {
        'count': 127,
        'done': 127,
        'trash': 0,
        'desc': 'всё положено куда надо',
        'number_of_tests': 21,
    },
    {
        'count': 127,
        'done': 0,
        'trash': 127,
        'desc': 'Всё вообще списано',
        'number_of_tests': 22,
    },
])
async def test_trash(tap, dataset, wait_order_status, counts):
    with tap.plan(counts['number_of_tests'], counts['desc']):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            type='stowage',
            required=[
                {
                    'product_id': product.product_id,
                    'count': counts['count'],
                    'maybe_count': True,
                    'valid': '2025-11-12',
                }
            ],
            status='reserving',
            estatus='begin',
            store=store,
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'с начала')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.count, counts['count'], 'количество')
            tap.eq(s.type, 'box2shelf', 'тип')

            tap.ok(await s.done(count=counts['done']), 'закрыт саджест')

        with tap.subtest(None, 'Саджесты на списание') as taps:
            version = order.version

            await wait_order_status(order, ('processing', 'waiting'))
            suggests = await dataset.Suggest.list_by_order(order)
            if counts['done'] < counts['count']:
                taps.eq(len(suggests), 2, 'ещё саджест появился')
                taps.ne(order.version, version, 'версия поменялась')

                suggests = {s.vars('stage', 'stowage'): s for s in suggests}
                taps.in_ok('stowage', suggests, 'stowage есть в саджестах')
                taps.in_ok('trash', suggests, 'trash есть в саджестах')

                with suggests['trash'] as s:
                    taps.eq(s.product_id, product.product_id, 'товар')
                    taps.eq(s.count,
                            counts['count'] - counts['done'],
                            'количество')
                    taps.eq(s.type, 'box2shelf', 'тип')

                    taps.ok(await s.done(count=counts['trash']),
                            'закрыт саджест')
            else:
                taps.eq(len(suggests), 1, 'новых саджестов нет')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=[('store_id', store.store_id)],
            sort=(),
        )
        count_stocks = len(stocks.list)

        stocks = {s.shelf_type: s for s in stocks}
        tap.eq(len(stocks.keys()), count_stocks, 'остатков по типам')

        if 'store' in stocks:
            with stocks['store'] as s:
                tap.eq(s.reserve, 0, 'нет резерва')
                tap.eq(s.count, counts['done'], 'количество')
        else:
            tap.passed('нет резерва на полке')
            tap.passed('нулевое количество')

        if 'trash' in stocks:
            with stocks['trash'] as s:
                tap.eq(s.reserve, 0, 'нет резерва')
                tap.eq(s.count, counts['trash'], 'количество')
                tap.eq(
                    s.vars['reasons'][0][order.order_id]['reason_code'],
                    'TRASH_DAMAGE',
                    'причина есть'
                )
        else:
            tap.passed('нет резерва на полке')
            tap.passed('нулевое количество')

        if 'lost' in stocks:
            with stocks['lost'] as s:
                tap.eq(s.reserve, 0, 'нет резерва')
                tap.eq(s.count,
                       counts['count'] - counts['done'] - counts['trash'],
                       'количество')
        else:
            tap.passed('нет резерва на полке')
            tap.passed('нулевое количество')
