import pytest

from . import const
from . import experiments


@pytest.mark.parametrize(
    'config_enabled, orders_size', [(True, 1), (False, 0)],
)
async def test_parcels_retrieve_orders_config(
        taxi_grocery_api,
        experiments3,
        tristero_parcels,
        config_enabled,
        orders_size,
):
    """ /retrieve-orders should return nothing if lavka_parcel
    config is disabled """

    experiments.lavka_parcel_config(experiments3, enabled=config_enabled)

    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'

    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID

    tristero_order = _prepare_tristero_parcels(
        tristero_parcels, vendor, order_id, ref_order, token, depot_id,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json={
            'known_orders': [
                {'vendor': vendor, 'ref_order': ref_order, 'token': token},
            ],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['orders']) == orders_size
    if orders_size > 0:
        _check_response_order(
            tristero_order, response_json['orders'][0], legacy_depot_id,
        )


@pytest.mark.parametrize(
    'request_token, orders_size',
    [
        pytest.param('some-token', 1, id='same token'),
        pytest.param('bad-token', 0, id='other token'),
        pytest.param(None, 0, id='no token'),
    ],
)
async def test_parcels_retrieve_known_orders(
        taxi_grocery_api,
        experiments3,
        tristero_parcels,
        request_token,
        orders_size,
):
    """ /retrieve-orders should return known orders if order token
    is same with request token """

    experiments.lavka_parcel_config(experiments3, enabled=True)

    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'

    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID

    tristero_order = _prepare_tristero_parcels(
        tristero_parcels, vendor, order_id, ref_order, token, depot_id,
    )

    json = {'known_orders': [{'vendor': vendor, 'ref_order': ref_order}]}
    if request_token is not None:
        json['known_orders'][0]['token'] = request_token

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders', json=json,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json['orders']) == orders_size

    if orders_size > 0:
        _check_response_order(
            tristero_order, response_json['orders'][0], legacy_depot_id,
        )


@pytest.mark.parametrize(
    'request_uid, orders_size',
    [
        pytest.param('some-uid', 1, id='same uid'),
        pytest.param('bad-uid', 0, id='other uid'),
        pytest.param(None, 0, id='no uid'),
    ],
)
async def test_parcels_retrieve_known_orders_by_uid(
        taxi_grocery_api,
        experiments3,
        tristero_parcels,
        request_uid,
        orders_size,
):
    """ /retrieve-orders should return known orders if order token
    is not specified but order can be matched by uid """

    experiments.lavka_parcel_config(experiments3, enabled=True)

    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    uid = 'some-uid'

    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID

    tristero_order = _prepare_tristero_parcels(
        tristero_parcels,
        vendor,
        order_id,
        ref_order,
        token,
        depot_id,
        uid=uid,
    )

    json = {'known_orders': [{'vendor': vendor, 'ref_order': ref_order}]}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json=json,
        headers={'X-Yandex-UID': request_uid},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json['orders']) == orders_size

    if orders_size > 0:
        _check_response_order(
            tristero_order, response_json['orders'][0], legacy_depot_id,
        )


@pytest.mark.parametrize(
    'location, request_uid, orders_size',
    [
        pytest.param([37, 55], 'some-uid', 1, id='depot found, good uid'),
        pytest.param([37, 55], 'bad-uid', 0, id='depot found, bad uid'),
        pytest.param([10, 10], 'some-uid', 0, id='depot not found'),
    ],
)
async def test_parcels_retrieve_order_by_position(
        taxi_grocery_api,
        overlord_catalog,
        experiments3,
        tristero_parcels,
        location,
        request_uid,
        orders_size,
        grocery_depots,
):
    """ /retrieve-orders should return orders from depot if
    position is specified, orders are matching by uid """

    experiments.lavka_parcel_config(experiments3, enabled=True)

    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    uid = 'some-uid'

    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID

    tristero_order = _prepare_tristero_parcels(
        tristero_parcels,
        vendor,
        order_id,
        ref_order,
        token,
        depot_id,
        uid=uid,
        with_delivering_parcel=False,
    )

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        location=[37, 55],
    )

    overlord_catalog.clear()
    overlord_catalog.add_depot(
        depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    overlord_catalog.add_location(
        location=[37, 55], depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )

    await taxi_grocery_api.invalidate_caches()

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json={'position': {'location': location}},
        headers={'X-Yandex-UID': request_uid},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['orders']) == orders_size

    if orders_size > 0:
        _check_response_order(
            tristero_order, response_json['orders'][0], legacy_depot_id,
        )


