import json

import pytest

from tests_tristero_parcels import headers


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
async def test_internal_retrieve_orders_v2_basic(
        taxi_tristero_parcels,
        taxi_config,
        tristero_parcels_db,
        status,
        order_cancelled,
        price_threshold,
        price,
        can_left_at_door,
):
    """ Checks retrieving known orders. Also retrieves other
    orders of this used in this depot because no explicit depot_id provided """
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
                i + 1, status=status, partner_id=partner_id,
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

        order_same_depot = db.add_order(
            2,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id,
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
            customer_meta=json.dumps({'some_key': 'some_value'}),
            price=price,
        )
        by_depot_id_expected_items = []
        for i in range(2):
            state = 'in_depot'
            parcel = order_same_depot.add_parcel(
                10 + i, status=state, partner_id=partner_id,
            )
            parcels_info[parcel.product_key] = {
                'parcel_id': parcel.product_key,
                'subtitle': parcel.description,
                'title': 'Посылка из Яндекс.Маркета',
                'image_url_template': config_vendors_settings['vendor-000001'][
                    'image-parcel'
                ],
                'quantity_limit': '1',
                'depot_id': order_same_depot.depot_id,
                'state': state,
                'state_meta': {},
                'barcode': parcel.barcode,
                'partner_id': partner_id,
                'measurements': parcel.get_measurements_as_object(),
                'order_id': '01234567-89ab-cdef-000a-000000000002',
                'vendor': 'vendor-000001',
                'can_left_at_door': can_left_at_door,
                'ref_order': order_same_depot.ref_order,
            }
            by_depot_id_expected_items.append(parcels_info[parcel.product_key])

    if order_cancelled:
        order.set_status('cancelled')

    response = await taxi_tristero_parcels.post(
        'internal/v1/parcels/v2/retrieve-orders',
        headers=headers.DEFAULT_HEADERS,
        json={
            'known_orders': [
                {'ref_order': order.ref_order, 'vendor': order.vendor},
            ],
        },
    )

    assert response.status_code == 200
    if order_cancelled:
        assert not response.json()['orders']
    else:
        assert 'depot_id' in response.json()
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
        known_orders_data = response.json()['orders'][0]
        known_orders_data.pop('delivery_date')
        known_orders_data.pop('state')
        assert known_orders_data == expected_response

        assert len(response.json()['orders'][1:]) == 1
        by_depot_data = response.json()['orders'][1]
        expected_response['items'] = by_depot_id_expected_items
        expected_response['ref_order'] = order_same_depot.ref_order
        expected_response['token'] = order_same_depot.token
        expected_response['order_id'] = '01234567-89ab-cdef-000a-000000000002'
        by_depot_data.pop('delivery_date')
        by_depot_data.pop('state')

        assert by_depot_data == expected_response

    print(response.json())


async def test_internal_retrieve_orders_v2_token(
        taxi_tristero_parcels, tristero_parcels_db,
):
    """ For known orders uid is not required be identical to
    order's uid if the correct token provided """
    depot_id = 'some_depot_id'
    another_uid = 'another_uid'

    order1 = tristero_parcels_db.add_order(
        1, user_id=headers.YANDEX_UID, depot_id=depot_id,
    )
    order1.add_parcel(1, status='in_depot')

    order2 = tristero_parcels_db.add_order(
        2, user_id=another_uid, depot_id=depot_id,
    )
    order2.add_parcel(1, status='ready_for_delivery')

    response = await taxi_tristero_parcels.post(
        'internal/v1/parcels/v2/retrieve-orders',
        headers=headers.DEFAULT_HEADERS,
        json={
            'known_orders': [
                {
                    'ref_order': order1.ref_order,
                    'vendor': order1.vendor,
                    'token': order1.token,
                },
                {
                    'ref_order': order2.ref_order,
                    'vendor': order2.vendor,
                    'token': order2.token,
                },
            ],
        },
    )
    response_json = response.json()

    assert len(response_json['orders']) == 2
    assert response_json['orders'][0]['token'] == order1.token
    assert response_json['orders'][1]['token'] == order2.token


async def test_internal_retrieve_orders_v2_by_depot(
        taxi_tristero_parcels, tristero_parcels_db,
):
    """Check conditions for retrieving unknown orders by depot and uid"""
    depot_id = 'some_depot_id'
    order = tristero_parcels_db.add_order(
        1, user_id=headers.YANDEX_UID, depot_id=depot_id,
    )
    parcel = order.add_parcel(1, status='in_depot')

    tristero_parcels_db.add_order(
        2, user_id=headers.YANDEX_UID, depot_id=depot_id,
    )  # order without parcels

    bad_order_2 = tristero_parcels_db.add_order(
        3, user_id=headers.YANDEX_UID, depot_id=depot_id,
    )  # not all parcels in depot
    bad_order_2.add_parcel(1, status='in_depot')
    bad_order_2.add_parcel(2, status='delivering')

    response = await taxi_tristero_parcels.post(
        'internal/v1/parcels/v2/retrieve-orders',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [], 'depot_id': depot_id},
    )
    response_json = response.json()
    assert len(response_json['orders']) == 1
    assert response_json['orders'][0]['order_id'] == order.order_id
    assert (
        response_json['orders'][0]['items'][0]['parcel_id']
        == parcel.product_key
    )


@pytest.mark.parametrize('error_cause', ['uid', 'token'])
async def test_internal_retrieve_orders_v2_uid_token_missmatch(
        taxi_tristero_parcels, tristero_parcels_db, error_cause,
):
    """ Skips order when token or uid missmatched """

    depot_id = 'some_depot_id'

    if error_cause == 'uid':
        uid = 'wrong_uid'
        token = None
    else:
        uid = headers.YANDEX_UID
        token = 'wrong_token'

    order = tristero_parcels_db.add_order(1, user_id=uid, depot_id=depot_id)
    order.add_parcel(1, status='in_depot')

    body = {
        'known_orders': [
            {'ref_order': order.ref_order, 'vendor': order.vendor},
        ],
    }
    if token:
        body['known_orders'][0]['token'] = token

    response = await taxi_tristero_parcels.post(
        'internal/v1/parcels/v2/retrieve-orders',
        headers=headers.DEFAULT_HEADERS,
        json=body,
    )
    assert response.status_code == 200
    assert not response.json()['orders']


async def test_internal_retrieve_orders_v2_unauthorized(taxi_tristero_parcels):
    response = await taxi_tristero_parcels.post(
        'internal/v1/parcels/v2/retrieve-orders',
        headers={},
        json={
            'depot_id': '023fffdff84144238fba02c84296c898000100010001',
            'known_orders': [],
        },
    )
    assert response.status_code == 200
