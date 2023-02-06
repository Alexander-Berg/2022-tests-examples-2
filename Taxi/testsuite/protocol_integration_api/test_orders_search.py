import copy
import json

import pytest

from replica_dbusers_switch_parametrize import (
    PROTOCOL_SWITCH_TO_REPLICA_DBUSERS,
)

TEST_PHONE = '+74951234001'
TEST_PHONE_OID = '5714f45e98956f0600000001'
TEST_PERSONAL_PHONE_ID = 'p11111111111111111111110'

TEST_PHONE_WO_USER = '+74951234004'
TEST_PERSONAL_PHONE_ID_WO_USER = 'p11111111111111111111114'


PERSONAL_DB = {
    '+74951234001': 'p11111111111111111111110',
    '+74951234002': 'p11111111111111111111112',
    '+74951234003': 'p11111111111111111111113',
    '+74951234004': 'p11111111111111111111114',
}


def setup_collection_item(collection, key, value, order_id):
    if value is not None:
        collection.update({'_id': order_id}, {'$set': {key: value}})


def setup_order_proc_current_prices(db, value, order_id, is_cashback, kind):
    # добработать, если кому-то нужно будет использовать,
    # заполняется одно и тоже значение
    # для всех видов цены в виду ненадобности всех полей,
    # кроме user_total_display_price и cashback_price
    setup_collection_item(
        db.order_proc,
        'order.current_prices.user_total_price',
        value,
        order_id,
    )
    setup_collection_item(
        db.order_proc,
        'order.current_prices.user_ride_display_price',
        value,
        order_id,
    )
    setup_collection_item(
        db.order_proc,
        'order.current_prices.user_total_display_price',
        value,
        order_id,
    )
    setup_collection_item(
        db.order_proc, 'order.current_prices.kind', kind, order_id,
    )
    if is_cashback:
        setup_collection_item(
            db.order_proc,
            'order.current_prices.cashback_price',
            100,
            order_id,
        )


