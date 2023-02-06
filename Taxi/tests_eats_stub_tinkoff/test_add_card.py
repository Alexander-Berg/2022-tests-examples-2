# pylint: disable=redefined-outer-name
import decimal

import pytest

DEFAULT_SPEND_PERIOD = 'IRREGULAR'
DEFAULT_CASH_PERIOD = 'IRREGULAR'
HEADERS = {'Authorization': 'Bearer TestToken'}


@pytest.mark.parametrize(
    'ucid, expected_status',
    [
        pytest.param('10000001', 200, id='simple create'),
        pytest.param('bad-cid', 400, id='error 400'),
        pytest.param('10000000', 409, id='error 409'),
    ],
)
async def test_add_card(
        taxi_eats_stub_tinkoff, create_card, ucid, expected_status,
):
    existing_ucid = '10000000'
    old_spend_period = 'IRREGULAR'
    old_spend_limit = 1000
    old_cash_period = 'MONTH'
    old_cash_limit = 500
    create_card(
        ucid=existing_ucid,
        spend_limit_period=old_spend_period,
        spend_limit_value=old_spend_limit,
        spend_limit_remain=old_spend_limit,
        cash_limit_period=old_cash_period,
        cash_limit_value=old_cash_limit,
        cash_limit_remain=old_cash_limit,
    )

    response = await taxi_eats_stub_tinkoff.post(
        f'/internal/api/v1/card', json={'ucid': ucid},
    )
    assert response.status == expected_status

    if expected_status == 200:
        response = await taxi_eats_stub_tinkoff.get(
            f'/api/v1/card/{ucid}/limits', headers=HEADERS,
        )
        assert response.status == 200
        assert response.json() == {
            'ucid': int(ucid),
            'spendLimit': {
                'limitPeriod': DEFAULT_SPEND_PERIOD,
                'limitValue': decimal.Decimal(0),
                'limitRemain': decimal.Decimal(0),
            },
            'cashLimit': {
                'limitPeriod': DEFAULT_CASH_PERIOD,
                'limitValue': decimal.Decimal(0),
                'limitRemain': decimal.Decimal(0),
            },
        }

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{existing_ucid}/limits', headers=HEADERS,
    )
    assert response.status == 200
    assert response.json() == {
        'ucid': int(existing_ucid),
        'spendLimit': {
            'limitPeriod': old_spend_period,
            'limitValue': decimal.Decimal(old_spend_limit),
            'limitRemain': decimal.Decimal(old_spend_limit),
        },
        'cashLimit': {
            'limitPeriod': old_cash_period,
            'limitValue': decimal.Decimal(old_cash_limit),
            'limitRemain': decimal.Decimal(old_cash_limit),
        },
    }


async def test_add_and_change_card(taxi_eats_stub_tinkoff):
    ucid = '10000000'
    response = await taxi_eats_stub_tinkoff.post(
        f'/internal/api/v1/card', json={'ucid': ucid},
    )
    assert response.status == 200

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{ucid}/limits', headers=HEADERS,
    )
    assert response.status == 200
    assert response.json() == {
        'ucid': int(ucid),
        'spendLimit': {
            'limitPeriod': DEFAULT_SPEND_PERIOD,
            'limitValue': decimal.Decimal(0),
            'limitRemain': decimal.Decimal(0),
        },
        'cashLimit': {
            'limitPeriod': DEFAULT_CASH_PERIOD,
            'limitValue': decimal.Decimal(0),
            'limitRemain': decimal.Decimal(0),
        },
    }

    new_spend_period = 'MONTH'
    new_spend_limit = 1000
    response = await taxi_eats_stub_tinkoff.post(
        f'/api/v1/card/{ucid}/spend-limit',
        headers=HEADERS,
        json={'limitValue': new_spend_limit, 'limitPeriod': new_spend_period},
    )
    assert response.status == 200

    new_cash_period = 'DAY'
    new_cash_limit = 1001
    response = await taxi_eats_stub_tinkoff.post(
        f'/api/v1/card/{ucid}/cash-limit',
        headers=HEADERS,
        json={'limitValue': new_cash_limit, 'limitPeriod': new_cash_period},
    )
    assert response.status == 200

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{ucid}/limits', headers=HEADERS,
    )
    assert response.status == 200
    assert response.json() == {
        'ucid': int(ucid),
        'spendLimit': {
            'limitPeriod': new_spend_period,
            'limitValue': decimal.Decimal(new_spend_limit),
            'limitRemain': decimal.Decimal(new_spend_limit),
        },
        'cashLimit': {
            'limitPeriod': new_cash_period,
            'limitValue': decimal.Decimal(new_cash_limit),
            'limitRemain': decimal.Decimal(new_cash_limit),
        },
    }
