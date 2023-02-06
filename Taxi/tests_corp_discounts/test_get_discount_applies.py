import pytest


@pytest.mark.parametrize(
    ['order_id', 'order_service', 'expected_status', 'expected_response'],
    [
        pytest.param(
            'order_1',
            'eats2',
            200,
            {
                'apply_timestamp': '2021-09-24T01:00:00+00:00',
                'client_id': 'client_1',
                'discount_amount': {
                    'sum': '256',
                    'vat': '51.2',
                    'with_vat': '317.2',
                },
                'is_reverted': True,
                'order_created': '2021-09-24T00:00:00+00:00',
                'order_id': 'order_1',
                'order_price': '1024',
                'order_version': 1,
                'service': 'eats2',
                'user_id': 'user_1',
            },
            id='found discount',
        ),
        pytest.param(
            'order_2',
            'taxi',
            404,
            {'message': 'Discount for order not found'},
            id='not found discount',
        ),
    ],
)
@pytest.mark.pgsql(
    'corp_discounts',
    files=[
        'insert_discounts.sql',
        'insert_discount_link.sql',
        'insert_apply_log.sql',
    ],
)
async def test_get_order_discount(
        taxi_corp_discounts,
        order_id,
        order_service,
        expected_status,
        expected_response,
):
    response = await taxi_corp_discounts.get(
        f'/v1/applies/get?order_id={order_id}&service={order_service}',
    )
    assert response.status == expected_status
    assert response.json() == expected_response
