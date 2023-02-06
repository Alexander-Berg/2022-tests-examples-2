import pytest


DEFAULT_HEADERS = {
    'X-Request-Language': 'ru',
    'X-YaTaxi-User': 'personal_phone_id=111,eats_user_id=222',
    'X-YaTaxi-Session': 'taxi:333',
    'X-Yandex-Uid': '3456723',
    'X-YaTaxi-Bound-Uids': '',
    'X-YaTaxi-Pass-Flags': 'portal',
    'content-type': 'application/json',
}


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(
    EATS_PLUS_PRESENTATION_BANNER_SETTINGS={
        'handler_enabled': True,
        'use_experiment': False,
        'handler_default': {
            'text_parts': [
                {'text': 'А тут '},
                {'text': '{balance}', 'styles': {'rainbow': True}},
                {'text': ' у нас ваш баланс'},
            ],
        },
    },
)
async def test_cashback_layout_happy_path(
        taxi_eats_plus, passport_blackbox, plus_wallet,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 2812})

    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/presentation/cashback/layout',
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'banner': {
            'text_parts': [
                {'text': 'А тут '},
                {'text': '2812', 'styles': {'rainbow': True}},
                {'text': ' у нас ваш баланс'},
            ],
        },
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(
    EATS_PLUS_PRESENTATION_BANNER_SETTINGS={
        'handler_enabled': True,
        'use_experiment': False,
        'handler_default': {
            'text_parts': [
                {'text': 'А тут '},
                {'text': '{balance}', 'styles': {'rainbow': True}},
                {'text': ' у нас ваш баланс'},
            ],
        },
    },
)
@pytest.mark.parametrize('currency', ['RUB', 'BYN', 'KZT'])
@pytest.mark.parametrize(
    'display_precision,balance,standard_displayed_balance',
    [
        pytest.param(0, 0.0, '0', id='displays 0 balance'),
        pytest.param(0, 100, '100', id='displays balance as is (prec 0)'),
        pytest.param(1, 100.9, '100.9', id='displays balance as is (prec 1)'),
        pytest.param(0, 100.9, '100', id='rounds balance down (prec 0)'),
        pytest.param(
            1,
            100,
            '100',
            id='does not affect balance in case of higher precision',
        ),
        pytest.param(1, 100.99, '100.9', id='rounds balance down (prec 1)'),
    ],
)
# @pytest.mark.parametrize('balance', [0.0, 100, 100.1, 100.4, 100.5, 100.9])
async def test_cashback_layout_display_precision(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        taxi_config,
        currency,
        display_precision,
        balance,
        standard_displayed_balance,
):
    taxi_config.set_values(
        {
            'EATS_PLUS_ROUNDING_AND_PRECISION_BY_CURRENCY_V2': {
                currency: {
                    'display_precision': display_precision,
                    'income_round_policy': 'half_up_round_policy',
                    'income_precision': 0,
                    'outcome_precision': 0,
                },
            },
        },
    )

    taxi_config.set_values(
        {
            'EATS_PLUS_DEFAULT_CURRENCY': {
                'enabled': True,
                'fallback': False,
                'currency': currency,
            },
        },
    )

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({currency: balance})

    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/presentation/cashback/layout',
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'banner': {
            'text_parts': [
                {'text': 'А тут '},
                {
                    'text': standard_displayed_balance,
                    'styles': {'rainbow': True},
                },
                {'text': ' у нас ваш баланс'},
            ],
        },
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(
    EATS_PLUS_PRESENTATION_BANNER_SETTINGS={
        'handler_enabled': True,
        'use_experiment': True,
        'handler_default': {
            'text_parts': [{'text': 'Нам не нужно это значение'}],
        },
    },
)
@pytest.mark.experiments3(filename='eats_plus_banner_for_layout.json')
@pytest.mark.experiments3(filename='exp3_eats_plus_check_geozone.json')
@pytest.mark.parametrize(
    'location,yandex_uid,has_plus,balance,expected_response',
    [
        (
            None,
            '3456723',
            False,
            0,
            {'banner': {'text_parts': [{'text': 'Ни баллов ни подписки'}]}},
        ),
        (
            None,
            '3456723',
            False,
            100,
            {
                'banner': {
                    'text_parts': [
                        {'text': 'У вас подписки нет, а мы вам тут '},
                        {'styles': {'rainbow': True}, 'text': '100 баллов'},
                        {'text': 'накопили!'},
                    ],
                },
            },
        ),
        (
            None,
            '28120000',
            True,
            100500,
            {
                'banner': {
                    'text_parts': [
                        {'text': 'У вас '},
                        {'styles': {'rainbow': True}, 'text': 'очень много'},
                        {'text': 'баллов накопилось.'},
                    ],
                },
            },
        ),
        (
            {'latitude': 12.3456, 'longitude': 12.3456},
            '12344321',
            True,
            100500,
            {'banner': {'text_parts': [{'text': 'Ни баллов ни подписки'}]}},
        ),
        (
            {'latitude': 2.000, 'longitude': 2.000},
            '12344321',
            True,
            100500,
            {
                'banner': {
                    'text_parts': [
                        {'text': 'У вас подписки нет, а мы вам тут '},
                        {'styles': {'rainbow': True}, 'text': '100500 баллов'},
                        {'text': 'накопили!'},
                    ],
                },
            },
        ),
        (
            {'latitude': 75.000, 'longitude': 75.000},
            '12344321',
            True,
            100500,
            {
                'banner': {
                    'text_parts': [
                        {'text': 'У вас '},
                        {'styles': {'rainbow': True}, 'text': 'очень много'},
                        {'text': 'баллов накопилось.'},
                    ],
                },
            },
        ),
        (
            {'latitude': 90.000, 'longitude': 90.000},
            '12344321',
            True,
            100500,
            {},
        ),
    ],
)
@pytest.mark.eats_plus_regions_cache(
    [
        {
            'id': 1111,
            'name': 'Moscow',
            'slug': 'moscow',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [11.1111, 11.1111, 22.2222, 22.2222],
            'center': [12.3456, 12.3456],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [213, 216],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
        {
            'id': 2222,
            'name': 'SPB',
            'slug': 'spb',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [1.000, 1.000, 3.000, 3.000],
            'center': [2.000, 2.000],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [321, 911],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
        {
            'id': 3333,
            'name': 'EKB',
            'slug': 'ekb',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [70.000, 70.000, 80.000, 80.000],
            'center': [75.000, 75.000],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [1, 2],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
        {
            'id': 112233,
            'name': 'KZN',
            'slug': 'kzn',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [80.000, 80.000, 100.000, 100.000],
            'center': [90.000, 90.000],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [1, 2],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
    ],
)
async def test_cashback_layout_experiment_data(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        yandex_uid,
        has_plus,
        balance,
        expected_response,
        location,
        eats_plus_regions_cache,
):
    passport_blackbox(has_plus=has_plus, has_cashback=True)
    plus_wallet({'RUB': balance})

    headers = DEFAULT_HEADERS.copy()
    headers['X-Yandex-Uid'] = yandex_uid
    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/presentation/cashback/layout',
        headers=headers,
        json={'location': location},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(
    EATS_PLUS_PRESENTATION_BANNER_SETTINGS={
        'handler_enabled': True,
        'use_experiment': False,
        'handler_default': {
            'text_parts': [
                {'text': 'А тут '},
                {'text': '{balance}', 'styles': {'rainbow': True}},
                {'text': ' у нас ваш баланс'},
            ],
        },
        'handle_without_uid': {
            'enabled': True,
            'handler_default': {
                'text_parts': [{'text': 'Вы не авторизовались'}],
            },
        },
    },
)
async def test_cashback_layout_unauthorized(taxi_eats_plus):
    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/presentation/cashback/layout',
        headers={'content-type': 'application/json'},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'banner': {'text_parts': [{'text': 'Вы не авторизовались'}]},
    }


@pytest.mark.parametrize(
    'location,expected_response',
    [
        (
            {'latitude': 55.750028, 'longitude': 37.534397},
            {
                'banner': {
                    'text_parts': [
                        {'text': 'Ваш баланс:'},
                        {'text': '2812', 'styles': {'rainbow': True}},
                    ],
                },
            },
        ),
        ({'latitude': 55.798910, 'longitude': 49.105788}, {}),
        (
            {'latitude': 12.3456, 'longitude': 12.3456},
            {
                'banner': {
                    'text_parts': [
                        {'text': 'Ваш баланс:'},
                        {'text': '2812', 'styles': {'rainbow': True}},
                    ],
                },
            },
        ),
        ({'latitude': 2.000, 'longitude': 2.000}, {}),
    ],
)
@pytest.mark.eats_plus_regions_cache(
    [
        {
            'id': 333,
            'name': 'Moscow',
            'slug': 'moscow',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [11.1111, 11.1111, 22.2222, 22.2222],
            'center': [12.3456, 12.3456],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [213, 216],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
        {
            'id': 2,
            'name': 'SPB',
            'slug': 'spb',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [1.000, 1.000, 3.000, 3.000],
            'center': [2.000, 2.000],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [321, 911],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
    ],
)
@pytest.mark.experiments3(filename='exp3_eats_plus_check_geozone.json')
async def test_cashback_layout_check_location(
        taxi_eats_plus,
        location,
        expected_response,
        passport_blackbox,
        plus_wallet,
        eats_plus_regions_cache,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 2812})

    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/presentation/cashback/layout',
        headers=DEFAULT_HEADERS,
        json={'location': location},
    )
    assert response.status_code == 200
    response = response.json()
    assert response == expected_response


@pytest.mark.config(
    EATS_PLUS_OPTIN_ENABLED_CITIES={
        'check_location': False,
        'cities': ['ru-mow'],
    },
)
async def test_cashback_layout_check_location_disabled(
        taxi_eats_plus, passport_blackbox, plus_wallet,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 2812})

    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/presentation/cashback/layout',
        headers=DEFAULT_HEADERS,
        json={'location': {'latitude': 55.798910, 'longitude': 49.105788}},
    )
    assert response.status_code == 200
    response = response.json()
    assert response == {
        'banner': {
            'text_parts': [
                {'text': 'Ваш баланс:'},
                {'text': '2812', 'styles': {'rainbow': True}},
            ],
        },
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(
    EATS_PLUS_PRESENTATION_BANNER_SETTINGS={
        'handler_enabled': True,
        'use_experiment': False,
        'handler_default': {
            'text_parts': [
                {'text': 'А тут '},
                {'text': '{balance}', 'styles': {'rainbow': True}},
                {'text': ' у нас ваш баланс'},
            ],
        },
    },
)
async def test_cashback_layout_plus_wallet_retry(
        taxi_eats_plus, mockserver, passport_blackbox,
):
    passport_blackbox(has_plus=True, has_cashback=True)

    calls_count = 0

    @mockserver.json_handler('plus-wallet/v1/balances')
    def _plus_balance(request):
        nonlocal calls_count
        calls_count += 1
        if calls_count == 1:
            raise mockserver.TimeoutError()

        return {
            'balances': [
                {
                    'wallet_id': 'wallet_1',
                    'balance': '2812',
                    'currency': 'RUB',
                },
            ],
        }

    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/presentation/cashback/layout',
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    response = response.json()
    assert calls_count == 2
    assert response == {
        'banner': {
            'text_parts': [
                {'text': 'А тут '},
                {'text': '2812', 'styles': {'rainbow': True}},
                {'text': ' у нас ваш баланс'},
            ],
        },
    }
