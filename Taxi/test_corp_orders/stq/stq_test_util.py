import decimal
import json

PRECISION = decimal.Decimal('0.0001')


async def fetch_eda_order(ctx, order_id):
    query, query_args = ctx.sqlt(
        'eats_orders/find_orders.sqlt',
        {
            'order_id': order_id,
            'user_id': None,
            'client_id': None,
            'department_id': None,
            'department_ids': None,
            'since_datetime': None,
            'till_datetime': None,
            'limit': None,
            'offset': None,
        },
    )
    master_pool = ctx.pg.master[0]
    async with master_pool.acquire() as conn:
        await conn.set_type_codec(
            'jsonb',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog',
        )
        order_json = await conn.fetchrow(query, *query_args)

    if order_json:
        return order_json['value']
    return None


def get_sum_with_vat(discount_sum):
    decimal_sum = decimal.Decimal(discount_sum).quantize(PRECISION)
    vat_value = (decimal_sum * decimal.Decimal('0.2')).quantize(PRECISION)
    sum_with_vat = {
        'sum': str(decimal_sum),
        'vat': str(vat_value),
        'with_vat': str(decimal_sum + vat_value),
    }
    return sum_with_vat


def mock_fetching_eats_orders(mockserver, load_json, is_fetched_ok=True):
    results = {
        'eats': load_json('eats_order.json'),
        'grocery': load_json('grocery_order.json'),
        'grocery_raw': load_json('grocery_order_raw.json'),
    }

    if is_fetched_ok:

        @mockserver.json_handler('/eats-corp-orders/v1/order')
        async def _qr_order(request):
            return load_json('qr_order.json')

    else:
        results['eats']['orders'] = []
        results['grocery']['orders'] = []
        results['grocery_raw']['orders'] = []

        @mockserver.json_handler('/eats-corp-orders/v1/order')
        async def _qr_order(request):
            return mockserver.make_response(
                status=404, json={'message': 'Order not found'},
            )

    @mockserver.json_handler(
        '/eats-orderhistory-py3/internal-api/v1/orders/retrieve',
    )
    async def _orders_retrieve(request):
        return results['eats']

    @mockserver.json_handler('/grocery-order-log/internal/orders/v1/retrieve')
    async def _grocery_orders_retrieve(request):
        return results['grocery']

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    async def _grocery_orders_retrieve_raw(request):
        return results['grocery_raw']
