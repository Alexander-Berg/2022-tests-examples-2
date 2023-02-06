# pylint: disable=redefined-outer-name
import decimal

import pytest

DEFAULT_CARD_UCID = 10000000
DEFAULT_SPEND_PERIOD = 'IRREGULAR'
DEFAULT_CASH_PERIOD = 'IRREGULAR'
HEADERS = {'Authorization': 'Bearer TestToken'}


@pytest.mark.parametrize(
    'limit_type,'
    'old_spend_period, new_spend_period,'
    'old_spend_limit, new_spend_limit,'
    'old_cash_period, new_cash_period,'
    'old_cash_limit, new_cash_limit',
    [
        pytest.param(
            'spend',
            'IRREGULAR',
            'MONTH',
            500,
            1000,
            'IRREGULAR',
            'IRREGULAR',
            0,
            0,
            id='spend-limit',
        ),
        pytest.param(
            'cash',
            'IRREGULAR',
            'IRREGULAR',
            0,
            0,
            'IRREGULAR',
            'MONTH',
            500,
            1000,
            id='cash-limit',
        ),
    ],
)
async def test_set_limit_ok(
        taxi_eats_stub_tinkoff,
        create_card,
        limit_type,
        old_spend_period,
        new_spend_period,
        old_spend_limit,
        new_spend_limit,
        old_cash_period,
        new_cash_period,
        old_cash_limit,
        new_cash_limit,
):
    ucid = DEFAULT_CARD_UCID
    create_card(
        ucid=ucid,
        spend_limit_period=old_spend_period,
        spend_limit_value=old_spend_limit,
        spend_limit_remain=old_spend_limit,
        cash_limit_period=old_cash_period,
        cash_limit_value=old_cash_limit,
        cash_limit_remain=old_cash_limit,
    )

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{ucid}/limits', headers=HEADERS,
    )
    assert response.status == 200
    assert response.json() == {
        'ucid': ucid,
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

    if limit_type == 'spend':
        new_card_limit = new_spend_limit
        new_period = new_spend_period
    else:
        new_card_limit = new_cash_limit
        new_period = new_cash_period
    response = await taxi_eats_stub_tinkoff.post(
        f'/api/v1/card/{ucid}/{limit_type}-limit',
        headers=HEADERS,
        json={'limitValue': new_card_limit, 'limitPeriod': new_period},
    )
    assert response.status == 200

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{ucid}/limits', headers=HEADERS,
    )
    assert response.status == 200
    assert response.json() == {
        'ucid': ucid,
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


@pytest.mark.parametrize(
    'limit_type, old_spend_limit, old_cash_limit',
    [
        pytest.param('spend', 500, 0, id='spend-limit'),
        pytest.param('cash', 0, 500, id='cash-limit'),
    ],
)
@pytest.mark.parametrize(
    'ucid, new_limit, expected_status',
    [
        pytest.param(DEFAULT_CARD_UCID, 1000, 200, id='200 normal'),
        pytest.param(DEFAULT_CARD_UCID, 0, 200, id='200 zero limit'),
        pytest.param(10000001, 1000, 404, id='404 not found'),
        pytest.param('bad-cid', 1000, 400, id='400 bad ucid'),
        pytest.param(DEFAULT_CARD_UCID, -1000, 400, id='400 bad limit'),
    ],
)
async def test_set_limit_corners(
        taxi_eats_stub_tinkoff,
        create_card,
        limit_type,
        old_spend_limit,
        old_cash_limit,
        ucid,
        new_limit,
        expected_status,
):
    existing_ucid = DEFAULT_CARD_UCID
    period = 'IRREGULAR'
    create_card(
        ucid=existing_ucid,
        spend_limit_period=period,
        spend_limit_value=old_spend_limit,
        spend_limit_remain=old_spend_limit,
        cash_limit_period=period,
        cash_limit_value=old_cash_limit,
        cash_limit_remain=old_cash_limit,
    )

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{existing_ucid}/limits', headers=HEADERS,
    )
    assert response.status == 200
    assert response.json() == {
        'ucid': existing_ucid,
        'spendLimit': {
            'limitPeriod': period,
            'limitValue': decimal.Decimal(old_spend_limit),
            'limitRemain': decimal.Decimal(old_spend_limit),
        },
        'cashLimit': {
            'limitPeriod': period,
            'limitValue': decimal.Decimal(old_cash_limit),
            'limitRemain': decimal.Decimal(old_cash_limit),
        },
    }

    response = await taxi_eats_stub_tinkoff.post(
        f'/api/v1/card/{ucid}/{limit_type}-limit',
        headers=HEADERS,
        json={'limitValue': new_limit, 'limitPeriod': period},
    )
    assert response.status == expected_status

    if expected_status != 200:
        new_spend_limit = old_spend_limit
        new_cash_limit = old_cash_limit
    elif limit_type == 'spend':
        new_spend_limit = new_limit
        new_cash_limit = old_cash_limit
    else:
        new_spend_limit = old_spend_limit
        new_cash_limit = new_limit

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{existing_ucid}/limits', headers=HEADERS,
    )
    assert response.status == 200
    assert response.json() == {
        'ucid': existing_ucid,
        'spendLimit': {
            'limitPeriod': period,
            'limitValue': decimal.Decimal(new_spend_limit),
            'limitRemain': decimal.Decimal(new_spend_limit),
        },
        'cashLimit': {
            'limitPeriod': period,
            'limitValue': decimal.Decimal(new_cash_limit),
            'limitRemain': decimal.Decimal(new_cash_limit),
        },
    }
