import datetime

# todo add delivery_types
def insert_surge_query(
        created,
        depot_id='100',
        pipeline='pipeline_1',
        load_level=777,
        delivery_types=tuple(),
):
    delivery_types_str = ','.join(
        f'"{item}"' for item in delivery_types
    )  # "a","b","c"
    seq_ts = created - datetime.timedelta(seconds=30)
    return (
        f'INSERT INTO surge.calculated '
        f'(seq_ts, created, pipeline, depot_id, load_level, delivery_types) '
        f'VALUES (\'{seq_ts.isoformat()}\', \'{created.isoformat()}\', '
        f'\'{pipeline}\', \'{depot_id}\', {load_level}, '
        f'\'{{{delivery_types_str}}}\');'
    )


NOW = datetime.datetime.fromisoformat('2021-01-01T21:00:00+00:00')
TIMESTAMPS = [NOW - datetime.timedelta(seconds=s) for s in range(0, 10)][::-1]
CALCULATED_SURGE_INFO_TTL = 1800


def make_card_data(user_id, checked_out):
    data = {
        'user_id': user_id,
        'checked_out': checked_out,
        'user_type': 'user_type_string',
        'cart_version': 4,
        'idempotency_token': 'idempotency_token_from_YT',
        'promocode': 'LAVKA1235',
        'promocode_source': 'taxi',
        'payment_method_type': 'payment',
        'payment_method_id': 'id',
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
        'source': 'SQL',
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
    }

    if checked_out:
        data['payment_method_discount'] = False
        data['delivery_zone_type'] = 'pedestrian'
        data['personal_wallet_id'] = 'id'
        data['promocode_discount'] = '10'
        data['promocode_properties'] = {
            'source': 'taxi',
            'discount_value': '10',
            'limit': '10',
            'tag': 'tag',
            'discount_type': 'fixed',
            'series_purpose': 'support',
        }
        data['delivery'] = {'cost': '100', 'max_eta': 40, 'min_eta': 10}
        data['limited_discount_ids'] = ['id_1', 'id_2']

    return data


CART_DATA = make_card_data('user_id_string', True)
CART_DATA_NON_CHECKED = make_card_data('user_id_string1', False)
