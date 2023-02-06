import pytest

from scripts.dev.do_lost_product import psingle


@pytest.mark.parametrize(
    's1,s2,target_count',
    [
        (300, 1, 0),
        (300, 1, 199),
    ]
)
async def test_psingle(tap, dataset, uuid, s1, s2, target_count):
    with tap:
        product = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        stock = await dataset.stock(
            count=s1,
            product_id=product.product_id,
            store_id=store.store_id,
        )
        stock1 = await dataset.stock(
            count=s2,
            product_id=product.product_id,
            store_id=store.store_id,
        )

        order_external_id_suffix = uuid()

        order = await psingle(
            store,
            [(product, target_count)],
            user,
            order_external_id_suffix,
            True,
        )

        await stock.reload()
        await stock1.reload()

        lost_count = 0
        for sl in await dataset.StockLog.list(
                by='full',
                conditions=('order_id', order.order_id),
                sort=(),
        ):
            if sl.type == 'lost':
                lost_count += sl.delta_count

        tap.eq(stock.count + stock1.count, target_count, 'уменьшили остаток')
        tap.eq(
            (s1 + s2) - (stock.count + stock1.count),
            abs(lost_count),
            'есть операции с типом lost',
        )
        tap.eq(stock.reserve + stock1.reserve, 0, 'резерва нет')
