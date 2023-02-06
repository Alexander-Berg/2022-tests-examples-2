import pytest


TEST_STATUS_BALANCE = '12345.67'

REGIONS_DATA = [
    {
        'id': 1,
        'name': 'Moscow',
        'slug': 'moscow',
        'genitive': '',
        'isAvailable': True,
        'isDefault': True,
        'bbox': [40.40, 10.10, 50.50, 20.20],
        'center': [43.21, 12.34],
        'timezone': 'Europe/Moscow',
        'sort': 1,
        'yandexRegionIds': [213, 216],
        'country': {'code': 'RU', 'id': 35, 'name': 'Российская Федерация'},
    },
    {
        'id': 9,
        'bbox': [20.0, 50.0, 35.128182, 57.796382],
        'center': [27.564091, 53.898191],
        'genitive': 'Minsk',
        'isAvailable': True,
        'isDefault': False,
        'name': 'Ekaterinburg',
        'slug': 'ekaterinburg',
        'sort': 100,
        'timezone': 'Asia/Yekaterinburg',
        'yandexRegionIds': [],
        'country': {'code': 'RU', 'id': 35, 'name': 'Белорусь'},
    },
]


@pytest.mark.config(EATS_PLUS_USE_AUTH_CONTEXT_ENABLED=True)
@pytest.mark.parametrize(
    ['header', 'balance', 'expected_response_code', 'expected_response_body'],
    [
        # Authorized with plus
        (
            {
                'X-Yandex-UID': '111',
                'X-Eats-User': 'user_id=222',
                'X-YaTaxi-Pass-Flags': 'ya-plus',
            },
            TEST_STATUS_BALANCE,
            200,
            {
                'plus_info': {
                    'balances': [
                        {'currency': 'RUB', 'balance': TEST_STATUS_BALANCE},
                    ],
                },
            },
        ),
        # Authorized without balance
        (
            {
                'X-Yandex-UID': '111',
                'X-Eats-User': 'user_id=222',
                'X-YaTaxi-Pass-Flags': '',
            },
            None,
            200,
            {},
        ),
        # Authorized without plus with balance
        (
            {
                'X-Yandex-UID': '111',
                'X-Eats-User': 'user_id=222',
                'X-YaTaxi-Pass-Flags': '',
            },
            TEST_STATUS_BALANCE,
            200,
            {},
        ),
        # Non Authorized
        (
            {},
            None,
            401,
            {
                'code': 'NON_AUTHORIZED',
                'message': 'Request is not authorized.',
            },
        ),
        # Empty yandex uid
        (
            {
                'X-Yandex-UID': '',
                'X-Eats-User': 'user_id=222',
                'X-YaTaxi-Pass-Flags': '',
            },
            None,
            401,
            {'code': 'NON_AUTHORIZED', 'message': 'yandex_uid is empty'},
        ),
    ],
)
async def test_status(
        taxi_eats_plus,
        plus_wallet,
        header,
        balance,
        expected_response_code,
        expected_response_body,
):
    plus_wallet({'RUB': balance})
    response = await taxi_eats_plus.get(
        '/eats/v1/eats-plus/v1/status', headers=header,
    )

    assert response.status_code == expected_response_code
    response = response.json()
    assert response == expected_response_body


@pytest.mark.config(
    EATS_PLUS_USE_AUTH_CONTEXT_ENABLED=True,
    EATS_PLUS_DEFAULT_CURRENCY={
        'currency': 'RUB',
        'enabled': False,
        'fallback': True,
    },
)
@pytest.mark.experiments3(filename='exp3_eats_plus_currency.json')
@pytest.mark.parametrize(
    [
        'header',
        'query_request',
        'expected_response_code',
        'expected_response_body',
    ],
    [
        pytest.param(
            {
                'X-Yandex-UID': '111',
                'X-Eats-User': 'user_id=222',
                'X-YaTaxi-Pass-Flags': 'ya-plus',
            },
            {'latitude': 12.34, 'longitude': 43.21},
            200,
            {
                'plus_info': {
                    'balances': [{'currency': 'RUB', 'balance': '228.228'}],
                },
            },
            id='RUB',
        ),
        pytest.param(
            {
                'X-Yandex-UID': '111',
                'X-Eats-User': 'user_id=222',
                'X-YaTaxi-Pass-Flags': 'ya-plus',
            },
            {'latitude': 53.898191, 'longitude': 27.564091},
            200,
            {
                'plus_info': {
                    'balances': [{'currency': 'BYN', 'balance': '1234.4321'}],
                },
            },
            id='BYN',
        ),
        pytest.param(
            {
                'X-Yandex-UID': '111',
                'X-Eats-User': 'user_id=222',
                'X-YaTaxi-Pass-Flags': 'ya-plus',
            },
            {'region_id': '9'},
            200,
            {
                'plus_info': {
                    'balances': [{'currency': 'BYN', 'balance': '1234.4321'}],
                },
            },
            id='BYN by region_id',
        ),
        pytest.param(
            {
                'X-Yandex-UID': '111',
                'X-Eats-User': 'user_id=222',
                'X-YaTaxi-Pass-Flags': 'ya-plus',
            },
            {'region_id': '1'},
            200,
            {
                'plus_info': {
                    'balances': [{'currency': 'RUB', 'balance': '228.228'}],
                },
            },
            id='RUB by region_id',
        ),
    ],
)
@pytest.mark.eats_plus_regions_cache(REGIONS_DATA)
async def test_status_with_different_currencies(
        taxi_eats_plus,
        plus_wallet,
        header,
        query_request,
        expected_response_code,
        expected_response_body,
):
    plus_wallet({'RUB': '228.228', 'BYN': '1234.4321'})

    response = await taxi_eats_plus.get(
        '/eats/v1/eats-plus/v1/status', headers=header, params=query_request,
    )

    assert response.status_code == expected_response_code
    response = response.json()
    assert response == expected_response_body
