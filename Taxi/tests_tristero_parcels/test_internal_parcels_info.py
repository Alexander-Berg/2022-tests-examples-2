import pytest

from testsuite.utils import ordered_object

from tests_tristero_parcels import headers


@pytest.mark.config(
    TRISTERO_PARCELS_VENDORS_SETTINGS={
        'vendor-000001': {
            'image-parcel': 'parcels-image_template.jpg',
            'image-informer': 'parcels-image_template.jpg',
        },
    },
)
@pytest.mark.parametrize(
    'status',
    [
        'reserved',
        'created',
        'in_depot',
        'courier_assigned',
        'ready_for_delivery',
        'delivering',
        'delivered',
        'ordered',
    ],
)
@pytest.mark.parametrize('order_cancelled', [True, False])
@pytest.mark.parametrize('header', [{}, headers.DEFAULT_HEADERS])
@pytest.mark.parametrize(
    'price_threshold, price, can_left_at_door',
    [('30000', '20000', True), ('3000', '20000', False), ('0', None, False)],
)
async def test_internal_parcels_infos(
        taxi_tristero_parcels,
        taxi_config,
        tristero_parcels_db,
        status,
        order_cancelled,
        header,
        price_threshold,
        price,
        can_left_at_door,
):
    """ test GET /internal/v1/parcels/v1/parcels-info returns
    parcels info by wms ids"""

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
    parcels_info = []
    parcel_product_keys = []

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id='does not matter',
            price=price,
            request_kind='hour_slot',
        )
        quantity_limit = '1' if status in ['in_depot', 'ordered'] else '0'
        # lets add some parcels
        for i in range(3):
            parcel = order.add_parcel(i + 1, status=status)
            parcels_info.append(
                {
                    'parcel_id': parcel.product_key,
                    'subtitle': parcel.description,
                    'title': 'Посылка из Яндекс.Маркета',
                    'image_url_template': config_vendors_settings[
                        'vendor-000001'
                    ]['image-parcel'],
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
                    'request_kind': order.request_kind,
                },
            )
            parcel_product_keys.append(parcel.product_key)

    if order_cancelled:
        order.set_status('cancelled')

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/parcels-info',
        headers=header,
        json={'parcel_ids': parcel_product_keys},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert 'parcels' in response_data
    if order_cancelled:
        assert not response_data['parcels']
    else:
        ordered_object.assert_eq(response_data['parcels'], parcels_info, [])


@pytest.mark.parametrize(
    'request_kind', ['hour_slot', 'wide_slot', 'on_demand', None],
)
async def test_internal_parcels_req_kind(
        taxi_tristero_parcels, tristero_parcels_db, request_kind,
):
    """ Check that parcels-info return kinds of request.
    In case order's request_kind is missing returns nothing"""

    parcel_product_keys = []

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id='does not matter',
            price='200',
            request_kind=request_kind,
        )
        # lets add some parcels
        for i in range(3):
            parcel = order.add_parcel(i + 1, status='in_depot')
            parcel_product_keys.append(parcel.product_key)

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/parcels-info',
        headers=headers.DEFAULT_HEADERS,
        json={'parcel_ids': parcel_product_keys},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert 'parcels' in response_data
    for parcel in response_data['parcels']:
        if request_kind:
            assert parcel['request_kind'] == request_kind
        else:
            assert 'request_kind' not in parcel