@pytest.fixture(scope='function', autouse=True)
def personal_phones_find(mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def mock_personal_phones_find(request):
        request_json = json.loads(request.get_data())
        phone = request_json['value']
        if phone in PERSONAL_DB:
            return {'id': PERSONAL_DB[phone], 'value': phone}
        else:
            return mockserver.make_response(status=404)


RESPONSE_SAMPLE_BASE = {
    'orders': [
        {
            'orderid': '8c83b49edb274ce0992f337000000001',
            'userid': 'user1',
            'created': '2018-01-01T08:29:16+0000',
            'driver': {'name': 'Ivan Ivanov', 'phone': '+78003000600'},
            'legal_entities': [
                {
                    'address': 'Street',
                    'name': 'Главное Такси',
                    'registration_number': 'OGRN: 123',
                    'type': 'park',
                },
                {
                    'address': 'Carrier Address',
                    'name': 'Carrier ltd',
                    'registration_number': 'OGRN: 123456789',
                    'type': 'carrier_permit_owner',
                    'work_hours': 'Hours: 10-22',
                },
            ],
            'platform': 'callcenter',
            'price_calc_type': 'taximeter_permanent',
            'vehicle': {
                'location': [37.7, 55.5],
                'color': 'blue',
                'color_code': '0000FF',
                'model': 'Mercedes-Benz M-Class',
                'plates': 'Х492НК77',
                'short_car_number': '492',
            },
            'park': {
                'id': '999012',
                'name': 'Главное Такси',
                'phone': '+79321259615',
            },
            'request': {
                'requirements': {
                    'nosmoking': True,
                    'creditcard': False,
                    'corp': True,
                },
                'due': '2018-01-01T08:33:29+0000',
                'comment': 'wait-1000',
                'class': 'econom',
                'route': [
                    {
                        'country': 'Россия',
                        'fullname': 'Россия, Москва, улица Охотный Ряд',
                        'geopoint': [37.61672446877377, 55.757743019358564],
                        'eta': None,
                        'porchnumber': 'подъезд 6',
                        'short_text': 'улица Охотный Ряд',
                        'type': '\x01',
                    },
                    {
                        'country': 'Россия',
                        'fullname': (
                            'Россия, Центральный федеральный '
                            'округ, Москва, Внуково пос., ул. 1-я '
                            'Рейсовая, 12, корп.2, '
                            'Аэропорт Внуково'
                        ),
                        'geopoint': [37.287938, 55.60556],
                        'eta': None,
                        'porchnumber': 'подъезд 7',
                        'short_text': 'Аэропорт Внуково',
                        'type': '\x02',
                    },
                ],
            },
            'status': 'waiting',
            'cost_message_details': {
                'price_raw': 555,
                'cost_breakdown': [
                    {'display_amount': '555 руб.', 'display_name': 'cost'},
                    {
                        'display_amount': '653 руб.',
                        'display_name': 'cost_without_discount',
                    },
                    {'display_amount': '15%', 'display_name': 'discount'},
                ],
            },
            'cancel_disabled': False,
            'payment_changes': [],
            'currency_rules': {
                'code': 'RUB',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
                'cost_precision': 0,
            },
            'nearest_zone': 'moscow',
        },
    ],
}


RESPONSE_ORDER_SAMPLE_MANY = {
    'orders': [
        {
            'platform': 'callcenter',
            'price_calc_type': 'taximeter_permanent',
            'orderid': '8c83b49edb274ce0992f337000000002',
            'userid': 'user1',
            'created': '2018-01-01T08:29:16+0000',
            'time_left': '16 мин',
            'time_left_raw': 960.0,
            'driver': {'name': 'Ivan Ivanov', 'phone': '+78003000600'},
            'legal_entities': [
                {
                    'address': 'Street',
                    'name': 'Главное Такси',
                    'registration_number': 'OGRN: 123',
                    'type': 'park',
                },
            ],
            'vehicle': {
                'location': [37.6, 55.7],
                'color': 'blue',
                'color_code': '0000FF',
                'model': 'Mercedes-Benz M-Class',
                'plates': 'Х492НК77',
                'short_car_number': '492',
            },
            'park': {
                'id': '999012',
                'name': 'Главное Такси',
                'phone': '+79321259615',
            },
            'request': {
                'requirements': {},
                'comment': '',
                'class': 'econom',
                'route': [
                    {
                        'country': 'Россия',
                        'fullname': 'Россия, Москва, улица Охотный Ряд',
                        'geopoint': [37.61672446877377, 55.757743019358564],
                        'eta': 16,
                        'short_text': 'улица Охотный Ряд',
                        'type': '\x01',
                    },
                ],
            },
            'status': 'driving',
            'cost_message_details': {'cost_breakdown': []},
            'cancel_disabled': False,
            'payment_changes': [],
            'currency_rules': {
                'code': 'RUB',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
                'cost_precision': 0,
            },
            'nearest_zone': 'moscow',
        },
        {
            'platform': 'callcenter',
            'price_calc_type': 'taximeter_permanent',
            'orderid': '8c83b49edb274ce0992f337000000001',
            'userid': 'user1',
            'created': '2018-01-01T08:29:16+0000',
            'driver': {'name': 'Ivan Ivanov', 'phone': '+78003000600'},
            'legal_entities': [
                {
                    'address': 'Street',
                    'name': 'Главное Такси',
                    'registration_number': 'OGRN: 123',
                    'type': 'park',
                },
            ],
            'vehicle': {
                'location': [37.6, 55.7],
                'color': 'blue',
                'color_code': '0000FF',
                'model': 'Mercedes-Benz M-Class',
                'plates': 'Х492НК77',
                'short_car_number': '492',
            },
            'park': {
                'id': '999012',
                'name': 'Главное Такси',
                'phone': '+79321259615',
            },
            'request': {
                'requirements': {
                    'nosmoking': True,
                    'creditcard': False,
                    'corp': True,
                },
                'due': '2018-01-01T08:33:29+0000',
                'comment': 'wait-1000',
                'class': 'econom',
                'route': [
                    {
                        'country': 'Россия',
                        'fullname': 'Россия, Москва, улица Охотный Ряд',
                        'geopoint': [37.61672446877377, 55.757743019358564],
                        'eta': None,
                        'porchnumber': 'подъезд 6',
                        'short_text': 'улица Охотный Ряд',
                        'type': '\x01',
                    },
                    {
                        'city': 'Москва',
                        'country': 'Россия',
                        'fullname': (
                            'Россия, Центральный федеральный '
                            'округ, Москва, Внуково пос., ул. 1-я '
                            'Рейсовая, 12, корп.2, '
                            'Аэропорт Внуково'
                        ),
                        'geopoint': [37.287938, 55.60556],
                        'eta': None,
                        'porchnumber': 'подъезд 7',
                        'short_text': 'Аэропорт Внуково',
                        'type': '\x02',
                    },
                ],
            },
            'status': 'waiting',
            'cost_message_details': {
                'price_raw': 555,
                'cost_breakdown': [
                    {'display_amount': '555 руб.', 'display_name': 'cost'},
                    {
                        'display_amount': '653 руб.',
                        'display_name': 'cost_without_discount',
                    },
                    {'display_amount': '15%', 'display_name': 'discount'},
                ],
            },
            'cancel_disabled': False,
            'payment_changes': [],
            'currency_rules': {
                'code': 'RUB',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
                'cost_precision': 0,
            },
            'nearest_zone': 'moscow',
        },
    ],
}


RESPONSE_SAMPLE_EMPTY: dict = {'orders': []}


def _to_time(dist):
    return dist * (3600.0 / 1000) / 25.0


@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_simple(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    data['orders'][0].pop('cancel_rules')
    assert data == RESPONSE_SAMPLE_BASE


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.config(USE_DRIVER_TRACKSTORY_PERCENT=100)
def test_simple_driver_trackstory(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.5,
                'lon': 37.7,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {
            'user': {'phone': TEST_PHONE, 'user_id': 'user1'},
            'chainid': 'chainid_1',
        },
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200
    data = response.json()
    data['orders'][0].pop('cancel_rules')
    assert data == RESPONSE_SAMPLE_BASE


@pytest.mark.parametrize(
    ('config_values', 'length', 'expected_response'),
    (
        (
            {
                'INTEGRATION_ORDERS_SEARCH_RESULT_SIZE': 2,
                'INTEGRATION_ORDERS_SEARCH_INTERVAL': 0,
                'INTEGRATION_ORDERS_SEARCH_ACTIVE_FIRST_ENABLED': False,
            },
            2,
            'response/draft_first.json',
        ),
        (
            {
                'INTEGRATION_ORDERS_SEARCH_RESULT_SIZE': 3,
                'INTEGRATION_ORDERS_SEARCH_INTERVAL': 1100,
                'INTEGRATION_ORDERS_SEARCH_ACTIVE_FIRST_ENABLED': True,
            },
            2,
            'response/active_first_all.json',
        ),
        (
            {
                'INTEGRATION_ORDERS_SEARCH_RESULT_SIZE': 3,
                'INTEGRATION_ORDERS_SEARCH_INTERVAL': 2,
                'INTEGRATION_ORDERS_SEARCH_ACTIVE_FIRST_ENABLED': True,
            },
            1,
            'response/active_first.json',
        ),
    ),
)
@pytest.mark.filldb(order_proc='draft')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_draft(
        taxi_integration,
        db,
        mockserver,
        config,
        load_json,
        config_values,
        length,
        expected_response,
        recalc_order,
):
    """
    have:
    draft40 - 40 seconds before
    active90 - 90 seconds before
    active1000 - 1000 seconds before
    """

    config.set_values(config_values)

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    request = {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}}

    response = taxi_integration.post(
        'v1/orders/search',
        request,
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['orders']) == length
    expected_data = load_json(expected_response)
    assert data == expected_data


@pytest.mark.parametrize(
    ('car_number', 'short_car_number'),
    (
        ('X', None),
        ('X492НК77', '492'),
        ('X4923252НКgg5277', '49-23-25-2-52'),
        ('77', '77'),
    ),
)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_short_car_number(
        db,
        taxi_integration,
        mockserver,
        car_number,
        short_car_number,
        recalc_order,
):

    order_id = '8c83b49edb274ce0992f337000000001'
    db.order_proc.update(
        {'_id': order_id}, {'$set': {'candidates.0.car_number': car_number}},
    )

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200
    data = response.json()
    vehicle = data['orders'][0]['vehicle']
    assert vehicle['plates'] == car_number
    assert vehicle.get('short_car_number') == short_car_number


@pytest.mark.parametrize(
    ('input', 'status_code', 'correct_response'),
    (
        # Ok sample
        (
            {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
            200,
            RESPONSE_SAMPLE_BASE,
        ),
        # No input
        (
            None,
            400,
            {'error': {'text': 'Cant parse request: failed to parse json'}},
        ),
        # Bad user
        (
            {},
            400,
            {'error': {'text': 'Neither "user" nor "order_id" provided'}},
        ),
        (
            {'user': f'phone: {TEST_PHONE}'},
            400,
            {'error': {'text': 'Cant parse request: invalid user'}},
        ),
        (
            {'user': 42},
            400,
            {'error': {'text': 'Cant parse request: invalid user'}},
        ),
        (
            {'user': None},
            400,
            {'error': {'text': 'Cant parse request: invalid user'}},
        ),
        (
            {'user': {}},
            400,
            {
                'error': {
                    'text': (
                        'either personal_phone_id or phone should be passed'
                    ),
                },
            },
        ),
        # Bad phone
        (
            {'user': {'phone': 42}},
            400,
            {'error': {'text': 'Cant parse request: invalid phone'}},
        ),
        (
            {'user': {'phone': None}},
            400,
            {
                'error': {
                    'text': (
                        'either personal_phone_id or phone should be passed'
                    ),
                },
            },
        ),
        # Bad sourceid
        (
            {'user': {'phone': TEST_PHONE}, 'sourceid': 42},
            400,
            {'error': {'text': 'Cant parse request: invalid sourceid'}},
        ),
        # Bad orderid
        ({'orderid': ''}, 400, {'error': {'text': 'empty order_id provided'}}),
        (
            {'orderid': 42},
            400,
            {'error': {'text': 'Cant parse request: invalid orderid'}},
        ),
        (
            {'orderid': None},
            400,
            {
                'error': {
                    'text': 'Neither user_id nor order_id provided for search',
                },
            },
        ),
        (
            {'orderid': {}},
            400,
            {'error': {'text': 'Cant parse request: invalid orderid'}},
        ),
        # Phone format canonize
        (
            {'user': {'phone': '8(495)-123-40-01', 'user_id': 'user1'}},
            200,
            RESPONSE_SAMPLE_BASE,
        ),
        (
            {'user': {'phone': TEST_PHONE}},
            400,
            {
                'error': {
                    'text': 'Neither user_id nor order_id provided for search',
                },
            },
        ),
        # Unauthorized user
        (
            {'user': {'phone': TEST_PHONE_WO_USER, 'user_id': 'user1'}},
            400,
            {
                'error': {
                    'text': (
                        'user personal_phone_id doesn\'t match request '
                        'personal_phone_id'
                    ),
                },
            },
        ),
        # Alice OK
        (
            {
                'user': {
                    'phone': TEST_PHONE,
                    'user_id': 'user1',
                    'yandex_uid': '4003514353',
                },
                'sourceid': 'alice',
            },
            200,
            RESPONSE_SAMPLE_BASE,
        ),
        # Alice invalid yandex_uid
        (
            {
                'user': {
                    'phone': TEST_PHONE,
                    'user_id': 'user1',
                    'yandex_uid': '44444444444',
                },
                'sourceid': 'alice',
            },
            400,
            {
                'error': {
                    'text': (
                        'user yandex_uid doesn\'t match request yandex_uid'
                    ),
                },
            },
        ),
        # Alice no yandex_uid
        (
            {
                'user': {'phone': TEST_PHONE, 'user_id': 'user1'},
                'sourceid': 'alice',
            },
            400,
            {
                'error': {
                    'text': (
                        'for Alice should contain non empty \'yandex_uid\''
                    ),
                },
            },
        ),
    ),
)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_input_errors(
        db,
        taxi_integration,
        mockserver,
        input,
        status_code,
        correct_response,
        recalc_order,
):
    def prepare_data(input):
        if input and input.get('user') and type(input['user']) is dict:
            user_id = input['user'].get('user_id')
            sourceid = input.get('sourceid')
            if user_id and sourceid == 'alice':
                db.users.update(
                    {'_id': user_id}, {'$set': {'sourceid': sourceid}},
                )

    def prepare_headers(input, headers):
        if input and not input.get('sourceid'):
            headers['User-Agent'] = 'call_center'

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    prepare_data(input)

    headers = {'Accept-Language': 'ru'}
    prepare_headers(input, headers)

    response = taxi_integration.post(
        'v1/orders/search', input, headers=headers,
    )
    assert response.status_code == status_code
    data = response.json()

    if response.status_code == 200:
        data['orders'][0].pop('cancel_rules')

    assert data == correct_response


@pytest.mark.filldb(order_proc='no_phone_id')
def test_search_by_phone_id(taxi_integration):
    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    data = response.json()

    assert response.status_code == 200
    assert data == RESPONSE_SAMPLE_EMPTY


@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['good_but_not_enough'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {
                'match': 'good_but_not_enough',
                '@app_name': 'good_but_not_enough',
                '@app_ver1': '2',
            },
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
@pytest.mark.parametrize(
    'user_agent, code, error_text',
    [
        (
            'good_but_not_enough',
            400,
            'user sourceid doesn\'t match request source_id',
        ),
        ('siri', 400, 'Invalid application'),
    ],
    ids=['valid_app', 'invalid_app'],
)
def test_application(taxi_integration, user_agent, code, error_text):
    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': user_agent},
    )

    assert response.status_code == code, response.json()

    data = response.json()
    if code == 200:
        assert data == RESPONSE_SAMPLE_BASE
    else:
        assert data['error']['text'] == error_text


@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_unknown_phone(taxi_integration):
    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': '+74951234560', 'user_id': 'user2'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 404


@pytest.mark.filldb(users='empty')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_unknown_user(taxi_integration, mockserver):
    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user2'}},
        headers={'User-Agent': 'call_center'},
    )
    assert response.status_code == 404


@pytest.mark.filldb(order_proc='empty')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_no_orders(taxi_integration, mockserver):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200
    assert response.json() == RESPONSE_SAMPLE_EMPTY


@pytest.mark.filldb(order_proc='many')
@pytest.mark.config(INTEGRATION_ORDERS_SEARCH_RESULT_SIZE=2)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_many_orders(taxi_integration, mockserver, recalc_order):
    """
    More then one order, sorted by created time, newer on the top
    """

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.7,
            'lon': 37.6,
            'speed': 30,
            'timestamp': 1502366306,
        }

    @mockserver.handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        return {
            'duration': 299,
            'smooth_duration': 16 * 60,
            'distance': 100,
            'driver_position': [37.51, 55.61],
            'path': [[37.511, 55.611], [37.514, 55.614]],
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    orders = response.json()['orders']
    sample_orders = copy.deepcopy(RESPONSE_ORDER_SAMPLE_MANY)
    expected_orders = sample_orders['orders']
    assert len(orders) == len(expected_orders)
    for expected_order, order in zip(expected_orders, orders):
        order.pop('cancel_rules')
        assert expected_order == order


@pytest.mark.config(INTEGRATION_ORDERS_SEARCH_USE_DRW=100)
@pytest.mark.filldb(order_proc='many')
@pytest.mark.config(INTEGRATION_ORDERS_SEARCH_RESULT_SIZE=2)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_orders_by_driver_route_responder(
        taxi_integration, mockserver, recalc_order,
):
    """
    Use driver-route-responder instead of tracker/smooth-routing
    """

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.7,
            'lon': 37.6,
            'speed': 30,
            'timestamp': 1502366306,
        }

    @mockserver.handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        # should not be called
        assert False

    @mockserver.json_handler('/driver_route_responder/timeleft')
    def mock_drw_timeleft(request):
        return {
            'time_left': 16 * 60,
            'distance_left': 100,
            'position': [37.51, 55.61],
            'destination': [37.514, 55.614],
            'tracking_type': 'route_tracking',
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    orders = response.json()['orders']
    sample_orders = copy.deepcopy(RESPONSE_ORDER_SAMPLE_MANY)
    expected_orders = sample_orders['orders']
    assert len(orders) == len(expected_orders)
    for expected_order, order in zip(expected_orders, orders):
        order.pop('cancel_rules')
        assert expected_order == order
    assert mock_drw_timeleft.times_called > 0


@pytest.mark.config(INTEGRATION_ORDERS_SEARCH_USE_DRW=100)
@pytest.mark.filldb(order_proc='many_drw_fallback')
@pytest.mark.config(INTEGRATION_ORDERS_SEARCH_RESULT_SIZE=2)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_orders_by_driver_route_responder_fallback(
        taxi_integration, mockserver,
):
    """
    Test eta by driver-route-responder, but driver-route-responder
    returns 500, so use fallback eta
    """

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.7,
            'lon': 37.6,
            'speed': 30,
            'timestamp': 1502366306,
        }

    @mockserver.handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        # should not be called
        assert False

    @mockserver.json_handler('/driver_route_responder/timeleft')
    def mock_drw_timeleft(request):
        # route-watcher is broken
        return mockserver.make_response('', 500)

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    orders = response.json()['orders']
    assert len(orders) == 1
    order = orders[0]
    assert order['time_left'] == '3 мин'
    assert order['time_left_raw'] == 169
    assert mock_drw_timeleft.times_called > 0


@pytest.mark.translations(color={'0000FF': {'ru': 'цвет'}})
@pytest.mark.parametrize(
    ('user_phone', 'user_id', 'expected_code', 'expected_response'),
    (
        (
            '+74951234001',
            'user1',
            200,
            {
                'orders': [
                    {
                        'price_calc_type': 'taximeter_permanent',
                        'orderid': (
                            'transporting_turboapp_cancel_disabled_false'
                        ),
                        'userid': 'user1',
                        'created': '2018-01-01T08:29:16+0000',
                        'time_left': '0 мин',
                        'time_left_raw': 0.0,
                        'driver': {
                            'name': 'driver_1_candidate_name',
                            'phone': 'driver_1_candidate_phone',
                        },
                        'legal_entities': [
                            {'name': 'Такси пользователя 2', 'type': 'park'},
                        ],
                        'vehicle': {
                            'location': [37.28001, 55.60001],
                            'color': 'цвет',
                            'color_code': '0000FF',
                            'model': 'Mercedes-Benz M-Class',
                            'plates': 'Х492НК77',
                            'short_car_number': '492',
                        },
                        'park': {
                            'id': 'driver_park',
                            'name': 'Такси пользователя 2',
                            'phone': '+79321259002',
                        },
                        'request': {
                            'requirements': {},
                            'comment': 'comment1',
                            'class': 'econom',
                            'route': [
                                {
                                    'city': 'Москва',
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Москва, улица Охотный Ряд'
                                    ),
                                    'geopoint': [
                                        37.61672446877377,
                                        55.757743019358564,
                                    ],
                                    'eta': 0,
                                    'short_text': 'улица Охотный Ряд',
                                    'type': '\x01',
                                },
                            ],
                        },
                        'status': 'transporting',
                        'cost_message_details': {'cost_breakdown': []},
                        'cancel_disabled': False,
                        'payment_changes': [],
                        'currency_rules': {
                            'code': 'RUB',
                            'template': '$VALUE$ $SIGN$$CURRENCY$',
                            'text': 'руб.',
                            'cost_precision': 0,
                        },
                        'nearest_zone': 'moscow',
                    },
                ],
            },
        ),
        (
            '+74951234002',
            'user2',
            200,
            {
                'orders': [
                    {
                        'platform': 'callcenter',
                        'price_calc_type': 'taximeter_permanent',
                        'orderid': 'transporting_cancel_disabled_true',
                        'userid': 'user2',
                        'created': '2018-01-01T08:29:16+0000',
                        'time_left': '4 мин',
                        'time_left_raw': 228.0,
                        'driver': {
                            'name': 'driver_2_candidate_name',
                            'phone': 'driver_2_candidate_phone',
                        },
                        'legal_entities': [
                            {'name': 'Такси пользователя 2', 'type': 'park'},
                        ],
                        'vehicle': {
                            'location': [37.28001, 55.60001],
                            'color': 'цвет',
                            'color_code': '0000FF',
                            'model': 'Mercedes-Benz M-Class',
                            'plates': 'РАН',
                        },
                        'park': {
                            'id': 'driver_park',
                            'name': 'Такси пользователя 2',
                            'phone': '+79321259002',
                        },
                        'request': {
                            'requirements': {},
                            'comment': 'comment2',
                            'class': 'econom',
                            'route': [
                                {
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Москва, улица Охотный Ряд'
                                    ),
                                    'geopoint': [
                                        37.61672446877377,
                                        55.757743019358564,
                                    ],
                                    'eta': None,
                                    'short_text': 'улица Охотный Ряд',
                                    'type': '\x01',
                                },
                                {
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Центральный федеральный '
                                        'округ, Москва, Внуково пос., '
                                        'ул. 1-я Рейсовая, '
                                        '12, корп.2, Аэропорт Внуково'
                                    ),
                                    'geopoint': [37.287938, 55.60556],
                                    'eta': None,
                                    'short_text': 'Аэропорт Внуково',
                                    'type': '\x02',
                                    'passed': True,
                                },
                                {
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Центральный федеральный '
                                        'округ, Москва, Внуково пос., '
                                        'ул. 1-я Рейсовая, '
                                        '12, корп.2, Аэропорт Внуково 2'
                                    ),
                                    'geopoint': [37.28002, 55.60002],
                                    'eta': 4,
                                    'short_text': 'Аэропорт Внуково',
                                    'type': '\x02',
                                    'passed': False,
                                },
                            ],
                        },
                        'status': 'transporting',
                        'cost_message_details': {'cost_breakdown': []},
                        'cancel_disabled': True,
                        'payment_changes': [],
                        'currency_rules': {
                            'code': 'RUB',
                            'template': '$VALUE$ $SIGN$$CURRENCY$',
                            'text': 'руб.',
                            'cost_precision': 0,
                        },
                        'nearest_zone': 'moscow',
                    },
                ],
            },
        ),
        (
            '+74951234003',
            'user3',
            200,
            {
                'orders': [
                    {
                        'platform': 'callcenter',
                        'price_calc_type': 'taximeter_permanent',
                        'orderid': 'finished_order',
                        'userid': 'user3',
                        'created': '2018-01-01T08:29:16+0000',
                        'distance': '3 км',
                        'driver': {
                            'name': 'driver_2_candidate_name',
                            'phone': 'driver_2_candidate_phone',
                        },
                        'legal_entities': [
                            {'name': 'Такси пользователя 2', 'type': 'park'},
                        ],
                        'vehicle': {
                            'color': 'цвет',
                            'color_code': '0000FF',
                            'model': 'Mercedes-Benz M-Class',
                            'plates': 'РАН',
                        },
                        'park': {
                            'id': 'driver_park',
                            'name': 'Такси пользователя 2',
                            'phone': '+79321259002',
                        },
                        'request': {
                            'requirements': {},
                            'comment': 'comment2',
                            'class': 'econom',
                            'route': [
                                {
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Москва, улица Охотный Ряд'
                                    ),
                                    'geopoint': [
                                        37.61672446877377,
                                        55.757743019358564,
                                    ],
                                    'eta': None,
                                    'short_text': 'улица Охотный Ряд',
                                    'type': '\x01',
                                },
                                {
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Центральный федеральный '
                                        'округ, Москва, Внуково пос., '
                                        'ул. 1-я Рейсовая, '
                                        '12, корп.2, Аэропорт Внуково 2'
                                    ),
                                    'geopoint': [37.28002, 55.60002],
                                    'eta': None,
                                    'short_text': 'Аэропорт Внуково',
                                    'type': '\x02',
                                },
                            ],
                        },
                        'status': 'complete',
                        'cost_message_details': {'cost_breakdown': []},
                        'cancel_disabled': True,
                        'payment_changes': [],
                        'currency_rules': {
                            'code': 'RUB',
                            'template': '$VALUE$ $SIGN$$CURRENCY$',
                            'text': 'руб.',
                            'cost_precision': 0,
                        },
                        'nearest_zone': 'moscow',
                    },
                ],
            },
        ),
    ),
)
@pytest.mark.filldb(order_proc='statuses')
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.config(
    INTEGRATION_ORDERS_SEARCH_RESULT_SIZE=2,
    CALLCENTER_ORDER_TIME_TO_CANCEL=600,
    APPLICATION_MAP_BRAND={
        '__default__': 'yataxi',
        'callcenter': 'yataxi',
        'web_turboapp_taxi': 'turboapp',
    },
    APPLICATION_BRAND_RELATED_BRANDS={'yataxi': ['turboapp']},
)
def test_search_statuses(
        taxi_integration,
        user_phone,
        user_id,
        expected_code,
        expected_response,
        mockserver,
        recalc_order,
):
    """
    Search order in transporting status
    """

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.60001,
            'lon': 37.28001,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': user_phone, 'user_id': user_id}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == expected_code
    if expected_code != 200:
        return

    data = response.json()
    if 'cancel_rules' in data['orders'][0]:
        data['orders'][0].pop('cancel_rules')
    assert data == expected_response


