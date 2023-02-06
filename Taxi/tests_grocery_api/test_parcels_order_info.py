import pytest

from . import const


@pytest.mark.parametrize(
    'token_type, status',
    [
        pytest.param('some-token', 200, id='200 response on correct token'),
        pytest.param('bad-token', 404, id='404 response on bad token'),
    ],
)
async def test_parcels_order_info(
        taxi_grocery_api, mockserver, tristero_parcels, token_type, status,
):
    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID

    _prepare_tristero_parcels(
        tristero_parcels, vendor, order_id, ref_order, token, depot_id,
    )

    @mockserver.json_handler('/grocery-offers/v1/match/multi')
    def _match(request):
        # 'order-info' shouldn't retrieve data from '/match/multi'
        assert False

    response = await taxi_grocery_api.get(
        '/lavka/v1/api/v1/parcels/order_info',
        params={'vendor': vendor, 'ref_order': ref_order, 'token': token_type},
        headers={
            'X-YaTaxi-User': 'eats_user_id=12345',
            'X-YaTaxi-Session': 'taxi:taxi-user-id',
            'X-Yandex-UID': 'yandex-uid',
            'locale': 'ru',
        },
    )
    assert response.status_code == status

    if token_type == 'some-token':

        order_data = response.json()
        assert order_data['order_id'] == order_id
        assert order_data['depot_id'] == legacy_depot_id
        assert len(order_data['items']) == 3
        assert (
            order_data['customer_address']
            == 'ymapsbm1://geo?text=%D0%BA%D0%B0%D0%BA%D0%BE%D0%B9-'
            '%D1%82%D0%BE%20%D0%B0%D0%B4%D1%80%D0%B5%D1%81&ll=35.1%2C55.2'
        )
        assert order_data['customer_address_parsed'] == 'какой-то адрес'
        assert order_data['customer_location'] == [35.1, 55.2]
        assert (
            order_data['image_url_order_with_groceries']
            == 'image_url_order_with_groceries.jpg'
        )


@pytest.mark.parametrize(
    'can_left_at_door, restrictions',
    [(True, []), (False, ['parcel_too_expensive'])],
)
async def test_parcels_order_info_restrictions(
        taxi_grocery_api,
        overlord_catalog,
        mockserver,
        tristero_parcels,
        can_left_at_door,
        restrictions,
):
    """ order_info should return restrictions for each items
    item should be marked as too expensive if it cannot be
    left at door """
    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    depot_id = const.DEPOT_ID

    _prepare_tristero_parcels(
        tristero_parcels,
        vendor,
        order_id,
        ref_order,
        token,
        depot_id,
        can_left_at_door=can_left_at_door,
    )

    @mockserver.json_handler('/grocery-offers/v1/match/multi')
    def _match(request):
        # 'order-info' shouldn't retrieve data from '/match/multi'
        assert False

    response = await taxi_grocery_api.get(
        '/lavka/v1/api/v1/parcels/order_info',
        params={'vendor': vendor, 'ref_order': ref_order, 'token': token},
        headers={
            'X-YaTaxi-User': 'eats_user_id=12345',
            'X-YaTaxi-Session': 'taxi:taxi-user-id',
            'X-Yandex-UID': 'yandex-uid',
            'locale': 'ru',
        },
    )
    assert response.status_code == 200
    order_data = response.json()
    for item in order_data['items']:
        assert item['restrictions'] == restrictions


def _prepare_tristero_parcels(
        tristero_parcels,
        vendor: str,
        order_id: str,
        ref_order: str,
        token: str,
        depot_id: str,
        can_left_at_door: bool = True,
):
    order = tristero_parcels.add_order(
        vendor=vendor,
        order_id=order_id,
        ref_order=ref_order,
        status='received',
        depot_id=depot_id,
        delivery_date='2020-11-02T13:00:42.109234+00:00',
        token=token,
        customer_address='ymapsbm1://geo?text=%D0%BA%D0%B0%D0%BA%D0%BE%D0%B9-'
        '%D1%82%D0%BE%20%D0%B0%D0%B4%D1%80%D0%B5%D1%81'
        '&ll=35.1%2C55.2',
        customer_location=[35.1, 55.2],
        image_url_order_with_groceries='image_url_order_with_groceries.jpg',
    )
    order.add_parcel(
        parcel_id='98765432-10ab-cdef-0000-000001000001:st-pa',
        status='in_depot',
        title='\u041f\u043e\u0441\u044b\u043b\u043a\u0430',
        image_url_template='parcels-image_template.jpg',
        quantity_limit='1',
        can_left_at_door=can_left_at_door,
    )
    order.add_parcel(
        parcel_id='98765432-10ab-cdef-0000-000001000002:st-pa',
        status='in_depot',
        title='\u041f\u043e\u0441\u044b\u043b\u043a\u0430',
        image_url_template='parcels-image_template.jpg',
        quantity_limit='1',
        can_left_at_door=can_left_at_door,
    )
    order.add_parcel(
        parcel_id='98765432-10ab-cdef-0000-000001000003:st-pa',
        status='delivering',
        title='\u041f\u043e\u0441\u044b\u043b\u043a\u0430',
        image_url_template='parcels-image_template.jpg',
        quantity_limit='1',
        can_left_at_door=can_left_at_door,
    )
