import pytest

from test_taxi_shared_payments.conftest import DEFAULT_HEADERS


@pytest.mark.config(COOP_ACCOUNT_CURRENCY_CODES=['RUB', 'EUR', 'USD'])
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_name.rub': {'ru': 'Рубль'},
        'currency_sign.rub': {'ru': '₽'},
        'currency_name.usd': {'ru': 'Доллар'},
        'currency_sign.usd': {'ru': '$'},
        'currency_name.eur': {'ru': 'Евро'},
        'currency_sign.eur': {'ru': '€'},
    },
)
async def test_currencies(web_app_client):
    response = await web_app_client.get(
        '/4.0/coop_account/currencies',
        headers={**DEFAULT_HEADERS, 'X-Yandex-UID': 'user1'},
    )
    expected_content = {
        'currencies': [
            {'code': 'RUB', 'text': 'Рубль', 'sign': '₽'},
            {'code': 'EUR', 'text': 'Евро', 'sign': '€'},
            {'code': 'USD', 'text': 'Доллар', 'sign': '$'},
        ],
    }

    content = await response.json()
    assert content == expected_content