@pytest.mark.parametrize(
    ('user_phone', 'user_id', 'expected_code', 'expected_response'),
    (
        (
            TEST_PHONE,
            'user1',
            200,
            {
                'orders': [
                    {
                        'orderid': 'cancelled_order',
                        'userid': 'user1',
                        'created': '2018-01-01T08:29:16+0000',
                        'platform': 'callcenter',
                        'price_calc_type': 'taximeter_permanent',
                        'request': {
                            'requirements': {},
                            'comment': 'comment2',
                            'class': 'econom',
                            'route': [
                                {
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Москва, улица Охотный Ряд'
                                    ),
                                    'geopoint': [
                                        37.61672446877377,
                                        55.757743019358564,
                                    ],
                                    'eta': None,
                                    'short_text': 'улица Охотный Ряд',
                                    'type': '\x01',
                                },
                                {
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Центральный федеральный '
                                        'округ, Москва, Внуково пос., '
                                        'ул. 1-я Рейсовая, '
                                        '12, корп.2, Аэропорт Внуково 2'
                                    ),
                                    'geopoint': [37.28002, 55.60002],
                                    'eta': None,
                                    'short_text': 'Аэропорт Внуково',
                                    'type': '\x02',
                                },
                            ],
                        },
                        'status': 'cancelled',
                        'cost_message_details': {
                            'cost_breakdown': [
                                {
                                    'display_amount': '15%',
                                    'display_name': 'discount',
                                },
                            ],
                        },
                        'cancel_disabled': True,
                        'payment_changes': [],
                        'currency_rules': {
                            'code': 'RUB',
                            'template': '$VALUE$ $SIGN$$CURRENCY$',
                            'text': 'руб.',
                            'cost_precision': 0,
                        },
                        'nearest_zone': 'moscow',
                    },
                ],
            },
        ),
        (
            '+74951234002',
            'user2',
            200,
            {
                'orders': [
                    {
                        'orderid': 'search_order',
                        'userid': 'user2',
                        'platform': 'callcenter',
                        'price_calc_type': 'taximeter_permanent',
                        'created': '2018-01-01T08:29:16+0000',
                        'request': {
                            'requirements': {},
                            'comment': 'comment2',
                            'class': 'econom',
                            'route': [
                                {
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Москва, улица Охотный Ряд'
                                    ),
                                    'geopoint': [
                                        37.61672446877377,
                                        55.757743019358564,
                                    ],
                                    'eta': None,
                                    'short_text': 'улица Охотный Ряд',
                                    'type': '\x01',
                                },
                                {
                                    'country': 'Россия',
                                    'fullname': (
                                        'Россия, Центральный федеральный '
                                        'округ, Москва, Внуково пос., '
                                        'ул. 1-я Рейсовая, '
                                        '12, корп.2, Аэропорт Внуково 2'
                                    ),
                                    'geopoint': [37.28002, 55.60002],
                                    'eta': None,
                                    'short_text': 'Аэропорт Внуково',
                                    'type': '\x02',
                                },
                            ],
                        },
                        'status': 'search',
                        'cost_message_details': {
                            'cost_breakdown': [
                                {
                                    'display_amount': '15%',
                                    'display_name': 'discount',
                                },
                            ],
                        },
                        'cancel_disabled': False,
                        'payment_changes': [],
                        'currency_rules': {
                            'code': 'RUB',
                            'template': '$VALUE$ $SIGN$$CURRENCY$',
                            'text': 'руб.',
                            'cost_precision': 0,
                        },
                        'nearest_zone': 'moscow',
                    },
                ],
            },
        ),
    ),
)
@pytest.mark.filldb(order_proc='without_performer')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_search_status_without_performer(
        taxi_integration,
        user_phone,
        user_id,
        expected_code,
        expected_response,
        mockserver,
        tracker,
        recalc_order,
):
    """
    Search order without performer
    """

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.60001,
            'lon': 37.28001,
            'speed': 30,
            'timestamp': 1502366306,
        }

    @mockserver.handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response('', 500)

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': user_phone, 'user_id': user_id}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == expected_code
    if expected_code != 200:
        return

    data = response.json()
    if 'cancel_rules' in data['orders'][0]:
        data['orders'][0].pop('cancel_rules')
    assert data == expected_response


