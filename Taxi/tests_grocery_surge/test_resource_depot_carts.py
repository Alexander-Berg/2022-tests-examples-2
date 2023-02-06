import pytest

CARTS = [
    {
        'user_id': 'user_id_string1',
        'checked_out': False,
        'user_type': 'user_type_string',
        'cart_version': 4,
        'idempotency_token': 'idempotency_token_from_YT',
        'promocode': 'LAVKA1235',
        'promocode_source': 'taxi',
        'payment_method_type': 'payment',
        'payment_method_id': 'id',
        'discounts_info': [
            {
                'item_id': 'id',
                'discounts': [
                    {
                        'type': 'cashback',
                        'discount_description': 'text',
                        'value_template': 'template',
                    },
                ],
                'total_discount_template': 'template',
            },
        ],
        'full_total_template': 'template',
        'client_price_template': 'template',
        'items_full_price_template': 'template',
        'total_item_discounts_template': 'template',
        'total_promocode_discount_template': 'template',
        'total_discount_template': 'template',
        'tips': {'amount': '5', 'amount_type': 'absolute'},
        'items': [
            {
                'id': 'id_1',
                'product_key': {'id': 'key_1', 'shelf_type': 'store'},
                'price': '100',
                'price_template': '500 $SIGN$$CURRENCY$',
                'full_price_template': '500 $SIGN$$CURRENCY$',
                'title': 'Item 1',
                'full_price': '100',
                'currency': 'RUB',
                'vat': '20',
                'quantity': '1',
                'width': 100,
                'height': 100,
                'depth': 100,
                'gross_weight': 100,
                'cashback_per_unit': '1',
                'refunded_quantity': '0',
            },
            {
                'id': 'id_2',
                'product_key': {'id': 'key_2', 'shelf_type': 'store'},
                'price': '150',
                'price_template': '500 $SIGN$$CURRENCY$',
                'full_price_template': '500 $SIGN$$CURRENCY$',
                'title': 'Item 2',
                'full_price': '150',
                'currency': 'RUB',
                'vat': '20',
                'quantity': '1',
                'width': 100,
                'height': 100,
                'depth': 100,
                'gross_weight': 100,
                'cashback_per_unit': '1',
                'refunded_quantity': '0',
            },
        ],
        'delivery_type': 'eats_dispatch',
        'cart_id': '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9',
        'exists_order_id': True,
        'client_price': '250',
        'total_discount': '10',
    },
]


@pytest.mark.now('2020-07-07T00:00:00Z')
@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'test_pipeline'}]},
    is_config=True,
)
async def test_resource_depot_carts(stq_runner, mockserver, testpoint):
    depot_id = '1'

    @testpoint('wrap_depot_carts_resource_output')
    def depot_shifts_result(val):
        assert val == {'carts': CARTS}

    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id='task_id',
        kwargs={'pipeline': 'test_pipeline', 'depot_id': depot_id},
    )

    assert depot_shifts_result.times_called == 1
