import pytest

URL = '/eats/v1/eats-payment-methods-availability/v1/payment-methods/side-list'

USER_AGENT = 'yandex-taxi/3.129.0.110856 Android/9 (samsung; SM-A705FN)'

DEFAULT_LOC_POINT = [37.534301, 55.750001]
DEFAULT_YANDEX_UID = '4003514353'
DEFAULT_PERSONAL_PHONE_ID = '5714f45e98956f06baaae3d4'
DEFAULT_APP_NAME = 'yango_android'
DEFAULT_ORDER_TOTAL_COST = '1000'

PA_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-YaTaxi-Pass-Flags': 'phonish',
    'X-Yandex-UID': DEFAULT_YANDEX_UID,
    'X-YaTaxi-PhoneId': DEFAULT_PERSONAL_PHONE_ID,
    'X-Request-Language': 'ru',
    'X-Request-Application': f'app_name={DEFAULT_APP_NAME}',
    'X-Ya-User-Ticket': 'user_ticket',
    'Date': 'Tue, 01 Aug 2017 15:00:00 GMT',
    'X-YaTaxi-User': 'personal_phone_id=5714f45e98956f06baaae3d4',
}

CARD: dict = {
    'availability': {'available': True, 'disabled_reason': ''},
    'bin': '462729',
    'currency': 'RUB',
    'id': 'card-x3609',
    'name': 'VISA',
    'number': '462729****0957',
    'system': 'VISA',
    'type': 'card',
    'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
}

YANDEX_BANK_CARD: dict = {
    'availability': {'available': True, 'disabled_reason': ''},
    'bin': '462729',
    'currency': 'RUB',
    'id': 'card-x3609',
    'name': 'Счет в Яндексе',
    'number': 'yandex-bank-number-overwrite',
    'system': 'YandexBank',
    'type': 'card',
    'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
}

ACTIVE_ORDERS: dict = {'active_orders': [{'id': 'card-x3609', 'count': 2}]}
ACTIVE_ORDERS_EMPTY: dict = {'active_orders': []}

API_PROXY_CARD = {**CARD, 'available': True, 'card_country': 'RU'}
API_PROXY_GOOGLE_PAY = {'type': 'googlepay'}
API_PROXY_YANDEX_CARD = {
    **YANDEX_BANK_CARD,
    'available': True,
    'card_country': 'RU',
}

ALL_AVAILABLE_PAYMENT_TYPES = [
    'card',
    'applepay',
    'googlepay',
    'badge',
    'corp',
    'sbp',
]

CORP = {
    'availability': {'available': True, 'disabled_reason': ''},
    'currency': 'RUB',
    'description': 'eats 3796 of 10000 RUB',
    'id': 'corp:9e63c266c0d84206bbc8765f2cf7a730:RUB',
    'name': 'corp-test',
    'type': 'corp',
    'user_id': '9e63c266c0d84206bbc8765f2cf7a730',
    'client_id': 'beed2277ae71428db1029c07394e542c',
}


def make_side_list_views_config(load_json) -> dict:
    cfg = load_json('side_list_views.json')
    return cfg


def make_side_list_icons_config(load_json) -> dict:
    cfg = load_json('side_list_icons.json')
    return cfg


@pytest.mark.parametrize(
    ['json', 'active_orders'],
    [
        pytest.param(
            {'location': DEFAULT_LOC_POINT}, ACTIVE_ORDERS_EMPTY, id='200',
        ),
        pytest.param(
            {'location': DEFAULT_LOC_POINT},
            ACTIVE_ORDERS,
            id='200 with active orders',
        ),
        pytest.param({}, {}, id='400'),
    ],
)
async def test_just_test(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        load_json,
        json,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_eats_payments_active_orders,
        active_orders,
):
    api_proxy_payment_methods = [API_PROXY_CARD, API_PROXY_GOOGLE_PAY]

    exp_payment_methods(ALL_AVAILABLE_PAYMENT_TYPES)

    experiments3.add_config(**make_side_list_views_config(load_json))

    mock_api_proxy_list_payment_methods(api_proxy_payment_methods)
    mock_corp_int_api_payment_methods_eats([CORP])
    mock_eats_payments_active_orders(active_orders)

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=json, headers=headers,
    )
    assert response.json()


