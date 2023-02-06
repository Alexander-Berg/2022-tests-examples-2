from typing import List
from typing import Tuple

from aiohttp import test_utils
import pytest


def _make_currency_rules(country_currency=List[Tuple[str, str]]) -> list:
    template = {
        'country_code': 'us',
        'currency': 'USD',
        'exclude_patterns': [],
        'payment_methods': [],
        'phone_patterns': [],
        'show_to_new_users': True,
    }
    result = []
    for country, currency in country_currency:
        rules = {**template, 'country_code': country, 'currency': currency}
        result.append(rules)

    return result


@pytest.mark.parametrize(
    'expected_currencies',
    [
        pytest.param(
            [],
            marks=[pytest.mark.config(PERSONAL_WALLET_CURRENCY_RULES=[])],
            id='empty-config',
        ),
        pytest.param(
            ['RUB', 'EUR', 'USD'],
            marks=[
                pytest.mark.config(
                    PERSONAL_WALLET_CURRENCY_RULES=_make_currency_rules(
                        [
                            ('ru', 'RUB'),
                            ('fr', 'EUR'),
                            ('es', 'EUR'),
                            ('de', 'EUR'),
                            ('us', 'USD'),
                        ],
                    ),
                ),
            ],
            id='normal-config',
        ),
    ],
)
async def test_get_currencies(
        web_app_client: test_utils.TestClient, expected_currencies,
):
    response = await web_app_client.get('/v1/admin/wallets/currencies')
    assert response.status == 200

    response_data = await response.json()

    assert sorted(response_data['currencies']) == sorted(expected_currencies)
