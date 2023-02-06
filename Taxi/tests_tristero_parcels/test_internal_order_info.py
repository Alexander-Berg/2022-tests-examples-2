import json

import pytest

from tests_tristero_parcels import headers


# should be removed after token becomes required field
@pytest.mark.config(
    TRISTERO_PARCELS_VENDORS_SETTINGS={
        'vendor-000001': {
            'image-parcel': 'parcels-image_template.jpg',
            'image-informer': 'parcels-image_template.jpg',
            'image-order-with-groceries': 'order-with-groceries-image.jpg',
        },
    },
)
@pytest.mark.parametrize(
    'status',
    [
        'reserved',
        'created',
        'in_depot',
        'ready_for_delivery',
        'courier_assigned',
        'delivering',
        'delivered',
    ],
)
@pytest.mark.parametrize('order_cancelled', [True, False])
@pytest.mark.parametrize(
    'price_threshold, price, can_left_at_door',
    [('30000', '20000', True), ('3000', '20000', False), ('0', None, False)],
)
async def test_internal_order_info_by_uid(
        taxi_tristero_parcels,
        taxi_config,
        tristero_parcels_db,
        status,
        order_cancelled,
        price_threshold,
        price,
        can_left_at_door,
):
    """ test GET /internal/v1/parcels/v1/order-info returns
    order with parcels by ref_order + vendor + uid """

    taxi_config.set_values(
        {
            'TRISTERO_PARCELS_ITEM_PRICE_LEFT_AT_DOOR_THRESHOLD': (
                price_threshold
            ),
        },
    )

    config_vendors_settings = taxi_config.get(
        key='TRISTERO_PARCELS_VENDORS_SETTINGS',
    )
    parcels_info = {}
    parcel_product_keys = []
    depot_id = tristero_parcels_db.make_depot_id(1)
    partner_id = 'some_partner_id'

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id,
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
            customer_meta=json.dumps({'some_key': 'some_value'}),
            price=price,
        )
        quantity_limit = '1' if status == 'in_depot' else '0'
        expected_response = {}
        expected_response['items'] = []
        # lets add some parcels
        for i in range(3):
            parcel = order.add_parcel(
                i + 1, status=status, partner_id='some_partner_id',
            )
            parcels_info[parcel.product_key] = {
                'parcel_id': parcel.product_key,
                'subtitle': parcel.description,
                'title': 'Посылка из Яндекс.Маркета',
                'image_url_template': config_vendors_settings['vendor-000001'][
                    'image-parcel'
                ],
                'quantity_limit': quantity_limit,
                'depot_id': order.depot_id,
                'state': status,
                'state_meta': {},
                'barcode': parcel.barcode,
                'partner_id': partner_id,
                'measurements': parcel.get_measurements_as_object(),
                'order_id': '01234567-89ab-cdef-000a-000000000001',
                'vendor': 'vendor-000001',
                'can_left_at_door': can_left_at_door,
                'ref_order': order.ref_order,
            }
            parcel_product_keys.append(parcel.product_key)
            expected_response['items'].append(parcels_info[parcel.product_key])

    if order_cancelled:
        order.set_status('cancelled')

    response = await taxi_tristero_parcels.get(
        '/internal/v1/parcels/v1/order-info',
        headers=headers.DEFAULT_HEADERS,
        params={'ref_order': order.ref_order, 'vendor': order.vendor},
    )
    if order_cancelled:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        expected_response[
            'customer_address'
        ] = 'ymapsbm1://geo?some_text&ll=35.1%2C55.2'
        expected_response['customer_location'] = [35.1, 55.2]
        expected_response['customer_meta'] = {'some_key': 'some_value'}
        expected_response['ref_order'] = order.ref_order
        expected_response['vendor'] = order.vendor
        expected_response['token'] = order.token
        expected_response['depot_id'] = depot_id
        expected_response['order_id'] = '01234567-89ab-cdef-000a-000000000001'
        expected_response[
            'image_url_order_with_groceries'
        ] = 'order-with-groceries-image.jpg'
        response_data = response.json()
        response_data.pop('delivery_date')
        response_data.pop('state')
        assert response_data == expected_response


# should be removed after token becomes required field
async def test_internal_order_info_wrong_uid_for_order(
        taxi_tristero_parcels, taxi_config, tristero_parcels_db,
):
    with tristero_parcels_db as db:
        order = db.add_order(1, user_id='some_unknown_uid')
        order.add_parcel(1, status='in_depot')
    await taxi_tristero_parcels.invalidate_caches()

    response = await taxi_tristero_parcels.get(
        '/internal/v1/parcels/v1/order-info',
        headers=headers.DEFAULT_HEADERS,
        params={'ref_order': order.ref_order, 'vendor': order.vendor},
    )
    assert response.status_code == 403


