import datetime
import json
import random

import pytest

from testsuite.utils import ordered_object

from tests_tristero_parcels import headers


@pytest.mark.parametrize('order_state', ['received', 'cancelled'])
@pytest.mark.parametrize(
    'parcel_states',
    [
        [['in_depot'], ['in_depot', 'in_depot', 'ordered']],
        [['in_depot', 'in_depot'], ['created']],
        [['in_depot', 'in_depot', 'in_depot']],
    ],
)
@pytest.mark.parametrize('authorised', [True, False])
@pytest.mark.parametrize(
    'price_threshold, price, can_left_at_door',
    [('30000', '20000', True), ('3000', '20000', False), ('0', None, False)],
)
@pytest.mark.config(
    TRISTERO_PARCELS_VENDORS_SETTINGS={
        'vendor-000001': {
            'image-parcel': 'parcels-image_template.jpg',
            'image-informer': 'parcels-image_template.jpg',
        },
    },
)
async def test_internal_parcels_retrieve_orders_200(
        taxi_tristero_parcels,
        taxi_config,
        tristero_parcels_db,
        authorised,
        order_state,
        parcel_states,
        price_threshold,
        price,
        can_left_at_door,
):
    """ test POST /internal/v1/parcels/v1/retrieve-orders
    returns authorised user orders with parcels with statuses=in_depot,
    and returns nothind to unauthorised users """

    order_items = []
    depot_id = tristero_parcels_db.make_depot_id(1)

    taxi_config.set_values(
        {
            'TRISTERO_PARCELS_ITEM_PRICE_LEFT_AT_DOOR_THRESHOLD': (
                price_threshold
            ),
        },
    )

    # order = None
    with tristero_parcels_db as db:
        for i, parcels_statuses in enumerate(parcel_states):
            order = db.add_order(
                i + 1,
                user_id=headers.YANDEX_UID,
                depot_id=depot_id,
                status=order_state,
                customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
                customer_location='(35.1,55.2)',
                customer_meta=json.dumps({'some_key': 'some_value'}),
                price=price,
            )

            parcel_items = []
            for j, parcel_state in enumerate(parcels_statuses):
                parcel = order.add_parcel(j + 1, status=parcel_state)
                parcel_items.append(
                    {
                        'parcel_id': parcel.product_key,
                        'status': parcel_state,
                        'description': parcel.description,
                        'title': 'Посылка из Яндекс.Маркета',
                        'image_url_template': 'parcels-image_template.jpg',
                        'can_left_at_door': can_left_at_door,
                        'quantity_limit': (
                            '1'
                            if parcel_state in ['in_depot', 'ordered']
                            else '0'
                        ),
                    },
                )

            has_all_parcels_in_depot = all(
                [status == 'in_depot' for status in parcels_statuses],
            )
            if has_all_parcels_in_depot and order.status != 'cancelled':
                order_items.append(
                    {
                        'order_id': order.order_id,
                        'ref_order': order.ref_order,
                        'token': order.token,
                        'vendor': order.vendor,
                        'status': order_state,
                        'parcels': parcel_items,
                        'customer_address': (
                            'ymapsbm1://geo?some_text&ll=35.1%2C55.2'
                        ),
                        'customer_location': [35.1, 55.2],
                        'customer_meta': {'some_key': 'some_value'},
                        'depot_id': depot_id,
                    },
                )
    auth_headers = {}
    expected_response = {}
    if authorised:
        auth_headers = headers.DEFAULT_HEADERS
        expected_response['orders'] = order_items
    else:
        expected_response['orders'] = []

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/retrieve-orders',
        headers=auth_headers,
        json={'depot_id': depot_id},
    )
    response_data = response.json()
    assert response.status_code == 200
    assert 'orders' in response_data
    ordered_object.assert_eq(
        response_data, expected_response, ['orders', 'orders.parcels'],
    )