@pytest.mark.filldb(order_proc='trips_get_details_for_chain_test')
@pytest.mark.parametrize(
    'enable_cp, cp_status, expected_eta_pickup',
    [
        (True, 'assigned', 426),
        (True, 'finished', 301),
        (True, 'cancelled', 301),
        (False, 'assigned', 301),
    ],
)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_chain_parent(
        taxi_integration,
        db,
        mockserver,
        tracker,
        enable_cp,
        cp_status,
        expected_eta_pickup,
):
    """
    This test repeat logic from test_trips_get_details.py :: test_base,
    beacause code is based on test_chain_parent logic
    """

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.787786,
            'lon': 37.600684,
            'speed': 25.0,
            'timestamp': 1502366306,
        }

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        return {
            'duration': 76,
            'smooth_duration': 77,
            'distance': 100,
            'driver_position': [37.51, 55.61],
            'path': [[37.511, 55.611], [37.514, 55.614]],
        }

    if enable_cp:
        db.order_proc.update(
            {'_id': 'driving_order'},
            {
                '$set': {
                    'candidates.0.cp': {
                        'dest': [37.600180, 55.789364],
                        'id': 'chain_%s' % cp_status,
                    },
                },
            },
        )
    else:
        db.order_proc.update(
            {'_id': 'driving_order'}, {'$unset': {'candidates.0.cp': True}},
        )

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data['orders']) == 1
    order = data['orders'][0]
    assert order['status'] == 'driving'
    route = order['request']['route']
    assert len(route) == 2
    pickup = route[0]
    destination = route[1]

    expected_eta_pickup = round(expected_eta_pickup / 60.0)
    assert abs(pickup['eta'] - _to_time(expected_eta_pickup)) < 2
    assert destination['eta'] is None