@pytest.mark.config(
    TRISTERO_PARCELS_VENDORS_SETTINGS={
        'vendor-000001': {
            'image-parcel': 'parcels-image_template.jpg',
            'image-informer': 'parcels-image_template.jpg',
            'image-order-with-groceries': 'order-with-groceries-image.jpg',
        },
    },
)
@pytest.mark.parametrize(
    'status',
    [
        'reserved',
        'created',
        'in_depot',
        'ready_for_delivery',
        'courier_assigned',
        'delivering',
        'delivered',
    ],
)
@pytest.mark.parametrize('order_cancelled', [True, False])
@pytest.mark.parametrize(
    'price_threshold, price, can_left_at_door',
    [('30000', '20000', True), ('3000', '20000', False), ('0', None, False)],
)
async def test_internal_order_info_by_token(
        taxi_tristero_parcels,
        taxi_config,
        tristero_parcels_db,
        status,
        order_cancelled,
        price_threshold,
        price,
        can_left_at_door,
):
    """ test GET /internal/v1/parcels/v1/order-info returns
    order with parcels by ref_order + vendor + token, uid should be ignored """

    taxi_config.set_values(
        {
            'TRISTERO_PARCELS_ITEM_PRICE_LEFT_AT_DOOR_THRESHOLD': (
                price_threshold
            ),
        },
    )

    config_vendors_settings = taxi_config.get(
        key='TRISTERO_PARCELS_VENDORS_SETTINGS',
    )
    parcels_info = {}
    parcel_product_keys = []
    token = 'some-token'
    depot_id = tristero_parcels_db.make_depot_id(1)

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id='does not matter',
            token=token,
            depot_id=depot_id,
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
            customer_meta=json.dumps({'some_key': 'some_value'}),
            price=price,
        )
        expected_response = {}
        expected_response['items'] = []
        quantity_limit = '1' if status == 'in_depot' else '0'
        # lets add some parcels
        for i in range(3):
            parcel = order.add_parcel(i + 1, status=status)
            parcels_info[parcel.product_key] = {
                'parcel_id': parcel.product_key,
                'subtitle': parcel.description,
                'title': 'Посылка из Яндекс.Маркета',
                'image_url_template': config_vendors_settings['vendor-000001'][
                    'image-parcel'
                ],
                'quantity_limit': quantity_limit,
                'depot_id': order.depot_id,
                'state': status,
                'state_meta': {},
                'barcode': parcel.barcode,
                'measurements': parcel.get_measurements_as_object(),
                'order_id': '01234567-89ab-cdef-000a-000000000001',
                'vendor': 'vendor-000001',
                'can_left_at_door': can_left_at_door,
                'ref_order': order.ref_order,
            }
            parcel_product_keys.append(parcel.product_key)
            expected_response['items'].append(parcels_info[parcel.product_key])

    if order_cancelled:
        order.set_status('cancelled')

    response = await taxi_tristero_parcels.get(
        '/internal/v1/parcels/v1/order-info',
        headers=headers.DEFAULT_HEADERS,
        params={
            'ref_order': order.ref_order,
            'vendor': order.vendor,
            'token': token,
        },
    )
    if order_cancelled:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        expected_response[
            'customer_address'
        ] = 'ymapsbm1://geo?some_text&ll=35.1%2C55.2'
        expected_response['customer_location'] = [35.1, 55.2]
        expected_response['customer_meta'] = {'some_key': 'some_value'}
        expected_response['ref_order'] = order.ref_order
        expected_response['vendor'] = order.vendor
        expected_response['token'] = order.token
        expected_response['depot_id'] = depot_id
        expected_response['order_id'] = '01234567-89ab-cdef-000a-000000000001'
        expected_response[
            'image_url_order_with_groceries'
        ] = 'order-with-groceries-image.jpg'
        response_data = response.json()
        response_data.pop('delivery_date')
        response_data.pop('state')
        assert response_data == expected_response


@pytest.mark.parametrize('token', [None, 'some-id'])
async def test_internal_order_info_wrong_token_for_order(
        taxi_tristero_parcels, taxi_config, tristero_parcels_db, token,
):
    """ test GET /internal/v1/parcels/v1/order-info returns 403
    for wrong token, uid should be ignored """
    with tristero_parcels_db as db:
        order = db.add_order(1, user_id=headers.YANDEX_UID, token=token)
        order.add_parcel(1, status='in_depot')
    await taxi_tristero_parcels.invalidate_caches()

    response = await taxi_tristero_parcels.get(
        '/internal/v1/parcels/v1/order-info',
        headers=headers.DEFAULT_HEADERS,
        params={
            'ref_order': order.ref_order,
            'vendor': order.vendor,
            'token': 'some-other-token',
        },
    )
    assert response.status_code == 403