@pytest.mark.parametrize(
    'can_left_at_door, restrictions',
    [(True, []), (False, ['parcel_too_expensive'])],
)
async def test_parcels_retrieve_restrictions(
        taxi_grocery_api,
        experiments3,
        tristero_parcels,
        can_left_at_door,
        restrictions,
):
    """ retrieve-orders should return restrictions for each item
    item should be marked as too expensive if it cannot be
    left at door """

    experiments.lavka_parcel_config(experiments3, enabled=True)

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
        can_left_at_door,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json={
            'known_orders': [
                {'vendor': vendor, 'ref_order': ref_order, 'token': token},
            ],
        },
    )
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json['orders']) == 1
    order_items = response_json['orders'][0]['items']
    assert order_items
    for item in order_items:
        assert item['restrictions'] == restrictions


@pytest.mark.config(
    TRISTERO_PARCELS_VENDORS_SETTINGS={
        'vendor-000001': {
            'image-parcel': 'zakusaka-image-parcel.jpg',
            'image-informer': 'zakusaka-image-informer.jpg',
            'image-informer-modal': 'zakusaka-image-informer-modal.jpg',
            'image-order-with-groceries': 'zakusaka-image-with-groceries.jpg',
        },
    },
)
async def test_parcels_retrieve_orders_informer(
        taxi_grocery_api, experiments3, tristero_parcels,
):
    """ /retrieve-orders should return informer about
    tristero orders """

    experiments.lavka_parcel_config(experiments3, enabled=True)

    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    depot_id = const.DEPOT_ID

    _prepare_tristero_parcels(
        tristero_parcels, vendor, order_id, ref_order, token, depot_id,
    )

    json = {
        'known_orders': [
            {'vendor': vendor, 'ref_order': ref_order, 'token': token},
        ],
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json=json,
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert response_json['informer'] == {
        'modal': {
            'buttons': [
                {
                    'variant': 'default',
                    'action': 'go_cart',
                    'background_color': '#f5f4f2',
                    'text': 'Перейти в корзину',
                },
                {
                    'variant': 'default',
                    'action': 'go_catalog',
                    'background_color': '#fce000',
                    'text': 'Перейти в каталог',
                },
            ],
            'text': (
                'Ваш заказ от ООО Закусака уже в корзине, можете вызвать '
                'курьера, а можете захватить что-то ещё из Лавки'
            ),
            'title': 'Ваш заказ от ООО Закусака',
            'picture': 'zakusaka-image-informer-modal.jpg',
        },
        'picture': 'zakusaka-image-informer.jpg',
        'show_in_root': True,
        'text': (
            'Ваш заказ от ООО Закусака уже в корзине, можете вызвать '
            'курьера, а можете захватить что-то ещё из Лавки'
        ),
    }
    assert response_json['image_url_order'] == 'zakusaka-image-parcel.jpg'
    assert (
        response_json['image_url_order_with_groceries']
        == 'zakusaka-image-with-groceries.jpg'
    )


async def test_parcels_retrieve_orders_delivery_options_on_demand(
        taxi_grocery_api, experiments3, tristero_parcels,
):
    """ /retrieve-orders should return single options for
    on demand orders """

    experiments.lavka_parcel_config(experiments3, enabled=True)

    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    depot_id = const.DEPOT_ID

    _prepare_tristero_parcels(
        tristero_parcels, vendor, order_id, ref_order, token, depot_id,
    )

    json = {
        'known_orders': [
            {'vendor': vendor, 'ref_order': ref_order, 'token': token},
        ],
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json=json,
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['orders'][0]['delivery_options'] == [
        {
            'button_subtitle': 'сейчас',
            'button_title': 'Доставить',
            'price_template': '0 $SIGN$$CURRENCY$',
            'selected': True,
            'subtitle': 'Через 15-30 минут',
            'title': 'Сейчас',
            'type': 'order_now',
        },
    ]
    assert response_json['currency'] == 'RUB'
    assert response_json['currency_sign'] == '₽'


@pytest.mark.now('2021-12-13T17:09:00+03:00')
async def test_parcels_retrieve_orders_delivery_options_timeslot(
        taxi_grocery_api, experiments3, tristero_parcels,
):
    """ /retrieve-orders should return single options for
    on demand orders """

    experiments.lavka_parcel_config(experiments3, enabled=True)
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
        timeslot_start='2021-12-15T17:09:00+03:00',
        timeslot_end='2021-12-15T18:09:00+03:00',
    )

    json = {
        'known_orders': [
            {'vendor': vendor, 'ref_order': ref_order, 'token': token},
        ],
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json=json,
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['orders'][0]['delivery_options'] == [
        {
            'button_subtitle': 'Доставить 15.12 с 17:09 до 18:09',
            'button_title': 'Хорошо',
            'price_template': '0 $SIGN$$CURRENCY$',
            'selected': True,
            'title': '15.12 с 17:09 до 18:09',
            'type': 'timeslot_dispatch',
        },
        {
            'button_subtitle': 'сейчас',
            'button_title': 'Доставить',
            'price_template': '0 $SIGN$$CURRENCY$',
            'selected': False,
            'subtitle': 'Через 15-30 минут',
            'title': 'Сейчас',
            'type': 'order_now',
        },
    ]
    assert response_json['currency'] == 'RUB'
    assert response_json['currency_sign'] == '₽'


@pytest.mark.now('2021-12-13T17:09:00+03:00')
async def test_parcels_retrieve_orders_delivery_options_alternative_timeslot(
        taxi_grocery_api, experiments3, tristero_parcels,
):
    experiments.lavka_parcel_config(experiments3, enabled=True)
    alternative_timeslots = [
        {
            'start': '2021-12-14T18:09:00+03:00',
            'end': '2021-12-14T19:09:00+03:00',
        },
        {
            'start': '2021-12-15T18:09:00+03:00',
            'end': '2021-12-15T19:09:00+03:00',
        },
    ]
    alternative_timeslots_utc = [
        {
            'start': '2021-12-14T15:09:00+00:00',
            'end': '2021-12-14T16:09:00+00:00',
        },
        {
            'start': '2021-12-15T15:09:00+00:00',
            'end': '2021-12-15T16:09:00+00:00',
        },
    ]
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
        timeslot_start='2021-12-15T17:09:00+03:00',
        timeslot_end='2021-12-15T18:09:00+03:00',
        alternative_timeslots=alternative_timeslots,
    )

    json = {
        'known_orders': [
            {'vendor': vendor, 'ref_order': ref_order, 'token': token},
        ],
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json=json,
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['orders'][0]['delivery_options'][2] == {
        'button_subtitle': 'Доставить завтра с 18:09 до 19:09',
        'button_title': 'Сохранить',
        'price_template': '0 $SIGN$$CURRENCY$',
        'selected': False,
        'title': 'Изменить дату и время',
        'timeslot': alternative_timeslots_utc[0],
        'time_range_string': '18:09 – 19:09',
        'localized_timeslot_date': 'Завтра',
        'type': 'modify_timeslot',
    }

    assert response_json['orders'][0]['delivery_options'][3] == {
        'button_subtitle': 'Доставить 15.12 с 18:09 до 19:09',
        'button_title': 'Сохранить',
        'price_template': '0 $SIGN$$CURRENCY$',
        'selected': False,
        'title': 'Изменить дату и время',
        'timeslot': alternative_timeslots_utc[1],
        'time_range_string': '18:09 – 19:09',
        'localized_timeslot_date': '15.12',
        'type': 'modify_timeslot',
    }

    assert response_json['orders'][0]['delivery_options'][4] == {
        'button_subtitle': 'Вызвать когда будет удобно',
        'button_title': 'Сохранить',
        'price_template': '0 $SIGN$$CURRENCY$',
        'selected': False,
        'subtitle': 'Доставка за 15 – 30 минут',
        'title': 'Пока не знаю когда',
        'type': 'order_later',
    }


@pytest.mark.now('2021-12-31T10:09:00+03:00')
@pytest.mark.parametrize(
    'timeslot',
    [
        [
            'Доставить сегодня',
            {
                'start': '2021-12-31T17:09:00+03:00',
                'end': '2021-12-31T18:09:00+03:00',
            },
        ],
        [
            'Доставить завтра',
            {
                'start': '2022-01-01T17:09:00+03:00',
                'end': '2022-01-01T18:09:00+03:00',
            },
        ],
        [
            'Доставить 03.01',
            {
                'start': '2022-01-03T17:09:00+03:00',
                'end': '2022-01-03T18:09:00+03:00',
            },
        ],
    ],
)
async def test_parcels_incorrect_subtitle_fix(
        taxi_grocery_api, experiments3, tristero_parcels, timeslot,
):
    experiments.lavka_parcel_config(experiments3, enabled=True)

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
        timeslot_start=timeslot[1]['start'],
        timeslot_end=timeslot[1]['end'],
    )

    json = {
        'known_orders': [
            {'vendor': vendor, 'ref_order': ref_order, 'token': token},
        ],
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json=json,
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['orders'][0]['delivery_options'][0][
        'button_subtitle'
    ].startswith(timeslot[0])


@pytest.mark.parametrize(
    'config_availability, catalog_available',
    [(None, True), (True, True), (False, False)],
)
async def test_parcels_retrieve_orders_catalog_availability(
        taxi_grocery_api,
        experiments3,
        tristero_parcels,
        config_availability,
        catalog_available,
):
    """ catalog_available field should be set depending on
    grocery_oneclick_catalog_availability config"""

    experiments.lavka_parcel_config(experiments3, enabled=True)
    if config_availability is not None:
        experiments.oneclick_catalog_availability(
            experiments3, available=config_availability,
        )

    vendor = 'vendor-000001'
    order_id = '01234567-89ab-cdef-000a-000000000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    depot_id = const.DEPOT_ID

    _prepare_tristero_parcels(
        tristero_parcels, vendor, order_id, ref_order, token, depot_id,
    )

    json = {
        'known_orders': [
            {'vendor': vendor, 'ref_order': ref_order, 'token': token},
        ],
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/retrieve-orders',
        json=json,
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['catalog_available'] == catalog_available


def _prepare_tristero_parcels(
        tristero_parcels,
        vendor: str,
        order_id: str,
        ref_order: str,
        token: str,
        depot_id: str,
        can_left_at_door: bool = True,
        uid: str = '',
        with_delivering_parcel: bool = True,
        timeslot_start: str = None,
        timeslot_end: str = None,
        alternative_timeslots: list = None,
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
        uid=uid,
        timeslot_start=timeslot_start,
        timeslot_end=timeslot_end,
        alternative_timeslots=alternative_timeslots,
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
    if with_delivering_parcel:
        order.add_parcel(
            parcel_id='98765432-10ab-cdef-0000-000001000003:st-pa',
            status='delivering',
            title='\u041f\u043e\u0441\u044b\u043b\u043a\u0430',
            image_url_template='parcels-image_template.jpg',
            quantity_limit='1',
            can_left_at_door=can_left_at_door,
            state_meta={'order_id': '12345678-grocery'},
        )
    return order


def _check_response_order(tristero_order, response_order, legacy_depot_id):
    order_data = tristero_order.data
    assert response_order['order_id'] == order_data['order_id']
    assert response_order['depot_id'] == legacy_depot_id
    assert response_order['customer_address'] == 'какой-то адрес'
    assert (
        response_order['customer_address_uri']
        == order_data['customer_address']
    )
    assert (
        response_order['customer_location'] == order_data['customer_location']
    )
    assert response_order['state'] == order_data['status']
    assert response_order['vendor'] == order_data['vendor']
    assert response_order['token'] == order_data['token']
    assert response_order['ref_order'] == order_data['ref_order']
    assert len(response_order['items']) == len(order_data['parcels'])

    parcels_data = {}
    for parcel in order_data['parcels']:
        parcel_data = {
            'state': parcel['status'],
            'quantity_limit': parcel['quantity_limit'],
        }
        if 'order_id' in parcel['state_meta']:
            parcel_data['grocery_order_id'] = parcel['state_meta']['order_id']
        parcels_data[parcel['parcel_id']] = parcel_data

    for item in response_order['items']:
        assert item['parcel_id'] in parcels_data
        parcel_data = parcels_data[item['parcel_id']]
        assert item['depot_id'] == legacy_depot_id
        assert item['state'] == parcel_data['state']
        assert item['quantity_limit'] == parcel_data['quantity_limit']
        assert ('grocery_order_id' in item) == (
            'grocery_order_id' in parcel_data
        )
        if 'grocery_order_id' in item:
            assert item['grocery_order_id'] == parcel_data['grocery_order_id']