@pytest.mark.config(
    TRACKER_ADJUST_EXPERIMENTS_PARAMETRS={
        'adjust_additional_options_1': {
            'part_count': 1,
            'part_distance': 1,
            'part_time': 1,
        },
    },
)
@pytest.mark.driver_experiments('adjust_additional_options_1')
def test_experiment_position_request(
        taxi_integration, mockserver, recalc_order,
):
    testcase = {'called': 0}

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        testcase['called'] += 1
        testcase['query_string'] = request.query_string
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )

    assert testcase['called'] == 1

    query = dict(
        map(
            lambda x: x.split('='),
            testcase['query_string'].decode().split('&'),
        ),
    )

    assert query == {'id': '999012_a5709ce56c2740d9a536650f5390de0b'}

    assert response.status_code == 200


@pytest.mark.config(CALLCENTER_ORDER_TIME_TO_CANCEL=300)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_cancel_rules(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.7577,
            'lon': 37.6167,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200
    order = response.json()['orders'][0]
    assert 'cancel_rules' in order
    cancel_rules = order['cancel_rules']
    assert cancel_rules['state'] == 'free'
    assert 'title' in cancel_rules
    assert 'message' in cancel_rules
    assert 'message_support' in cancel_rules


def test_phone_mismatch(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    # phone number and user_id belongs to different users
    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': '+74951234002', 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 400


@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_corp_cabinet(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'user_id': 'user1'}, 'sourceid': 'corp_cabinet'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    data['orders'][0].pop('cancel_rules')
    assert data == RESPONSE_SAMPLE_BASE


@pytest.mark.config(CALLCENTER_ORDER_TIME_TO_CANCEL=300)
@pytest.mark.parametrize(
    'phone, user_id, ' 'expected_payment, expected_cancel_state',
    [
        (
            TEST_PHONE,
            'user1',
            {'type': 'corp', 'payment_method_id': 'corp-1234'},
            'paid',
        ),
        ('+74951234002', 'user2', {'type': 'cash'}, 'free'),
        ('+74951234003', 'user3', {'type': 'cash'}, 'free'),
    ],
)
@pytest.mark.filldb(order_proc='payment')
@pytest.mark.filldb(orders='payment')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_payment(
        taxi_integration,
        mockserver,
        phone,
        user_id,
        expected_payment,
        expected_cancel_state,
        recalc_order,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.757743019358564,
            'lon': 37.61672446877377,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': phone, 'user_id': user_id}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['orders'][0]['payment'] == expected_payment
    assert data['orders'][0]['cancel_rules']['state'] == expected_cancel_state


@pytest.mark.filldb(order_proc='with_order_source')
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'orderid,success',
    [
        ('8c83b49edb274ce0992f337000000001', True),
        ('8c83b49edb274ce0992f337000000003', False),
    ],
)
def test_search_by_orderid(
        orderid, success, taxi_integration, mockserver, recalc_order,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'orderid': orderid, 'sourceid': 'corp_cabinet'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    if success:
        data['orders'][0].pop('cancel_rules')
        assert data == RESPONSE_SAMPLE_BASE
    else:
        assert data == RESPONSE_SAMPLE_EMPTY


@pytest.mark.filldb(order_proc='linked_by_yandex_uid')
@pytest.mark.filldb(users='linked_by_yandex_uid')
@pytest.mark.config(INTEGRATION_ORDERS_SEARCH_RESULT_SIZE=2)
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'crossdevice_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(CROSSDEVICE_ENABLED=True),
            id='Crossdevice on',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(CROSSDEVICE_ENABLED=False),
            id='Crossdevice off',
        ),
    ],
)
@pytest.mark.parametrize(
    'search_orders_by_uid',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='int_api_search_orders_by_uid',
                    consumers=['protocol/user-api-switch'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {'enabled': True},
                        },
                    ],
                ),
            ],
        ),
    ],
)
@PROTOCOL_SWITCH_TO_REPLICA_DBUSERS
def test_search_by_linked_user_ids(
        taxi_integration,
        mockserver,
        crossdevice_enabled,
        search_orders_by_uid,
        testpoint,
        read_from_replica_dbusers,
        recalc_order,
):
    """
    More then one order, sorted by created time, newer on the top
    """

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.7,
            'lon': 37.6,
            'speed': 30,
            'timestamp': 1502366306,
        }

    @mockserver.handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        return {
            'duration': 299,
            'smooth_duration': 16 * 60,
            'distance': 100,
            'driver_position': [37.51, 55.61],
            'path': [[37.511, 55.611], [37.514, 55.614]],
        }

    @testpoint('ordersearch::query_hint')
    def order_search_query_hint(hint):
        if crossdevice_enabled and search_orders_by_uid:
            assert hint == {'order.user_uid': 1}
        else:
            assert hint == {'order.user_id': 1, 'status': 1}

    @testpoint('orderkit::GetUserById')
    def replica_dbusers_test_point(data):
        assert read_from_replica_dbusers == data['replica']

    def get_expected_orders():
        sample_orders = copy.deepcopy(RESPONSE_ORDER_SAMPLE_MANY)
        expected_orders = sample_orders['orders']
        expected_orders[1]['userid'] = 'user2'
        if crossdevice_enabled:
            if search_orders_by_uid:
                expected_orders[0][
                    'orderid'
                ] = '8c83b49edb274ce0992f337000000004'
                expected_orders[0]['userid'] = 'user3'
            return expected_orders
        return expected_orders[:1]

    response = taxi_integration.post(
        'v1/orders/search',
        {
            'user': {'phone': TEST_PHONE, 'user_id': 'user1'},
            'sourceid': 'turboapp',
        },
        headers={'Accept-Language': 'ru', 'User-Agent': 'Yabro turboapp'},
    )

    assert response.status_code == 200, response.text

    orders = response.json()['orders']
    expected_orders = get_expected_orders()

    assert len(orders) == len(expected_orders)
    for expected_order, order in zip(expected_orders, orders):
        order.pop('cancel_rules')
        assert expected_order == order
    assert order_search_query_hint.times_called == 1
    assert replica_dbusers_test_point.times_called == 1


