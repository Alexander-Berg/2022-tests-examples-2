# pylint: disable=redefined-outer-name
import decimal

import pytest

HEADERS = {'Authorization': 'Bearer TestToken'}
TEST_ERROR_MODE_SETTINGS = {
    'error_codes': {
        '400': 'test 400',
        '401': 'test 401',
        '403': 'test 403',
        '404': 'test 404',  # значение игнорируется
        '422': 'test 422',
        '500': 'test 500',
    },
}


@pytest.mark.parametrize(
    'mock_error_code, expected_status',
    [
        pytest.param('400', 204, id='turn on 400'),
        pytest.param('401', 204, id='turn on 401'),
        pytest.param('403', 204, id='turn on 403'),
        pytest.param('404', 204, id='turn on 404'),
        pytest.param('422', 204, id='turn on 422'),
        pytest.param('500', 204, id='turn on 500'),
        pytest.param('409', 400, id='not from enum'),
        pytest.param('bad-code', 400, id='bad code'),
    ],
)
async def test_set_error_mode(
        taxi_eats_stub_tinkoff,
        init_settings,
        get_general_setting,
        mock_error_code,
        expected_status,
):
    setting = get_general_setting()
    assert setting['strict_mode'] is True
    assert setting['error_mode'] is False
    assert setting['mock_error_code'] is None

    response = await taxi_eats_stub_tinkoff.post(
        f'/internal/api/v1/error-mode/turn-on',
        json={'error_code': mock_error_code},
    )
    assert response.status == expected_status

    setting = get_general_setting()
    if expected_status == 204:
        assert setting['strict_mode'] is True
        assert setting['error_mode'] is True
        assert setting['mock_error_code'] == mock_error_code
    else:
        assert setting['strict_mode'] is True
        assert setting['error_mode'] is False
        assert setting['mock_error_code'] is None

    response = await taxi_eats_stub_tinkoff.post(
        f'/internal/api/v1/error-mode/turn-off',
    )
    assert response.status == 204

    setting = get_general_setting()
    assert setting['strict_mode'] is True
    assert setting['error_mode'] is False
    assert setting['mock_error_code'] is None


@pytest.mark.config(
    EATS_STUB_TINKOFF_ERROR_MODE_SETTINGS=TEST_ERROR_MODE_SETTINGS,
)
@pytest.mark.parametrize(
    'error_mode, mock_error_code',
    [
        pytest.param(False, None, id='turn off'),
        pytest.param(True, '400', id='turn on 400'),
        pytest.param(True, '401', id='turn on 401'),
        pytest.param(True, '403', id='turn on 403'),
        pytest.param(True, '404', id='turn on 404'),
        pytest.param(True, '422', id='turn on 422'),
        pytest.param(True, '500', id='turn on 500'),
    ],
)
@pytest.mark.parametrize(
    'ucid, get_limits_expected_status',
    [
        pytest.param(10000000, 200, id='ok data'),
        pytest.param(10000001, 404, id='not found'),
    ],
)
async def test_get_limits_error_mode(
        taxi_eats_stub_tinkoff,
        taxi_config,
        init_settings,
        create_card,
        get_general_setting,
        error_mode,
        mock_error_code,
        ucid,
        get_limits_expected_status,
):
    existing_ucid = 10000000
    spend_period = 'IRREGULAR'
    spend_limit = 1000
    cash_period = 'MONTH'
    cash_limit = 500
    create_card(
        ucid=existing_ucid,
        spend_limit_period=spend_period,
        spend_limit_value=spend_limit,
        spend_limit_remain=spend_limit,
        cash_limit_period=cash_period,
        cash_limit_value=cash_limit,
        cash_limit_remain=cash_limit,
    )

    if error_mode:
        response = await taxi_eats_stub_tinkoff.post(
            f'/internal/api/v1/error-mode/turn-on',
            json={'error_code': mock_error_code},
        )
        assert response.status == 204

        setting = get_general_setting()
        assert setting['strict_mode'] is True
        assert setting['error_mode'] is True
        assert setting['mock_error_code'] == mock_error_code

        response = await taxi_eats_stub_tinkoff.get(
            f'/api/v1/card/{ucid}/limits', headers=HEADERS,
        )
        assert response.status == int(mock_error_code)

        config = taxi_config.get('EATS_STUB_TINKOFF_ERROR_MODE_SETTINGS')[
            'error_codes'
        ]
        if mock_error_code == '404':
            assert response.text == ''
        elif mock_error_code in ('401', '403'):
            assert response.text == config[mock_error_code]
        else:
            assert response.json()['errorId'] == mock_error_code
            assert response.json()['errorMessage'] == config[mock_error_code]
    else:
        response = await taxi_eats_stub_tinkoff.post(
            f'/internal/api/v1/error-mode/turn-off',
        )
        assert response.status == 204

        setting = get_general_setting()
        assert setting['strict_mode'] is True
        assert setting['error_mode'] is False
        assert setting['mock_error_code'] is None

        response = await taxi_eats_stub_tinkoff.get(
            f'/api/v1/card/{ucid}/limits', headers=HEADERS,
        )
        assert response.status == get_limits_expected_status
        if get_limits_expected_status == 200:
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


