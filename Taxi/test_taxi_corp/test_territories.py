import pytest


@pytest.mark.parametrize(
    'expected_result',
    [
        {
            'supported_order_countries': [
                {
                    '_id': 'rus',
                    'country_code': 'RU',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                    'vat': '18%',
                    'default_language': 'ru',
                    'default_phone_code': '+7',
                    'web_ui_languages': ['ru'],
                    'name_translate': 'Россия',
                    'show_tariffs': True,
                },
            ],
            'supported_user_phones': [
                {
                    'prefixes': ['^76', '^77'],
                    'matches': ['^76', '^77'],
                    'mask': '+\\7 999 999 99 99 9',
                    'min_length': 11,
                    'max_length': 11,
                },
            ],
        },
    ],
)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {
            'country_code': 'RU',
            'currency': 'RUB',
            'currency_sign': '₽',
            'default_language': 'ru',
            'default_phone_code': '+7',
            'utc_offset': '+03:00',
            'vat': 0.18,
            'web_ui_languages': ['ru'],
            'show_tariffs': True,
        },
    },
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'country': 'rus',
            'prefixes': ['+76', '+77'],
            'matches': ['^76', '^77'],
            'mask': '+\\7 999 999 99 99 9',
            'min_length': 11,
            'max_length': 11,
        },
    ],
)
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': 'руб.'},
        'currency_sign.rub': {'ru': '₽'},
    },
    geoareas={'rus': {'ru': 'Россия'}},
)
async def test_territories(
        monkeypatch, taxi_corp_auth_client, expected_result,
):
    response = await taxi_corp_auth_client.get('/1.0/territories')

    assert response.status == 200
    assert await response.json() == expected_result
