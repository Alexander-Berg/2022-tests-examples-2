# pylint: disable=redefined-outer-name
import decimal

import pytest

HEADERS = {'Authorization': 'Bearer TestToken'}


async def test_get_limit_ok(taxi_eats_stub_tinkoff, create_card):
    ucid = 12345
    spend_period = 'IRREGULAR'
    spend_limit = 1000
    cash_period = 'MONTH'
    cash_limit = 500
    create_card(
        ucid=ucid,
        spend_limit_period=spend_period,
        spend_limit_value=spend_limit,
        spend_limit_remain=spend_limit,
        cash_limit_period=cash_period,
        cash_limit_value=cash_limit,
        cash_limit_remain=cash_limit,
    )

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{ucid}/limits', headers=HEADERS,
    )

    assert response.status == 200
    assert response.json() == {
        'ucid': ucid,
        'spendLimit': {
            'limitPeriod': spend_period,
            'limitValue': decimal.Decimal(spend_limit),
            'limitRemain': decimal.Decimal(spend_limit),
        },
        'cashLimit': {
            'limitPeriod': cash_period,
            'limitValue': decimal.Decimal(cash_limit),
            'limitRemain': decimal.Decimal(cash_limit),
        },
    }


@pytest.mark.parametrize(
    'ucid, expected_status',
    [
        pytest.param(12345678, 404, id='not found'),
        pytest.param('bad-value', 400, id='bad ucid'),
    ],
)
async def test_get_limit_errors(taxi_eats_stub_tinkoff, ucid, expected_status):
    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{ucid}/limits', headers=HEADERS,
    )

    assert response.status == expected_status
