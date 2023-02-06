import decimal

from corp_orders.internal.order_parsing import grocery_parser
from corp_orders.models import corp_user
from corp_orders.stq import corp_create_eda_order


async def test_grocery_order_parsing(stq3_context, mockserver, load_json):
    @mockserver.json_handler('/grocery-order-log/internal/orders/v1/retrieve')
    async def _grocery_orders_retrieve(request):
        return load_json('grocery_order.json')

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    async def _grocery_orders_retrieve_raw(request):
        return load_json('grocery_order_raw.json')

    order = await corp_create_eda_order.fetch_grocery_order(
        stq3_context, 'order_id', 'yandex_uid',
    )
    order_raw = await corp_create_eda_order.fetch_raw_grocery_order(
        stq3_context, 'order_id', 'yandex_uid',
    )
    parsed_order = await grocery_parser.parse_order(
        stq3_context,
        decimal.Decimal('1.2'),
        'test_yandex_uid',
        corp_user.CorpUser(
            user_id='corp_user_id',
            client_id='corp_client_id',
            department_id='department_id',
        ),
        order,
        order_raw,
        consumer_price_from_billing='123',
    )
    assert parsed_order.serialize() == load_json('expected_grocery_order.json')