@pytest.mark.filldb(order_proc='with_order_source')
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'forwarding_enabled, empty_phone',
    [(True, False), (True, True), (False, False)],
)
def test_search_has_forwarding(
        taxi_integration,
        mockserver,
        db,
        forwarding_enabled,
        empty_phone,
        recalc_order,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    origin_phone = '+78003000600'
    orderid = '8c83b49edb274ce0992f337000000001'
    if empty_phone:
        phone, ext = '', ''
    else:
        phone, ext = '+79636698958', '1513'

    expected_phone = (
        f'{phone},,{ext}'
        if forwarding_enabled and not empty_phone
        else origin_phone
    )

    if forwarding_enabled:
        forwarding_struct = {'phone': phone, 'ext': ext}

        db.order_proc.update(
            {'_id': orderid, 'candidates.0': {'$exists': True}},
            {'$set': {'candidates.0.forwarding': forwarding_struct}},
        )

    response = taxi_integration.post(
        'v1/orders/search',
        {'orderid': orderid, 'sourceid': 'corp_cabinet'},
        headers={'Accept-Language': 'ru'},
    )

    resp_j = response.json()
    assert response.status_code == 200

    driver = resp_j['orders'][0]['driver']
    assert driver['phone'] == expected_phone
    if forwarding_enabled and not empty_phone:
        assert 'forwarding' in driver
        assert driver['forwarding'] == forwarding_struct


@pytest.mark.filldb(order_proc='with_order_source')
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['callcenter'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [{'@app_name': 'callcenter', '@app_ver1': '1'}],
    },
)
@pytest.mark.parametrize(
    'forwarding_enabled, empty_phone',
    [
        pytest.param(
            True,
            False,
            marks=pytest.mark.config(
                INTEGRATION_USE_RAW_DRIVER_PHONE_APPLICATION_LIST={
                    'applications': [],
                },
            ),
        ),
        pytest.param(
            True,
            True,
            marks=pytest.mark.config(
                INTEGRATION_USE_RAW_DRIVER_PHONE_APPLICATION_LIST={
                    'applications': ['callcenter'],
                },
            ),
        ),
        (False, False),
    ],
)
def test_search_has_forwarding_use_raw_phone_config(
        taxi_integration,
        mockserver,
        db,
        forwarding_enabled,
        empty_phone,
        recalc_order,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    origin_phone = '+78003000600'
    orderid = '8c83b49edb274ce0992f337000000002'  # callcenter app
    if empty_phone:
        phone, ext = '', ''
    else:
        phone, ext = '+79636698958', '1513'

    expected_phone = (
        f'{phone},,{ext}'
        if forwarding_enabled and not empty_phone
        else origin_phone
    )

    if forwarding_enabled:
        forwarding_struct = {'phone': phone, 'ext': ext}

        db.order_proc.update(
            {'_id': orderid, 'candidates.0': {'$exists': True}},
            {'$set': {'candidates.0.forwarding': forwarding_struct}},
        )

    response = taxi_integration.post(
        'v1/orders/search',
        {'orderid': orderid},
        headers={'Accept-Language': 'ru'},
    )

    resp_j = response.json()
    assert response.status_code == 200

    driver = resp_j['orders'][0]['driver']
    assert driver['phone'] == expected_phone
    if forwarding_enabled and not empty_phone:
        assert 'forwarding' in driver
        assert driver['forwarding'] == forwarding_struct


@pytest.mark.parametrize(
    'sourceid,code',
    [
        ('call_center', 400),
        ('corp_cabinet', 200),
        ('alice', 200),
        ('svo_order', 200),
        ('uber', 400),
        ('wrong', 400),
    ],
)
@pytest.mark.filldb(order_proc='with_order_source')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_sourceid(
        taxi_integration, mockserver, db, sourceid, code, recalc_order,
):
    """
    Check allowable values of sourceid in request for int-api
    """

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    user_id = 'user1'
    db.users.update({'_id': user_id}, {'$set': {'sourceid': sourceid}})

    request = {'user': {'user_id': user_id}, 'sourceid': sourceid}

    # not all sourceid need, but for simplicity
    if sourceid != 'corp_cabinet':
        request['user']['phone'] = TEST_PHONE

    if sourceid == 'alice':
        request['user'].update({'yandex_uid': '4003514353'})

    response = taxi_integration.post(
        'v1/orders/search', request, headers={'Accept-Language': 'ru'},
    )
    data = response.json()

    assert response.status_code == code
    if code == 200:
        assert data['orders']
    elif code == 400:
        assert data == {'error': {'text': 'source_id invalid'}}
    else:
        assert False


@pytest.mark.filldb(order_proc='with_order_source')
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'source,phone_exist,code',
    [
        ('corp_cabinet', False, 200),
        ('corp_cabinet', True, 200),
        ('call_center', True, 200),
        ('call_center', False, 400),
        ('svo_order', True, 200),
        ('svo_order', False, 400),
        ('alice', True, 200),
        ('alice', False, 400),
    ],
)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_phone(
        taxi_integration,
        mockserver,
        db,
        source,
        phone_exist,
        code,
        recalc_order,
):
    """
    Corp Cabinet doesn't need phone, others need

    """

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    user_id = 'user1'
    db.users.update({'_id': user_id}, {'$set': {'sourceid': source}})

    request = {'user': {'user_id': user_id}}
    if source == 'call_center':
        headers = {'Accept-Language': 'ru', 'User-Agent': 'call_center'}
    else:
        headers = {'Accept-Language': 'ru'}
        request['sourceid'] = source

    if source == 'alice':
        request['user'].update({'yandex_uid': '4003514353'})

    if phone_exist:
        request['user']['phone'] = TEST_PHONE

    response = taxi_integration.post(
        'v1/orders/search', request, headers=headers,
    )
    data = response.json()

    assert response.status_code == code
    if code == 200:
        assert data['orders']
    else:
        assert data == {
            'error': {
                'text': 'either personal_phone_id or phone should be passed',
            },
        }


