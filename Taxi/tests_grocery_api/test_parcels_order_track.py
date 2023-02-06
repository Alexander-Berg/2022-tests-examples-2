from . import const


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


EXPECTED_TRACKING_INFO = {
    'order_id': '4fe795ed-afd8-41d2-9f73-bb4333437bb5',
    'short_order_id': '280920-a-2254655',
    'order_info': {
        'order_id': '01234567-89ab-cdef-000a-000000000001',
        'vendor': 'vendor-000001',
        'ref_order': 'reforder-0000001',
        'token': 'some-token',
        'depot_id': const.LEGACY_DEPOT_ID,
        'items': [
            {
                'parcel_id': '98765432-10ab-cdef-0000-000001000001:st-pa',
                'depot_id': const.LEGACY_DEPOT_ID,
                'quantity_limit': '1',
                'title': 'Посылка',
                'state': 'in_depot',
                'restrictions': [],
            },
        ],
        'customer_address': 'какой-то адрес',
        'customer_address_uri': (
            'ymapsbm1://geo?text=%D0%BA%D0%B0%D0%BA%D0%BE%D0%B9-'
            '%D1%82%D0%BE%20%D0%B0%D0%B4%D1%80%D0%B5%D1%81&ll=35.1%2C55.2'
        ),
        'customer_location': [35.1, 55.2],
        'state': 'received',
    },
    'status': 'assembled',
    'delivery_eta_min': 3,
    'client_price_template': '1000$SIGN$$CURRENCY$',
    'location': [10.0, 20.0],
    'address': {
        'country': 'order_country',
        'city': 'order_city',
        'street': 'order_street',
        'house': 'order_building',
        'floor': 'order_floor',
        'flat': 'order_flat',
        'doorcode': 'order_doorcode',
        'place_id': 'place-id',
    },
    'depot_location': [13.0, 37.0],
    'promise_max': '2020-05-25T15:38:45+00:00',
    'localized_promise': 'Заказ приедет к ~ 18:38',
    'courier_info': {'name': 'Ivan', 'transport_type': 'car'},
    'tracking_info': {'title': 'Ещё примерно 56 минут'},
    'actions': [{'type': 'call_courier'}],
}


async def test_parcels_order_track_empty_response(
        taxi_grocery_api, tristero_parcels, mockserver,
):
    vendor = 'vendor-000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/order/track',
        json={'vendor': vendor, 'ref_order': ref_order, 'token': token},
        headers={
            'X-YaTaxi-User': 'eats_user_id=12345',
            'X-YaTaxi-Session': 'taxi:taxi-user-id',
            'X-Yandex-UID': 'yandex-uid',
            'locale': 'ru',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_parcels_order_track_happy_path(
        taxi_grocery_api, tristero_parcels, mockserver, overlord_catalog,
):
    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    can_left_at_door = True

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

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/order/track',
        json={'vendor': vendor, 'ref_order': ref_order, 'token': token},
        headers={
            'X-YaTaxi-User': 'eats_user_id=12345',
            'X-YaTaxi-Session': 'taxi:taxi-user-id',
            'X-Yandex-UID': 'yandex-uid',
            'locale': 'ru',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    for key, value in EXPECTED_TRACKING_INFO.items():
        assert response_json['order'][key] == value
    # TODO: check order info
