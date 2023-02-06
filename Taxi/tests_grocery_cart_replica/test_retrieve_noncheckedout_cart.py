def make_card_data(user_id, checked_out):
    return {
        'user_id': user_id,
        'checked_out': checked_out,
        'user_type': 'user_type_string',
        'cart_version': 4,
        'idempotency_token': 'idempotency_token_from_YT',
        'promocode': 'LAVKA1235',
        'promocode_source': 'taxi',
        'promocode_discount': '10',
        'promocode_properties': {
            'source': 'taxi',
            'discount_value': '10',
            'limit': '10',
            'tag': 'tag',
            'discount_type': 'fixed',
            'series_purpose': 'support',
        },
        'payment_method_type': 'payment',
        'payment_method_id': 'id',
        'personal_wallet_id': 'id',
        'items_v2': [
            {
                'info': {
                    'item_id': 'id',
                    'shelf_type': 'store',
                    'title': 'title_1',
                    'refunded_quantity': '0',
                    'vat': '20',
                    'width': 100,
                    'height': 100,
                    'depth': 100,
                    'gross_weight': 100,
                },
                'sub_items': [
                    {
                        'item_id': 'id',
                        'price': '100',
                        'paid_with_cashback': '110',
                        'paid_with_promocode': '90',
                        'full_price': '100',
                        'quantity': '1',
                    },
                ],
            },
        ],
        'items_v2_source': 'stored',
        'payment_method_discount': False,
        'delivery': {'cost': '100', 'max_eta': 40, 'min_eta': 10},
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
        'items_price_template': 'template',
        'total_item_discounts_template': 'template',
        'total_promocode_discount_template': 'template',
        'total_discount_template': 'template',
        'delivery_zone_type': 'pedestrian',
        'source': 'SQL',
        'tips': {'amount': '5', 'amount_type': 'absolute'},
        'limited_discount_ids': ['id_1', 'id_2'],
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
        'cart_id': 'e6a59113-503c-4d3e-8c59-000000000020',
        'exists_order_id': True,
        'client_price': '250',
        'total_discount': '10',
    }


CHECKED_OUT_CART = make_card_data('user_id_string1', True)
NON_CHECKED_OUT_CART = make_card_data('user_id_string2', False)

CART_DATA = [CHECKED_OUT_CART, NON_CHECKED_OUT_CART]


async def test_basic(mockserver, taxi_grocery_cart_replica):
    depot_id = '112233'

    @mockserver.json_handler('grocery-cart/internal/v1/cart/retrieve/by-depot')
    def check_promocode(request):  # pylint: disable=unused-variable
        body = request.json

        assert body['depot_id'] == depot_id

        return mockserver.make_response(status=200, json={'items': CART_DATA})

    response = await taxi_grocery_cart_replica.post(
        '/internal/v1/cart/retrieve/depot/non_checkedout',
        json={'depot_id': depot_id},
    )
    assert response.status_code == 200
    assert response.json() == {'items': [NON_CHECKED_OUT_CART]}

    # повторяем запрос по следам корки LAVKALOGDEV-1441
    response = await taxi_grocery_cart_replica.post(
        '/internal/v1/cart/retrieve/depot/non_checkedout',
        json={'depot_id': depot_id},
    )
    assert response.status_code == 200
