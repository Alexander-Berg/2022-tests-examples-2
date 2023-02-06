import pytest


@pytest.mark.parametrize(
    'table, item_key, item_ids',
    [
        ('carts', 'cart_id', ['cart_id_1', 'cart_id_2']),
        ('order-log', 'order_id', ['order_id_1', 'order_id_2']),
        ('orders', 'order_id', ['order_id_1', 'order_id_2']),
        ('carts_checkout_data', 'cart_id', ['cart_id_1', 'cart_id_2']),
        ('carts-by-order-id', 'order_id', ['order_id_1', 'order_id_2']),
        ('invoices/receipts', 'order_id', ['order_id_1', 'order_id_2']),
        (
            'cargo_dispatches',
            'dispatch_id',
            ['dispatch_id_1', 'dispatch_id_2'],
        ),
    ],
)
@pytest.mark.yt(
    schemas=[
        'yt_carts_raw_schema.yaml',
        'yt_order_log_raw_schema.yaml',
        'yt_orders_raw_schema.yaml',
        'yt_carts_checkout_data_raw_schema.yaml',
        'yt_carts_by_order_id_schema.yaml',
        'yt_invoices_receipts_raw_schema.yaml',
        'yt_cargo_dispatches_raw_schema.yaml',
    ],
    dyn_table_data=[
        'yt_carts_raw.yaml',
        'yt_order_log_raw.yaml',
        'yt_orders_raw.yaml',
        'yt_carts_checkout_data_raw.yaml',
        'yt_carts_by_order_id.yaml',
        'yt_invoices_receipts_raw.yaml',
        'yt_cargo_dispatches_raw.yaml',
    ],
)
async def test_yt_basic(
        taxi_grocery_cold_storage, yt_apply, table, item_key, item_ids,
):
    response = await taxi_grocery_cold_storage.post(
        f'/internal/v1/cold-storage/v1/get/{table}',
        json={
            'item_ids': item_ids,
            'fields': [
                {
                    'name': 'required_string_field_without_default',
                    'type': 'string',
                    'is_required': True,
                },
                {
                    'name': 'required_string_field_with_default',
                    'type': 'string',
                    'is_required': True,
                    'default_value': 'string_1',
                },
                {
                    'name': 'optional_string_field',
                    'type': 'string',
                    'is_required': False,
                },
                {
                    'name': 'null_string_field',
                    'type': 'string',
                    'is_required': False,
                },
                {
                    'name': 'required_int_field',
                    'type': 'int',
                    'is_required': True,
                },
                {
                    'name': 'optional_int_field',
                    'type': 'int',
                    'is_required': False,
                },
                {
                    'name': 'required_object_field_without_default',
                    'type': 'object',
                    'is_required': True,
                },
                {
                    'name': 'required_object_field_with_default',
                    'type': 'object',
                    'is_required': True,
                    'default_value': {'int': 1, 'string': 'some_string_1'},
                },
                {
                    'name': 'optional_object_field',
                    'type': 'object',
                    'is_required': False,
                },
                {
                    'name': 'optional_object_str_field',
                    'type': 'object',
                    'is_required': False,
                },
                {
                    'name': 'optional_array_of_objects_field',
                    'type': 'array_of_objects',
                    'is_required': False,
                },
                {
                    'name': 'optional_array_of_objects_str_field',
                    'type': 'array_of_objects',
                    'is_required': False,
                },
                {
                    'name': 'required_array_of_objects_field_str_with_default',
                    'type': 'array_of_objects',
                    'is_required': True,
                    'default_value': [{'int': 1}],
                },
                {
                    'name': 'optional_array_of_strings_field',
                    'type': 'array_of_strings',
                    'is_required': False,
                },
                {
                    'name': 'optional_array_of_strings_str_field',
                    'type': 'array_of_strings',
                    'is_required': False,
                },
                {
                    'name': 'required_array_of_strings_field_with_default',
                    'type': 'array_of_strings',
                    'is_required': True,
                    'default_value': ['str1', 'str1'],
                },
                {
                    'name': 'optional_double_field',
                    'type': 'double',
                    'is_required': False,
                },
                {
                    'name': 'required_double_field_with_default',
                    'type': 'double',
                    'is_required': True,
                    'default_value': 1.45,
                },
                {
                    'name': 'optional_decimal_string',
                    'type': 'string',
                    'is_required': False,
                },
                {
                    'name': 'optional_datetime_string',
                    'type': 'string',
                    'is_required': False,
                },
                {
                    'name': 'optional_object_string_with_decimal_string',
                    'type': 'object',
                    'is_required': False,
                },
                {
                    'name': 'optional_object_with_decimal_string',
                    'type': 'object',
                    'is_required': False,
                },
                {
                    'name': 'optional_object_string_with_datetime_string',
                    'type': 'object',
                    'is_required': False,
                },
                {
                    'name': 'optional_object_with_datetime_string',
                    'type': 'object',
                    'is_required': False,
                },
                {
                    'name': (
                        'optional_array_of_objects_string_with_decimal_string'
                    ),
                    'type': 'array_of_objects',
                    'is_required': False,
                },
                {
                    'name': (
                        'optional_array_of_objects_string_with_datetime_string'
                    ),
                    'type': 'array_of_objects',
                    'is_required': False,
                },
            ],
        },
    )

    assert response.status_code == 200

    expected_json = {
        'items': [
            {
                'item_id': item_ids[0],
                'required_string_field_without_default': 'string_1',
                'required_string_field_with_default': 'string_1',
                'optional_string_field': 'string_1',
                'required_int_field': 100,
                'required_object_field_without_default': {
                    'int': 1,
                    'string': 'some_string_1',
                },
                'required_object_field_with_default': {
                    'int': 1,
                    'string': 'some_string_1',
                },
                'required_array_of_objects_field_str_with_default': [
                    {'int': 1},
                ],
                'required_array_of_strings_field_with_default': [
                    'str1',
                    'str1',
                ],
                'required_double_field_with_default': 1.45,
            },
            {
                'item_id': item_ids[1],
                'required_string_field_without_default': 'string_2',
                'required_string_field_with_default': 'string_2',
                'null_string_field': 'string_2',
                'required_int_field': 200,
                'optional_int_field': 400,
                'required_object_field_without_default': {
                    'int': 2,
                    'string': 'some_string_2',
                },
                'required_object_field_with_default': {
                    'int': 2,
                    'string': 'some_string_2',
                },
                'optional_object_field': {'int': 4},
                'optional_object_str_field': {'int': 2},
                'optional_array_of_objects_field': [{'int': 2}],
                'optional_array_of_objects_str_field': [{'int': 2}],
                'required_array_of_objects_field_str_with_default': [
                    {'int': 2},
                ],
                'optional_array_of_strings_field': ['str2', 'str2'],
                'optional_array_of_strings_str_field': ['str2', 'str2'],
                'required_array_of_strings_field_with_default': [
                    'str2',
                    'str2',
                ],
                'optional_double_field': 1.23,
                'required_double_field_with_default': 1.23,
                'optional_decimal_string': '1',
                'optional_datetime_string': '2020-11-25T16:01:03+0000',
                'optional_object_string_with_decimal_string': {'price': '1'},
                'optional_object_with_decimal_string': {'price': '1'},
                'optional_object_string_with_datetime_string': {
                    'updated': '2020-11-25T16:01:03+0000',
                },
                'optional_object_with_datetime_string': {
                    'updated': '2020-11-25T16:01:03+0000',
                },
                'optional_array_of_objects_string_with_decimal_string': [
                    {'price': '1'},
                ],
                'optional_array_of_objects_string_with_datetime_string': [
                    {'updated': '2020-11-25T16:01:03+0000'},
                ],
            },
        ],
    }
    for item, item_id in zip(expected_json['items'], item_ids):
        item[item_key] = item_id

    assert response.json() == expected_json


@pytest.mark.yt(
    schemas=[
        'yt_carts_raw_schema.yaml',
        'yt_carts_checkout_data_raw_schema.yaml',
    ],
    dyn_table_data=['yt_carts_checkout_data_raw.yaml'],
)
async def test_optional_object(taxi_grocery_cold_storage, yt_apply):
    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/carts_checkout_data',
        json={
            'item_ids': [
                'optional_object_without_value',
                'optional_object_with_value',
            ],
            'fields': [
                {
                    'name': 'optional_object',
                    'type': 'object',
                    'is_required': False,
                },
            ],
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        'items': [
            {
                'cart_id': 'optional_object_without_value',
                'item_id': 'optional_object_without_value',
            },
            {
                'cart_id': 'optional_object_with_value',
                'item_id': 'optional_object_with_value',
                'optional_object': {},
            },
        ],
    }
