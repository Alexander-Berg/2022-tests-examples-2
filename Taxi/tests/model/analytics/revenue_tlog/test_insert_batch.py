from stall.model.analytics.revenue_tlog import (
    RevenueTlog,
    REVENUE_TLOG_SOURCES,
)


async def test_insert_batch(tap, dataset, now):
    with tap.plan(2):
        store = await dataset.store()

        rows = []

        for _ in range(5):
            order = await dataset.order(store=store)
            product = await dataset.product()

            rows.append(
                {
                    'company_id': store.company_id,
                    'store_id': store.store_id,
                    'order_id': order.order_id,
                    'source': REVENUE_TLOG_SOURCES[0],
                    'transaction_id': int(now().timestamp() * 1000_000),
                    'transaction_dttm': now(),
                    'raw_data': {
                        'transaction_type': 'payment',
                        'transaction_product': 'smth',
                        'transaction_detailed_product': 'smth',
                        'aggregation_sign': 1,
                        'product_id': product.product_id,
                        'quantity': '300',
                        'amount_with_vat': '300',
                        'amount_without_vat': '300',
                        'vat_amount': '0',
                        'vat_rate': '0',
                    }
                }
            )

        tap.ok(await RevenueTlog.insert_batch(rows), 'вставили пачку')

        revenues = await RevenueTlog.list(
            by='full',
            conditions=('company_id', store.company_id),
            sort=(),
        )
        tap.eq(
            {i.transaction_id for i in revenues.list},
            {i['transaction_id'] for i in rows},
            'получили пачку',
        )
