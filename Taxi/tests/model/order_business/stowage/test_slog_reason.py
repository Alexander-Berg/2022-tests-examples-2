import pytest
from stall.model.suggest_reason import TO_TRASH_REASONS, OLD_REASONS


@pytest.mark.parametrize('reason', set(TO_TRASH_REASONS)-set(OLD_REASONS))
async def test_process(tap, dataset, wait_order_status, reason):
    with tap.plan(21, f'Заполнение reason=TRASH_{reason}'):
        store = await dataset.full_store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        product = await dataset.product()
        tap.ok(product, 'товар сгенерирован')

        order = await dataset.order(
            type='stowage',
            status='reserving',
            acks=[user.user_id],
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 27,
                    'maybe_count': True,
                    'valid': '2012-11-05',
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.vars('mode'), 'product', 'обычный саджест')
            tap.eq(s.conditions.trash_reason, False, 'не требуется reason')
            tap.ok(await s.done(count=22), 'саджест завершён')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест на списание')
        with suggests[0] as s:
            tap.eq(s.vars('stage'), 'trash', 'списание')
            tap.eq(s.conditions.trash_reason, True, 'требуется reason')
            tap.ok(await s.done(count=2,
                                reason={'code': reason}),
                   'саджест завершён')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.StockLog.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
                ('shelf_type', ('store', 'trash'))
            ),
            sort=(),
        )
        tap.eq(len(stocks.list), 2, 'остатки')

        ss = next(s for s in stocks if s.shelf_type == 'store')
        tap.ok(ss, 'остаток на обычной полке есть')
        tap.eq(ss.reason, None, 'reason в обычном пуст')

        st = next(s for s in stocks if s.shelf_type == 'trash')
        tap.ok(st, 'остаток на списании есть')
        tap.ok(st.reason, 'reason заполнен')
        tap.eq(st.reason.code, reason, 'значение reason.code')