@pytest.mark.parametrize(
    'fill_rsk_to_order_proc,config_values,route_sharing_url',
    [
        (
            True,
            {
                'ROUTE_SHARING_URL_TEMPLATES': {
                    'yandex': 'https://taxi.yandex.ru/route/{key}',
                    'yataxi': 'https://taxi.yandex.ru/route/{key}',
                },
            },
            'https://taxi.yandex.ru/route/a5709ce56c2740d9a536650f5390de01',
        ),
        (
            True,
            {
                'ROUTE_SHARING_URL_TEMPLATES': {
                    'yandex': 'https://taxi.yandex.ru/route/{key}?lang={lang}',
                    'yataxi': 'https://taxi.yandex.ru/route/{key}?lang={lang}',
                },
            },
            'https://taxi.yandex.ru/route/a5709ce56c2740d9a536650f5390de01'
            + '?lang=ru',
        ),
        (True, {'ROUTE_SHARING_URL_TEMPLATES': {}}, None),
        (
            False,
            {
                'ROUTE_SHARING_URL_TEMPLATES': {
                    'yandex': 'https://taxi.yandex.ru/route/{key}',
                    'yataxi': 'https://taxi.yandex.ru/route/{key}',
                },
            },
            None,
        ),
    ],
)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_route_sharing_url(
        taxi_integration,
        mockserver,
        config,
        db,
        fill_rsk_to_order_proc,
        config_values,
        route_sharing_url,
        recalc_order,
):

    config.set_values(config_values)

    if fill_rsk_to_order_proc:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337000000001'},
            {'$set': {'order.rsk': 'a5709ce56c2740d9a536650f5390de01'}},
        )

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['orders'][0].get('route_sharing_url') == route_sharing_url


@pytest.mark.parametrize(
    'is_cost_in_order',
    [
        pytest.param(True, id='Order with cost'),
        pytest.param(False, id='Order without cost'),
    ],
)
@pytest.mark.parametrize(
    'orderid, expected_calc_type, is_fixed',
    [
        pytest.param(
            'without-fixed_price-field', 'taximeter_permanent', False,
        ),
        pytest.param('with-fixed_price-field', 'fixed', True),
        pytest.param(
            'with-fixed_price-field-no-price', 'taximeter_obliged', False,
        ),
    ],
)
@pytest.mark.filldb(order_proc='price_calc_type')
def test_price_calc_type(
        taxi_integration,
        mockserver,
        config,
        db,
        is_cost_in_order,
        orderid,
        expected_calc_type,
        is_fixed,
        recalc_order,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    if not is_cost_in_order:
        db.order_proc.update({'_id': orderid}, {'$unset': {'order.cost': 1}})

    def get_cost_part_amount(breakdown, name):
        for part in breakdown:
            if part['display_name'] == name:
                return part['display_amount']
        return None

    response = taxi_integration.post(
        'v1/orders/search',
        {'orderid': orderid},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )

    assert response.status_code == 200
    assert (
        response.json()['orders'][0]['price_calc_type'] == expected_calc_type
    )

    cost_breakdown = response.json()['orders'][0]['cost_message_details'][
        'cost_breakdown'
    ]

    def check_cost_str(name, amount):
        assert get_cost_part_amount(cost_breakdown, name) == (
            f'{amount} руб.'
            if (is_fixed or is_cost_in_order)
            else f'От {amount} руб.'
        )

    check_cost_str('cost', 555)
    check_cost_str('cost_without_discount', 653)


@pytest.mark.filldb(order_proc='route_points_types')
def test_route_points_types(
        taxi_integration, mockserver, config, db, recalc_order,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'orderid': 'order_to_test_route_points_types'},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )

    assert response.status_code == 200
    for index, type in enumerate(
            [
                'address',
                'organization',
                'address',
                'organization',
                'address',
                'unknown',
            ],
    ):
        assert (
            response.json()['orders'][0]['request']['route'][index]['type']
            == type
        ), 'type mismatch at point with index ' + str(index)


@pytest.mark.filldb(order_proc='no_country')
def test_no_country(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.7,
            'lon': 37.6,
            'speed': 30,
            'timestamp': 1502366306,
        }

    request = {'orderid': 'no_country_id'}

    response = taxi_integration.post(
        'v1/orders/search',
        request,
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )

    assert response.status_code == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    route = orders[0]['request']['route']
    assert len(route) == 2
    assert route[0]['country'] == 'Россия'
    assert route[1]['country'] == ''


@pytest.mark.filldb(order_proc='no_phone')
def test_no_phone(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.7,
            'lon': 37.6,
            'speed': 30,
            'timestamp': 1502366306,
        }

    request = {'orderid': 'no_phone_id'}

    response = taxi_integration.post(
        'v1/orders/search',
        request,
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )

    assert response.status_code == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['driver'] == {'name': 'Иванов Александр', 'phone': ''}


