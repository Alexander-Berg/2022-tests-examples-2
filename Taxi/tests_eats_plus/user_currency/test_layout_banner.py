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
    EATS_PLUS_OPTIN_ENABLED_CITIES={'cities': [], 'check_location': False},
    EATS_PLUS_DEFAULT_CURRENCY={
        'enabled': False,
        'fallback': False,
        'currency': 'RUB',
    },
)
@pytest.mark.experiments3(filename='exp3_eats_plus_currency.json')
async def test_cashback_layout_fetch_user_currency(
        taxi_eats_plus, passport_blackbox, plus_wallet,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 2812, 'BYN': 2502})

    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/presentation/cashback/layout',
        headers=DEFAULT_HEADERS,
        json={'location': {'latitude': 55.643472, 'longitude': 37.476936}},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'banner': {
            'text_parts': [
                {'text': 'А тут '},
                {'text': '2502', 'styles': {'rainbow': True}},
                {'text': ' у нас ваш баланс'},
            ],
        },
    }