async def test_internal_parcels_retrieve_orders_in_another_depot(
        taxi_tristero_parcels, tristero_parcels_db,
):
    """ test POST /internal/v1/parcels/v1/retrieve-orders return nothing
    when parcels are in another depot """

    depot_id_parcels = tristero_parcels_db.make_depot_id(1)
    depot_id_user = tristero_parcels_db.make_depot_id(2)

    with tristero_parcels_db as db:
        order = db.add_order(
            1, user_id=headers.YANDEX_UID, depot_id=depot_id_parcels,
        )
        order.add_parcel(1, status='in_depot')

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/retrieve-orders',
        headers=headers.DEFAULT_HEADERS,
        json={'depot_id': depot_id_user},
    )
    response_data = response.json()
    assert response.status_code == 200
    assert 'orders' in response_data
    assert not response_data['orders']


async def test_internal_retrieve_order_groups(
        taxi_tristero_parcels, tristero_parcels_db, grocery_depots,
):
    """ Return order groups by uid. Should group in_depot orders by depots.
        Should group ordered orders by grocery_order_id.
        Should exclude delivered orders after some time.
        Group should have paid delivery if all orders are of wide_slot kind."""
    depot_id = tristero_parcels_db.make_depot_id(1)
    depot_id_2 = tristero_parcels_db.make_depot_id(2)

    legacy_depot_id = '123456'
    legacy_depot_id_2 = '654321'

    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id), depot_id=depot_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id_2), depot_id=depot_id_2,
    )

    await taxi_tristero_parcels.invalidate_caches()

    # will be excluded because some parcels are not even in depot yet
    order_0 = tristero_parcels_db.add_order(
        10, user_id=headers.YANDEX_UID, depot_id=depot_id,
    )
    order_0.add_parcel(1, status='in_depot')
    order_0.add_parcel(2, status='reserved')

    order_1 = tristero_parcels_db.add_order(
        1,
        user_id=headers.YANDEX_UID,
        depot_id=depot_id,
        request_kind='wide_slot',
        customer_location='(35.1,55.2)',
    )
    order_1.add_parcel(1, status='in_depot')
    order_1.add_parcel(2, status='in_depot')
    order_1.add_parcel(3, status='in_depot')

    order_2 = tristero_parcels_db.add_order(
        2,
        user_id=headers.YANDEX_UID,
        depot_id=depot_id,
        request_kind='wide_slot',
    )
    order_2.add_parcel(1, status='in_depot')
    order_2.add_parcel(2, status='in_depot')

    # will be excluded because has no grocery_order_id
    order_3 = tristero_parcels_db.add_order(
        3, user_id=headers.YANDEX_UID, depot_id=depot_id,
    )
    order_3.add_parcel(1, status='delivering')
    order_3.add_parcel(2, status='delivering')

    order_4 = tristero_parcels_db.add_order(
        4, user_id=headers.YANDEX_UID, depot_id=depot_id_2,
    )
    order_4.add_parcel(
        1, status='auto_ordered', status_meta=json.dumps({'order_id': '123'}),
    )

    order_5 = tristero_parcels_db.add_order(
        5, user_id=headers.YANDEX_UID, depot_id=depot_id, status='delivered',
    )
    order_5.add_parcel(
        1, status='delivered', status_meta=json.dumps({'order_id': '234'}),
    )
    order_5.set_updated(datetime.datetime.now() - datetime.timedelta(hours=1))

    # will be in a separate in_depot group because depot_id is different
    order_6 = tristero_parcels_db.add_order(
        6, user_id=headers.YANDEX_UID, depot_id=depot_id_2,
    )
    order_6.add_parcel(1, status='in_depot')

    # will be excluded because it was delivered long time ago
    order_7 = tristero_parcels_db.add_order(
        7, user_id=headers.YANDEX_UID, depot_id=depot_id_2,
    )
    order_7.add_parcel(
        1, status='delivered', status_meta=json.dumps({'order_id': '345'}),
    )
    order_7.set_updated(datetime.datetime.now() - datetime.timedelta(days=1))

    await taxi_tristero_parcels.invalidate_caches()

    expected_response = {
        'order_groups': [
            {
                'customer_location': [35.1, 55.2],
                'legacy_depot_id': legacy_depot_id,
                'has_paid_delivery': True,
                'orders': [
                    {
                        'ref_order': 'ref-order-000001',
                        'vendor': 'vendor-000001',
                        'token': 'some-token',
                    },
                    {
                        'ref_order': 'ref-order-000002',
                        'vendor': 'vendor-000001',
                        'token': 'some-token',
                    },
                ],
                'state': 'in_depot',
            },
            {
                'has_paid_delivery': False,
                'legacy_depot_id': legacy_depot_id_2,
                'orders': [
                    {
                        'ref_order': 'ref-order-000006',
                        'vendor': 'vendor-000001',
                        'token': 'some-token',
                    },
                ],
                'state': 'in_depot',
            },
            {
                'has_paid_delivery': False,
                'legacy_depot_id': legacy_depot_id_2,
                'orders': [
                    {
                        'ref_order': 'ref-order-000004',
                        'vendor': 'vendor-000001',
                        'token': 'some-token',
                    },
                ],
                'state': 'auto_ordered',
                'grocery_order_id': '123',
            },
            {
                'has_paid_delivery': False,
                'legacy_depot_id': legacy_depot_id,
                'orders': [
                    {
                        'ref_order': 'ref-order-000005',
                        'vendor': 'vendor-000001',
                        'token': 'some-token',
                    },
                ],
                'state': 'delivered',
                'grocery_order_id': '234',
            },
            {
                'has_paid_delivery': False,
                'legacy_depot_id': legacy_depot_id_2,
                'orders': [
                    {
                        'ref_order': 'ref-order-000007',
                        'vendor': 'vendor-000001',
                        'token': 'some-token',
                    },
                ],
                'state': 'delivered',
                'grocery_order_id': '345',
            },
        ],
    }

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/retrieve-order-groups',
        headers=headers.DEFAULT_HEADERS,
        json={},
    )

    response_data = response.json()
    assert response.status_code == 200
    assert response_data == expected_response