@pytest.mark.config(
    TRISTERO_PARCELS_VENDORS_SETTINGS={
        'vendor-000001': {
            'image-parcel': 'parcels-image_template.jpg',
            'image-informer': 'parcels-image_template.jpg',
            'image-order-with-groceries': 'order-with-groceries-image.jpg',
        },
    },
)
@pytest.mark.config(TRISTERO_PARCELS_USE_GROCERY_LOCALIZATION=True)
@pytest.mark.config(
    GROCERY_LOCALIZATION_USED_KEYSETS=['virtual_catalog', 'tristero'],
)
@pytest.mark.config(
    GROCERY_LOCALIZATION_FALLBACK_LOCALES={'__default__': [], 'fr': ['en']},
)
@pytest.mark.parametrize('status', ['reserved'])
@pytest.mark.parametrize('order_cancelled', [False])
@pytest.mark.parametrize(
    'price_threshold, price, can_left_at_door', [('30000', '20000', True)],
)
@pytest.mark.parametrize(
    'locale, title',
    [
        ('ru', 'Посылка из Яндекс.Маркета'),
        ('en', 'Parcel from Yandex.Market'),
        ('fr', 'Parcel from Yandex.Market'),
    ],
)
async def test_internal_order_info_using_grocery_localization(
        taxi_tristero_parcels,
        taxi_config,
        tristero_parcels_db,
        status,
        order_cancelled,
        price_threshold,
        price,
        can_left_at_door,
        locale,
        title,
):
    taxi_config.set_values(
        {
            'TRISTERO_PARCELS_ITEM_PRICE_LEFT_AT_DOOR_THRESHOLD': (
                price_threshold
            ),
        },
    )

    config_vendors_settings = taxi_config.get(
        key='TRISTERO_PARCELS_VENDORS_SETTINGS',
    )
    parcels_info = {}
    parcel_product_keys = []
    token = 'some-token'
    depot_id = tristero_parcels_db.make_depot_id(1)

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id='does not matter',
            token=token,
            depot_id=depot_id,
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
            customer_meta=json.dumps({'some_key': 'some_value'}),
            price=price,
        )
        expected_response = {}
        expected_response['items'] = []
        quantity_limit = '1' if status == 'in_depot' else '0'
        # lets add some parcels
        for i in range(3):
            parcel = order.add_parcel(i + 1, status=status)
            parcels_info[parcel.product_key] = {
                'parcel_id': parcel.product_key,
                'subtitle': parcel.description,
                'title': title,
                'image_url_template': config_vendors_settings['vendor-000001'][
                    'image-parcel'
                ],
                'quantity_limit': quantity_limit,
                'depot_id': order.depot_id,
                'state': status,
                'state_meta': {},
                'barcode': parcel.barcode,
                'measurements': parcel.get_measurements_as_object(),
                'order_id': '01234567-89ab-cdef-000a-000000000001',
                'vendor': 'vendor-000001',
                'can_left_at_door': can_left_at_door,
                'ref_order': order.ref_order,
            }
            parcel_product_keys.append(parcel.product_key)
            expected_response['items'].append(parcels_info[parcel.product_key])

    if order_cancelled:
        order.set_status('cancelled')

    custom_headers = headers.DEFAULT_HEADERS.copy()
    custom_headers['X-Request-Language'] = locale

    response = await taxi_tristero_parcels.get(
        '/internal/v1/parcels/v1/order-info',
        headers=custom_headers,
        params={
            'ref_order': order.ref_order,
            'vendor': order.vendor,
            'token': token,
        },
    )
    if order_cancelled:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        expected_response[
            'customer_address'
        ] = 'ymapsbm1://geo?some_text&ll=35.1%2C55.2'
        expected_response['customer_location'] = [35.1, 55.2]
        expected_response['customer_meta'] = {'some_key': 'some_value'}
        expected_response['ref_order'] = order.ref_order
        expected_response['vendor'] = order.vendor
        expected_response['token'] = order.token
        expected_response['depot_id'] = depot_id
        expected_response['order_id'] = '01234567-89ab-cdef-000a-000000000001'
        expected_response[
            'image_url_order_with_groceries'
        ] = 'order-with-groceries-image.jpg'
        response_data = response.json()
        response_data.pop('delivery_date')
        response_data.pop('state')
        assert response_data == expected_response
