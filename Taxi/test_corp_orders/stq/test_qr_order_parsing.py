import decimal

from corp_orders.internal.order_parsing import qr_parser
from corp_orders.models import corp_user
from corp_orders.stq import corp_create_eda_order


async def test_grocery_order_parsing(stq3_context, mockserver, load_json):
    @mockserver.json_handler('/eats-corp-orders/v1/order')
    async def _qr_order(request):
        return load_json('qr_order.json')

    order = await corp_create_eda_order.fetch_qr_order(
        stq3_context, 'order_id',
    )
    parsed_order = await qr_parser.parse_order(
        stq3_context,
        decimal.Decimal('1.2'),
        'test_yandex_uid',
        corp_user.CorpUser(
            user_id='corp_user_id',
            client_id='corp_client_id',
            department_id='department_id',
        ),
        order,
        consumer_price_from_billing='123',
    )
    assert parsed_order.serialize() == load_json('expected_qr_order.json')