@pytest.mark.config(
    EATS_STUB_TINKOFF_ERROR_MODE_SETTINGS=TEST_ERROR_MODE_SETTINGS,
)
@pytest.mark.parametrize(
    'error_mode, mock_error_code',
    [
        pytest.param(False, None, id='turn off'),
        pytest.param(True, '400', id='turn on 400'),
        pytest.param(True, '401', id='turn on 401'),
        pytest.param(True, '403', id='turn on 403'),
        pytest.param(True, '404', id='turn on 404'),
        pytest.param(True, '422', id='turn on 422'),
        pytest.param(True, '500', id='turn on 500'),
    ],
)
@pytest.mark.parametrize(
    'limit_type, old_spend_limit, old_cash_limit',
    [
        pytest.param('spend', 500, 0, id='spend-limit'),
        pytest.param('cash', 0, 500, id='cash-limit'),
    ],
)
@pytest.mark.parametrize(
    'ucid, new_limit, set_limit_expected_status',
    [
        pytest.param(10000000, 1000, 200, id='normal'),
        pytest.param(10000000, 0, 200, id='zero limit'),
        pytest.param(10000001, 1000, 404, id='not found'),
        pytest.param(10000000, -1000, 400, id='bad limit'),
    ],
)
async def test_set_limits_error_mode(
        taxi_eats_stub_tinkoff,
        taxi_config,
        init_settings,
        create_card,
        get_general_setting,
        get_card,
        error_mode,
        mock_error_code,
        limit_type,
        old_spend_limit,
        old_cash_limit,
        ucid,
        new_limit,
        set_limit_expected_status,
):
    existing_ucid = 10000000
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

    if error_mode:
        response = await taxi_eats_stub_tinkoff.post(
            f'/internal/api/v1/error-mode/turn-on',
            json={'error_code': mock_error_code},
        )
        assert response.status == 204

        setting = get_general_setting()
        assert setting['strict_mode'] is True
        assert setting['error_mode'] is True
        assert setting['mock_error_code'] == mock_error_code

        response = await taxi_eats_stub_tinkoff.post(
            f'/api/v1/card/{ucid}/{limit_type}-limit',
            headers=HEADERS,
            json={'limitValue': new_limit, 'limitPeriod': period},
        )
        assert response.status == int(mock_error_code)

        config = taxi_config.get('EATS_STUB_TINKOFF_ERROR_MODE_SETTINGS')[
            'error_codes'
        ]
        if mock_error_code == '404':
            assert response.text == ''
        elif mock_error_code in ('401', '403'):
            assert response.text == config[mock_error_code]
        else:
            assert response.json()['errorId'] == mock_error_code
            assert response.json()['errorMessage'] == config[mock_error_code]

        card = get_card(ucid=str(existing_ucid))
        assert card['ucid'] == str(existing_ucid)
        assert card['spend_limit_period'] == period
        assert card['spend_limit_value'] == decimal.Decimal(old_spend_limit)
        assert card['spend_limit_remain'] == decimal.Decimal(old_spend_limit)
        assert card['cash_limit_period'] == period
        assert card['cash_limit_value'] == decimal.Decimal(old_cash_limit)
        assert card['cash_limit_remain'] == decimal.Decimal(old_cash_limit)
    else:
        response = await taxi_eats_stub_tinkoff.post(
            f'/internal/api/v1/error-mode/turn-off',
        )
        assert response.status == 204

        setting = get_general_setting()
        assert setting['strict_mode'] is True
        assert setting['error_mode'] is False
        assert setting['mock_error_code'] is None

        response = await taxi_eats_stub_tinkoff.post(
            f'/api/v1/card/{ucid}/{limit_type}-limit',
            headers=HEADERS,
            json={'limitValue': new_limit, 'limitPeriod': period},
        )
        assert response.status == set_limit_expected_status
        if set_limit_expected_status != 200:
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