@pytest.mark.parametrize(
    ['json', 'active_orders'],
    [
        pytest.param(
            {'location': DEFAULT_LOC_POINT},
            ACTIVE_ORDERS_EMPTY,
            id='Empty active orders',
        ),
        pytest.param(
            {'location': DEFAULT_LOC_POINT},
            ACTIVE_ORDERS,
            id='Not empty active orders',
        ),
    ],
)
async def test_active_orders_and_group_id(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        load_json,
        json,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_eats_payments_active_orders,
        active_orders,
):
    api_proxy_payment_methods = [API_PROXY_CARD, API_PROXY_GOOGLE_PAY]

    exp_payment_methods(ALL_AVAILABLE_PAYMENT_TYPES)

    experiments3.add_config(**make_side_list_views_config(load_json))

    mock_api_proxy_list_payment_methods(api_proxy_payment_methods)
    mock_corp_int_api_payment_methods_eats([CORP])
    mock_eats_payments_active_orders(active_orders)

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=json, headers=headers,
    )
    if active_orders['active_orders']:
        excpected_count = active_orders['active_orders'][0]['count']
    else:
        excpected_count = 0
    payment_method = response.json()['payment_methods'][0]
    assert payment_method['active_orders']['count'] == excpected_count
    assert response.json()['payment_methods'][0]['group']['id'] == 1


async def test_sbp(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        load_json,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_eats_payments_active_orders,
):
    exp_payment_methods(ALL_AVAILABLE_PAYMENT_TYPES)

    experiments3.add_config(**make_side_list_views_config(load_json))

    mock_api_proxy_list_payment_methods([])
    mock_corp_int_api_payment_methods_eats([])
    mock_eats_payments_active_orders([])

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json={'location': DEFAULT_LOC_POINT}, headers=headers,
    )
    assert response.json()['payment_methods'][1]['type'] == 'sbp'


async def test_actions(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        load_json,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_eats_payments_active_orders,
):
    api_proxy_payment_methods = [API_PROXY_CARD]
    exp_payment_methods(ALL_AVAILABLE_PAYMENT_TYPES)

    experiments3.add_config(**make_side_list_views_config(load_json))

    mock_api_proxy_list_payment_methods(api_proxy_payment_methods)
    mock_corp_int_api_payment_methods_eats([])
    mock_eats_payments_active_orders([])

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json={'location': DEFAULT_LOC_POINT}, headers=headers,
    )
    assert (
        response.json()['payment_methods'][0]['actions'][0]['type'] == 'remove'
    )


async def test_urls(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        load_json,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_eats_payments_active_orders,
):
    api_proxy_payment_methods = [API_PROXY_CARD]
    exp_payment_methods(ALL_AVAILABLE_PAYMENT_TYPES)

    experiments3.add_config(**make_side_list_views_config(load_json))
    experiments3.add_config(**make_side_list_icons_config(load_json))

    mock_api_proxy_list_payment_methods(api_proxy_payment_methods)
    mock_corp_int_api_payment_methods_eats([])
    mock_eats_payments_active_orders([])

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    await taxi_eats_payment_methods_availability.post(
        URL, json={'location': DEFAULT_LOC_POINT}, headers=headers,
    )


async def test_yandex_bank_available(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        load_json,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_eats_payments_active_orders,
):
    api_proxy_payment_methods = [API_PROXY_YANDEX_CARD]
    exp_payment_methods(
        ['card', 'yandex_bank'], side_visibility={'yandex_bank': False},
    )

    experiments3.add_config(**make_side_list_views_config(load_json))
    experiments3.add_config(**make_side_list_icons_config(load_json))

    mock_api_proxy_list_payment_methods(api_proxy_payment_methods)
    mock_corp_int_api_payment_methods_eats([])
    mock_eats_payments_active_orders([])

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json={'location': DEFAULT_LOC_POINT}, headers=headers,
    )
    assert len(response.json()['payment_methods']) == 1