@pytest.mark.filldb(order_proc='price_calc_type')
def test_coupon(taxi_integration, mockserver, db, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        pass

    db.tariff_settings.update({'hz': 'moscow'}, {'$set': {'discount': 0}})
    doc = db.order_proc.find_one(
        {'_id': 'with-fixed_price-field'}, {'order': True},
    )
    cost = doc['order']['cost']

    response = taxi_integration.post(
        'v1/orders/search',
        {'orderid': 'with-fixed_price-field', 'sourceid': 'maps_web'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    cost_breakdown = data['orders'][0]['cost_message_details'][
        'cost_breakdown'
    ]
    assert [
        {'display_amount': f'{cost} руб.', 'display_name': 'cost'},
    ] == cost_breakdown


@pytest.mark.filldb(order_proc='price_calc_type')
def test_invalid_coupon(taxi_integration, mockserver, db, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        pass

    db.tariff_settings.update({'hz': 'moscow'}, {'$set': {'discount': 0}})
    doc = db.order_proc.find_one(
        {'_id': 'with-fixed_price-field'}, {'order': True},
    )
    print('WWWWWWWWWWW doc = {}'.format(doc))
    db.order_proc.update(
        {'_id': 'with-fixed_price-field'},
        {'$set': {'order.coupon.valid': False}},
    )
    cost = doc['order']['cost']

    response = taxi_integration.post(
        'v1/orders/search',
        {'orderid': 'with-fixed_price-field', 'sourceid': 'maps_web'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    cost_breakdown = data['orders'][0]['cost_message_details'][
        'cost_breakdown'
    ]
    assert [
        {'display_amount': f'{cost} руб.', 'display_name': 'cost'},
    ] == cost_breakdown


@pytest.mark.filldb(order_proc='price_calc_type')
def test_is_used_current_prices(
        taxi_integration, mockserver, db, recalc_order,
):
    setup_order_proc_current_prices(
        db, 355, 'with-fixed_price-field', True, 'fixed',
    )

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        pass

    db.tariff_settings.update({'hz': 'moscow'}, {'$set': {'discount': 0}})
    doc = db.order_proc.find_one(
        {'_id': 'with-fixed_price-field'}, {'order': True},
    )
    print('WWWWWWWWWWW doc = {}'.format(doc))
    db.order_proc.update(
        {'_id': 'with-fixed_price-field'},
        {'$set': {'order.coupon.valid': False}},
    )

    response = taxi_integration.post(
        'v1/orders/search',
        {'orderid': 'with-fixed_price-field', 'sourceid': 'maps_web'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    cost_breakdown = data['orders'][0]['cost_message_details'][
        'cost_breakdown'
    ]
    assert [
        {'display_amount': '355 руб.', 'display_name': 'cost'},
    ] == cost_breakdown


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.filldb(order_proc='legal_entities')
def test_with_legal_entities(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {
            'user': {'phone': TEST_PHONE, 'user_id': 'user1'},
            'chainid': 'chainid_1',
        },
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data['orders']) == 1
    park_entity = None
    for entity in data['orders'][0]['legal_entities']:
        if entity['type'] == 'park':
            park_entity = entity
            break
    assert park_entity
    assert park_entity['tin'] == '987654321'


@pytest.mark.config(CALLCENTER_ORDER_TIME_TO_CANCEL=0)
@pytest.mark.filldb(order_proc='cc_transporting')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_cc_cancel_disabled(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {
            'user': {'phone': TEST_PHONE, 'user_id': 'user1'},
            'chainid': 'chainid_1',
        },
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data['orders']) == 1
    assert data['orders'][0]['cancel_disabled']


@pytest.mark.config(CALLCENTER_ORDER_TIME_TO_CANCEL=1000000)
@pytest.mark.filldb(order_proc='cc_transporting')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_cc_cancel_enabled(taxi_integration, mockserver, recalc_order):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {
            'user': {'phone': TEST_PHONE, 'user_id': 'user1'},
            'chainid': 'chainid_1',
        },
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data['orders']) == 1
    assert not data['orders'][0]['cancel_disabled']


@pytest.mark.parametrize(('phone', 'user_id'), ((TEST_PHONE, 'user1'),))
@pytest.mark.translations(
    client_messages={
        'updated_requirements.creditcard.code': {'ru': 'Код', 'en': 'Code'},
    },
)
@pytest.mark.filldb(order_proc='payment_changes')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_payment_changes(
        taxi_integration, mockserver, phone, user_id, recalc_order,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data['orders'][0]['payment_changes']) == 1


@pytest.mark.translations(
    client_messages={
        # button_modifiers
        'deaf_driver.call_to_driver.label': {'ru': 'deaf driver label'},
        'deaf_driver.call_to_driver.dialog_title': {'ru': 'dialog title'},
        'deaf_driver.call_to_driver.dialog_message': {'ru': 'dialog message'},
        'deaf_driver.call_to_driver.button_title_back': {
            'ru': 'back button title',
        },
        # force_destination
        'deaf_driver.force_destination.dialog_title': {'ru': 'dialog title'},
        'deaf_driver.force_destination.dialog_message': {
            'ru': 'dialog message',
        },
        'deaf_driver.force_destination.button_title_destination': {
            'ru': 'destination button title',
        },
        'deaf_driver.force_destination.button_title_back': {
            'ru': 'back button title',
        },
    },
)
@pytest.mark.filldb(order_proc='deaf_driver')
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_deaf_driver(taxi_integration, mockserver, load_json):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == load_json('response/deaf_driver.json')


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize('is_chat_visible', [False, True])
def test_chat_field(
        taxi_integration, mockserver, db, is_chat_visible, recalc_order,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337000000001'},
        {'$set': {'chat_id': 'test_chat_id', 'chat_visible': is_chat_visible}},
    )

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['orders'][0]['driverclientchat_enabled'] is is_chat_visible


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'auction_data, fixed_price, response_etalon',
    [
        (
            {
                'auction': {
                    'iteration': 0,
                    'price': {'base': 1000, 'current': 1000},
                    'allowed_price_change': {
                        'fixed_steps': {'step': 50, 'max_steps': 3},
                    },
                },
            },
            True,
            {
                'current_price': 1000.0,
                'iteration': 0,
                'allowed_price_change': {
                    'fixed_steps': {'step': 50, 'max_steps': 3},
                },
            },
        ),
        (
            {
                'auction': {
                    'iteration': 1,
                    'price': {'base': 1000, 'current': 1100},
                },
            },
            True,
            {'current_price': 1100.0, 'iteration': 1},
        ),
        (
            {
                'auction': {
                    'iteration': 1,
                    'price': {'base': 1000, 'current': 1100},
                },
            },
            False,
            {'current_price': 100.0, 'iteration': 1},
        ),
        ({'auction': {'iteration': 0}}, True, None),
    ],
)
def test_auction(
        taxi_integration,
        mockserver,
        db,
        auction_data,
        fixed_price,
        response_etalon,
        recalc_order,
):
    order_proc_update = {'$set': auction_data}
    if fixed_price:
        order_proc_update['$set']['order.fixed_price.price'] = 5
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337000000001'}, order_proc_update,
    )

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['orders'][0].get('auction') == response_etalon
    assert data['orders'][0]['currency_rules'] == {
        'code': 'RUB',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'руб.',
        'cost_precision': 0,
    }


@pytest.mark.filldb(order_proc='price_calc_type')
@pytest.mark.parametrize(
    'performer_paid_supply,expected_paid_supply',
    [
        (None, None),
        (
            True,
            {
                'is_dropped': False,
                'paid_supply_price': '45 руб.',
                'paid_supply_price_raw': 45.0,
            },
        ),
        (False, {'is_dropped': True}),
    ],
)
def test_paid_supply(
        taxi_integration,
        mockserver,
        db,
        performer_paid_supply,
        expected_paid_supply,
        recalc_order,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        pass

    db.tariff_settings.update({'hz': 'moscow'}, {'$set': {'discount': 0}})
    order_proc_update = {'$set': {'order.coupon.valid': False}}
    if performer_paid_supply is not None:
        order_proc_update = {
            '$set': {
                'order.fixed_price.paid_supply_price': 45,
                'order.performer.paid_supply': performer_paid_supply,
            },
        }
    db.order_proc.update({'_id': 'with-fixed_price-field'}, order_proc_update)

    response = taxi_integration.post(
        'v1/orders/search',
        {'orderid': 'with-fixed_price-field', 'sourceid': 'maps_web'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert orders
    order = orders[0]
    if expected_paid_supply is not None:
        assert 'paid_supply' in order
        assert order['paid_supply'] == expected_paid_supply
    else:
        assert 'paid_supply' not in order


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'is_config_enbaled',
    [
        pytest.param(False, id='config disabled'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                ORDERS_SEARCH_VISIBILITY_HELPER_ENABLED_FOR_APPLICATIONS=[
                    'call_center',
                ],
            ),
            id='config enabled',
        ),
    ],
)
@pytest.mark.parametrize(
    'are_brands_mathching',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                APPLICATION_BRAND_CATEGORIES_SETS={'yataxi': ['econom']},
            ),
            id='ok',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                APPLICATION_BRAND_CATEGORIES_SETS={'yataxi': ['vip']},
            ),
            id='order filtered by brand',
        ),
    ],
)
def test_not_visible(
        taxi_integration,
        mockserver,
        are_brands_mathching,
        is_config_enbaled,
        recalc_order,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_integration.post(
        'v1/orders/search',
        {'user': {'phone': TEST_PHONE, 'user_id': 'user1'}},
        headers={'Accept-Language': 'ru', 'User-Agent': 'call_center'},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    if not is_config_enbaled or are_brands_mathching:
        data['orders'][0].pop('cancel_rules')
        assert data == RESPONSE_SAMPLE_BASE
    else:
        assert len(data['orders']) == 0