@pytest.mark.parametrize('uid', [None, headers.YANDEX_UID])
async def test_internal_retrieve_groups_no_uid(
        taxi_tristero_parcels, tristero_parcels_db, uid,
):
    """If request has no uid, return empty order_groups array"""
    depot_id = tristero_parcels_db.make_depot_id(1)
    order = tristero_parcels_db.add_order(
        1, user_id=headers.YANDEX_UID, depot_id=depot_id,
    )
    order.add_parcel(1, status='in_depot')
    order.add_parcel(2, status='in_depot')

    another_uid = 'not-the-same-uid'
    order_1 = tristero_parcels_db.add_order(
        2,
        user_id=another_uid,
        depot_id=depot_id,
        customer_meta=json.dumps({'order_id': '123'}),
    )
    order_1.add_parcel(1, status='delivering')

    request_headers = headers.DEFAULT_HEADERS
    request_headers['X-Yandex-UID'] = uid
    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/retrieve-order-groups',
        headers=request_headers,
        json={},
    )

    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data['order_groups']) == (0 if not uid else 1)


async def test_internal_retrieve_groups_sorted(
        taxi_tristero_parcels, tristero_parcels_db, grocery_depots,
):
    """Groups should be sorted by uid"""

    depot_id = tristero_parcels_db.make_depot_id(1)
    depot_id_2 = tristero_parcels_db.make_depot_id(2)

    legacy_depot_id = '123456'
    legacy_depot_id_2 = '654321'

    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id), depot_id=depot_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id_2), depot_id=depot_id_2,
    )

    await taxi_tristero_parcels.invalidate_caches()

    for i in random.sample(range(1, 100), 10):
        order_depot_1 = tristero_parcels_db.add_order(
            i,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id,
            request_kind='wide_slot',
            customer_location='(35.1,55.2)',
        )
        order_depot_1.add_parcel(1, status='in_depot')
    for i in random.sample(range(100, 141), 5):
        order_depot_2 = tristero_parcels_db.add_order(
            i,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id_2,
            customer_location='(35.1,55.2)',
        )
        order_depot_2.add_parcel(
            1,
            status='delivering',
            status_meta=json.dumps({'order_id': '123'}),
        )

    await taxi_tristero_parcels.invalidate_caches()

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/retrieve-order-groups',
        headers=headers.DEFAULT_HEADERS,
        json={},
    )

    response_data = response.json()
    assert response.status_code == 200

    for group in response_data['order_groups']:
        orders = group['orders']
        print(orders)
        assert all(
            orders[i]['ref_order'] < orders[i + 1]['ref_order']
            for i in range(len(orders) - 1)
        )
