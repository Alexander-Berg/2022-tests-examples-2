import datetime

import pytest
import pytz


@pytest.mark.parametrize(
    'flow_type, order_source, expected_order_type, expected_shipping_type, '
    'expected_default_catalog_type',
    [
        pytest.param(
            'retail', 'eda', 'retail', 'delivery', 'eats_nomenclature',
        ),
        pytest.param(
            'retail', 'lavka', 'lavka', 'delivery', 'eats_nomenclature',
        ),
        pytest.param('native', 'eda', 'native', 'delivery', 'core_catalog'),
        pytest.param(
            'burger_king', 'eda', 'fast_food', 'delivery', 'core_catalog',
        ),
        pytest.param('pickup', 'eda', 'native', 'pickup', 'core_catalog'),
        pytest.param(
            'pharmacy', 'eda', 'pharmacy', 'delivery', 'core_catalog',
        ),
        pytest.param('shop', 'eda', 'shop', 'delivery', 'core_catalog'),
        pytest.param(
            'fuelfood', 'eda', 'fuel_food', 'delivery', 'core_catalog',
        ),
        pytest.param(
            'fuelfood_rosneft', 'eda', 'fuel_food', 'delivery', 'core_catalog',
        ),
        pytest.param('native', 'lavka', 'lavka', 'delivery', 'core_catalog'),
        pytest.param('shop', 'lavka', 'lavka', 'delivery', 'core_catalog'),
    ],
)
@pytest.mark.parametrize(
    'stq_task_id, stq_task_order, db_expected_order, '
    'db_expected_cart, db_expected_address',
    [
        pytest.param(
            '1234:in_progress',
            {
                'eats_user_id': 12345,
                'place_id': 123,
                'delivery_location': {'lon': 12.34, 'lat': 34.56},
                'total_amount': '123.45',
                'is_asap': True,
                'created_at': '2019-10-31T11:20:00+00:00',
                'cart': [],
            },
            (
                '1234',
                12345,
                None,
                None,
                123,
                'taken',
                '(12.34,34.56)',
                '123.45',
                True,
                None,
                datetime.datetime(2019, 10, 31, 11, 20),
                None,
            ),
            [],
            ('1234', None, None, None, None, None, None),
            id='in_progress minimal',
        ),
        pytest.param(
            '1234:in_progress',
            {
                'eats_user_id': 12345,
                'taxi_user_id': 'taxi-user-id',
                'yandex_uid': 'yandex-uid',
                'place_id': 123,
                'delivery_location': {
                    'lon': 12.34,
                    'lat': 34.56,
                    'full_address': 'full_address_1',
                    'entrance': 'entrance_1',
                    'floor_number': 'floor_number_1',
                    'office': 'office_1',
                    'doorcode': 'doorcode_1',
                    'comment': 'comment_1',
                },
                'total_amount': '123.45',
                'is_asap': True,
                'created_at': '2019-10-31T11:20:00+00:00',
                'cart': [],
            },
            (
                '1234',
                12345,
                'taxi-user-id',
                'yandex-uid',
                123,
                'taken',
                '(12.34,34.56)',
                '123.45',
                True,
                None,
                datetime.datetime(2019, 10, 31, 11, 20),
                None,
            ),
            [],
            (
                '1234',
                'full_address_1',
                'entrance_1',
                'floor_number_1',
                'office_1',
                'doorcode_1',
                'comment_1',
            ),
            id='in_progress full',
        ),
        pytest.param(
            '1234:cancelled',
            {
                'eats_user_id': 12345,
                'taxi_user_id': 'taxi-user-id',
                'yandex_uid': 'yandex-uid',
                'place_id': 123,
                'delivery_location': {
                    'lon': 12.34,
                    'lat': 34.56,
                    'full_address': 'full_address_2',
                    'entrance': 'entrance_2',
                    'floor_number': 'floor_number_2',
                    'office': 'office_2',
                    'doorcode': 'doorcode_2',
                    'comment': 'comment_2',
                },
                'total_amount': '123.45',
                'is_asap': True,
                'cancel_reason': 'cancel-reason',
                'created_at': '2019-10-31T11:20:00+00:00',
                'delivered_at': '2019-10-31T12:00:00+00:00',
                'cart': [],
            },
            (
                '1234',
                12345,
                'taxi-user-id',
                'yandex-uid',
                123,
                'cancelled',
                '(12.34,34.56)',
                '123.45',
                True,
                'cancel-reason',
                datetime.datetime(2019, 10, 31, 11, 20),
                datetime.datetime(2019, 10, 31, 12, 0),
            ),
            [],
            (
                '1234',
                'full_address_2',
                'entrance_2',
                'floor_number_2',
                'office_2',
                'doorcode_2',
                'comment_2',
            ),
            id='cancelled full',
        ),
        pytest.param(
            '1234:delivered',
            {
                'eats_user_id': 12345,
                'taxi_user_id': 'taxi-user-id',
                'yandex_uid': 'yandex-uid',
                'place_id': 123,
                'delivery_location': {
                    'lon': 12.34,
                    'lat': 34.56,
                    'full_address': 'full_address_3',
                    'entrance': 'entrance_3',
                    'floor_number': 'floor_number_3',
                    'office': 'office_3',
                    'doorcode': 'doorcode_3',
                    'comment': 'comment_3',
                },
                'total_amount': '123.45',
                'is_asap': True,
                'created_at': '2019-10-31T11:20:00+00:00',
                'delivered_at': '2019-10-31T12:00:00+00:00',
                'cart': [
                    {
                        'place_menu_item_id': 1,
                        'product_id': '1',
                        'name': 'name-1',
                        'quantity': 1,
                        'origin_id': '1',
                        'catalog_type': 'core_catalog',
                    },
                    {
                        'place_menu_item_id': 2,
                        'name': 'name-2',
                        'quantity': 1,
                        'product_id': 'product_id',
                        'catalog_type': 'eats_nomenclature',
                    },
                    {
                        'place_menu_item_id': 2,
                        'name': 'name-2',
                        'quantity': 1,
                        'product_id': 'product_id',
                        'catalog_type': 'eats_nomenclature',
                    },
                ],
            },
            (
                '1234',
                12345,
                'taxi-user-id',
                'yandex-uid',
                123,
                'finished',
                '(12.34,34.56)',
                '123.45',
                True,
                None,
                datetime.datetime(2019, 10, 31, 11, 20),
                datetime.datetime(2019, 10, 31, 12, 0),
            ),
            [
                ('1234', 1, 'name-1', 1, '1', 'core_catalog'),
                ('1234', 2, 'name-2', 2, 'product_id', 'eats_nomenclature'),
            ],
            (
                '1234',
                'full_address_3',
                'entrance_3',
                'floor_number_3',
                'office_3',
                'doorcode_3',
                'comment_3',
            ),
            id='delivered full with cart',
        ),
        pytest.param(
            '1234:delivered',
            {
                'eats_user_id': 12345,
                'taxi_user_id': 'taxi-user-id',
                'yandex_uid': 'yandex-uid',
                'place_id': 123,
                'delivery_location': {
                    'lon': 12.34,
                    'lat': 34.56,
                    'full_address': 'full_address_3',
                    'entrance': 'entrance_3',
                    'floor_number': 'floor_number_3',
                    'office': 'office_3',
                    'doorcode': 'doorcode_3',
                    'comment': 'comment_3',
                },
                'total_amount': '123.45',
                'is_asap': True,
                'created_at': '2019-10-31T11:20:00+00:00',
                'delivered_at': '2019-10-31T12:00:00+00:00',
                'cart': [
                    {
                        'place_menu_item_id': 1,
                        'product_id': '1',
                        'name': 'name-1',
                        'quantity': 1,
                    },
                    {
                        'catalog_type': 'eats_nomenclature',
                        'origin_id': '2',
                        'name': 'name-2',
                        'quantity': 2,
                    },
                    {
                        'catalog_type': 'eats_nomenclature',
                        'product_id': 'some_product_id',
                        'name': 'name-3',
                        'quantity': 1,
                    },
                    {
                        'catalog_type': 'eats_nomenclature',
                        'product_id': 'some_product_id',
                        'name': 'name-3',
                        'quantity': 1,
                    },
                ],
            },
            (
                '1234',
                12345,
                'taxi-user-id',
                'yandex-uid',
                123,
                'finished',
                '(12.34,34.56)',
                '123.45',
                True,
                None,
                datetime.datetime(2019, 10, 31, 11, 20),
                datetime.datetime(2019, 10, 31, 12, 0),
            ),
            [
                ('1234', 1, 'name-1', 1, '1'),
                ('1234', 2, 'name-2', 2, '2', 'eats_nomenclature'),
                (
                    '1234',
                    0,
                    'name-3',
                    2,
                    'some_product_id',
                    'eats_nomenclature',
                ),
            ],
            (
                '1234',
                'full_address_3',
                'entrance_3',
                'floor_number_3',
                'office_3',
                'doorcode_3',
                'comment_3',
            ),
            id='delivered full with cart without place_menu_item_id',
        ),
        pytest.param(
            '1234:delivered',
            {
                'eats_user_id': 12345,
                'taxi_user_id': 'taxi-user-id',
                'yandex_uid': 'yandex-uid',
                'place_id': 123,
                'delivery_location': {
                    'lon': 12.34,
                    'lat': 34.56,
                    'full_address': 'full_address_3',
                    'entrance': 'entrance_3',
                    'floor_number': 'floor_number_3',
                    'office': 'office_3',
                    'doorcode': 'doorcode_3',
                    'comment': 'comment_3',
                },
                'total_amount': '123.45',
                'is_asap': True,
                'created_at': '2019-10-31T11:20:00+00:00',
                'delivered_at': '2019-10-31T12:00:00+00:00',
                'cart': [
                    {
                        'place_menu_item_id': 1,
                        'origin_id': '1',
                        'product_id': 'product_id_1',
                        'name': 'name-1',
                        'quantity': 1,
                    },
                    {
                        'place_menu_item_id': 2,
                        'catalog_type': 'eats_nomenclature',
                        'product_id': 'product_id_2',
                        'name': 'name-2',
                        'quantity': 2,
                    },
                    {
                        'catalog_type': 'eats_nomenclature',
                        'product_id': 'product_id_3',
                        'name': 'name-3',
                        'quantity': 1,
                    },
                    {
                        'origin_id': '4',
                        'catalog_type': 'eats_nomenclature',
                        'product_id': 'product_id_4',
                        'name': 'name-3',
                        'quantity': 1,
                    },
                ],
            },
            (
                '1234',
                12345,
                'taxi-user-id',
                'yandex-uid',
                123,
                'finished',
                '(12.34,34.56)',
                '123.45',
                True,
                None,
                datetime.datetime(2019, 10, 31, 11, 20),
                datetime.datetime(2019, 10, 31, 12, 0),
            ),
            [
                ('1234', 1, 'name-1', 1, 'product_id_1'),
                ('1234', 2, 'name-2', 2, 'product_id_2', 'eats_nomenclature'),
                ('1234', 0, 'name-3', 1, 'product_id_3', 'eats_nomenclature'),
                ('1234', 0, 'name-3', 1, 'product_id_4', 'eats_nomenclature'),
            ],
            (
                '1234',
                'full_address_3',
                'entrance_3',
                'floor_number_3',
                'office_3',
                'doorcode_3',
                'comment_3',
            ),
            id='delivered full with cart origin_id from product_id',
        ),
    ],
)
async def test_stq_add_order(
        stq,
        taxi_eats_ordershistory,
        pgsql,
        stq_task_id,
        stq_task_order,
        db_expected_order,
        db_expected_cart,
        db_expected_address,
        flow_type,
        order_source,
        expected_order_type,
        expected_shipping_type,
        expected_default_catalog_type,
):
    stq_task_order['flow_type'] = flow_type
    stq_task_order['order_source'] = order_source
    request_body = {
        'queue_name': 'eats_ordershistory_add_order',
        'task_id': stq_task_id,
        'args': [],
        'kwargs': {'order': stq_task_order},
    }
    response = await taxi_eats_ordershistory.post(
        'testsuite/stq', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {'failed': False}

    assert stq.eats_ordershistory_update_order_info.times_called > 0

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT order_id, eats_user_id, taxi_user_id, yandex_uid, place_id, '
        'status, delivery_location, total_amount, is_asap, cancel_reason, '
        'created_at, delivered_at, flow_type, order_source, order_type, '
        'shipping_type '
        'FROM eats_ordershistory.orders WHERE order_id = %s;',
        (stq_task_id[0 : stq_task_id.find(':')],),
    )
    orders = list(cursor)
    assert len(orders) == 1
    db_expected_order = db_expected_order + (
        flow_type,
        order_source,
        expected_order_type,
        expected_shipping_type,
    )
    for order_item, expected_item in zip(orders[0], db_expected_order):
        assert _pg_to_plain(order_item) == expected_item

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT order_id, place_menu_item_id, name, quantity, '
        'origin_id, catalog_type '
        'FROM eats_ordershistory.cart_items WHERE order_id = %s;',
        (stq_task_id[0 : stq_task_id.find(':')],),
    )

    db_expected_cart = await _add_default_catalog_type_to_tuple(
        db_expected_cart, expected_default_catalog_type,
    )

    assert list(cursor) == db_expected_cart

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT * FROM eats_ordershistory.addresses WHERE order_id = %s;',
        (stq_task_id[0 : stq_task_id.find(':')],),
    )
    assert list(cursor)[0] == db_expected_address


def _pg_to_plain(order_item):
    if isinstance(order_item, datetime.datetime):
        if order_item.tzinfo is not None:
            order_item = order_item.astimezone(pytz.UTC).replace(tzinfo=None)
    return order_item


async def _add_default_catalog_type_to_tuple(
        db_expected_cart, expected_default_catalog_type,
):
    new_db_expected_cart = []
    for cart in db_expected_cart:
        if len(cart) < 6:
            new_db_expected_cart.append(
                cart + (expected_default_catalog_type,),
            )
        else:
            new_db_expected_cart.append(cart)
    return new_db_expected_cart
