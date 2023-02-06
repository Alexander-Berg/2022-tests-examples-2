# pylint: disable=redefined-outer-name
import decimal

import pytest

DEFAULT_SPEND_PERIOD = 'IRREGULAR'
DEFAULT_CASH_PERIOD = 'IRREGULAR'
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


@pytest.fixture()
def check_card_has_values(get_card):
    def do_check_card_has_values(
            ucid,
            spend_limit_period,
            spend_limit,
            cash_limit_period,
            cash_limit,
    ):
        card = get_card(ucid=str(ucid))
        assert card['ucid'] == str(ucid)
        assert card['spend_limit_period'] == spend_limit_period
        assert card['spend_limit_value'] == decimal.Decimal(spend_limit)
        assert card['spend_limit_remain'] == decimal.Decimal(spend_limit)
        assert card['cash_limit_period'] == cash_limit_period
        assert card['cash_limit_value'] == decimal.Decimal(cash_limit)
        assert card['cash_limit_remain'] == decimal.Decimal(cash_limit)

    return do_check_card_has_values


async def test_set_strict_mode(
        taxi_eats_stub_tinkoff, init_settings, get_general_setting,
):
    setting = get_general_setting()
    assert setting['strict_mode'] is True
    assert setting['error_mode'] is False
    assert setting['mock_error_code'] is None

    response = await taxi_eats_stub_tinkoff.post(
        f'/internal/api/v1/strict-mode/turn-on',
    )
    assert response.status == 204

    setting = get_general_setting()
    assert setting['strict_mode'] is True
    assert setting['error_mode'] is False
    assert setting['mock_error_code'] is None

    response = await taxi_eats_stub_tinkoff.post(
        f'/internal/api/v1/strict-mode/turn-off',
    )
    assert response.status == 204

    setting = get_general_setting()
    assert setting['strict_mode'] is False
    assert setting['error_mode'] is False
    assert setting['mock_error_code'] is None


@pytest.mark.config(
    EATS_STUB_TINKOFF_ERROR_MODE_SETTINGS=TEST_ERROR_MODE_SETTINGS,
)
@pytest.mark.parametrize(
    'strict_mode',
    [
        pytest.param(True, id='strict-mode on'),
        pytest.param(False, id='strict-mode off'),
    ],
)
@pytest.mark.parametrize(
    'error_mode, mock_error_code',
    [
        pytest.param(False, None, id='error-mode off'),
        pytest.param(True, '422', id='error-mode on'),
    ],
)
@pytest.mark.parametrize(
    'ucid, get_limits_expected_status',
    [
        pytest.param(10000000, 200, id='ok data'),
        pytest.param(10000001, 404, id='not found'),
    ],
)
async def test_get_limits_non_strict_mode(
        taxi_eats_stub_tinkoff,
        taxi_config,
        init_settings,
        create_card,
        set_strict_and_error_modes,
        strict_mode,
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

    await set_strict_and_error_modes(
        strict_mode=strict_mode,
        error_mode=error_mode,
        mock_error_code=mock_error_code,
    )

    get_limits_response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{ucid}/limits', headers=HEADERS,
    )
    if error_mode:
        assert get_limits_response.status == int(mock_error_code)

        config = taxi_config.get('EATS_STUB_TINKOFF_ERROR_MODE_SETTINGS')[
            'error_codes'
        ]
        assert get_limits_response.json()['errorId'] == mock_error_code
        assert (
            get_limits_response.json()['errorMessage']
            == config[mock_error_code]
        )
    elif strict_mode:
        assert get_limits_response.status == get_limits_expected_status
        if get_limits_expected_status == 200:
            assert get_limits_response.json() == {
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
    else:
        assert get_limits_response.status == 200
        if get_limits_expected_status == 200:
            assert get_limits_response.json() == {
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
        elif get_limits_expected_status == 404:
            assert get_limits_response.json() == {
                'ucid': ucid,
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


@pytest.mark.config(
    EATS_STUB_TINKOFF_ERROR_MODE_SETTINGS=TEST_ERROR_MODE_SETTINGS,
)
@pytest.mark.parametrize(
    'strict_mode',
    [
        pytest.param(True, id='strict-mode on'),
        pytest.param(False, id='strict-mode off'),
    ],
)
@pytest.mark.parametrize(
    'error_mode, mock_error_code',
    [
        pytest.param(False, None, id='error-mode off'),
        pytest.param(True, '422', id='error-mode on'),
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
        pytest.param(10000001, 1000, 404, id='not found'),
    ],
)
async def test_set_limits_error_mode(
        taxi_eats_stub_tinkoff,
        taxi_config,
        init_settings,
        create_card,
        set_strict_and_error_modes,
        check_card_has_values,
        strict_mode,
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

    await set_strict_and_error_modes(
        strict_mode=strict_mode,
        error_mode=error_mode,
        mock_error_code=mock_error_code,
    )

    set_limit_response = await taxi_eats_stub_tinkoff.post(
        f'/api/v1/card/{ucid}/{limit_type}-limit',
        headers=HEADERS,
        json={'limitValue': new_limit, 'limitPeriod': period},
    )
    if error_mode:
        assert set_limit_response.status == int(mock_error_code)

        config = taxi_config.get('EATS_STUB_TINKOFF_ERROR_MODE_SETTINGS')[
            'error_codes'
        ]
        assert set_limit_response.json()['errorId'] == mock_error_code
        assert (
            set_limit_response.json()['errorMessage']
            == config[mock_error_code]
        )

        check_card_has_values(
            ucid=existing_ucid,
            spend_limit_period=period,
            spend_limit=old_spend_limit,
            cash_limit_period=period,
            cash_limit=old_cash_limit,
        )
    elif strict_mode:
        assert set_limit_response.status == set_limit_expected_status

        if set_limit_expected_status != 200:
            new_spend_limit = old_spend_limit
            new_cash_limit = old_cash_limit
        elif limit_type == 'spend':
            new_spend_limit = new_limit
            new_cash_limit = old_cash_limit
        else:
            new_spend_limit = old_spend_limit
            new_cash_limit = new_limit

        check_card_has_values(
            ucid=existing_ucid,
            spend_limit_period=period,
            spend_limit=new_spend_limit,
            cash_limit_period=period,
            cash_limit=new_cash_limit,
        )
    else:
        assert set_limit_response.status == 200

        if limit_type == 'spend':
            new_spend_limit = new_limit
            new_cash_limit = old_cash_limit
        else:
            new_spend_limit = old_spend_limit
            new_cash_limit = new_limit

        if set_limit_expected_status == 200:
            check_card_has_values(
                ucid=existing_ucid,
                spend_limit_period=period,
                spend_limit=new_spend_limit,
                cash_limit_period=period,
                cash_limit=new_cash_limit,
            )
        elif set_limit_expected_status == 404:
            check_card_has_values(
                ucid=existing_ucid,
                spend_limit_period=period,
                spend_limit=old_spend_limit,
                cash_limit_period=period,
                cash_limit=old_cash_limit,
            )
            check_card_has_values(
                ucid=ucid,
                spend_limit_period=period,
                spend_limit=new_spend_limit,
                cash_limit_period=period,
                cash_limit=new_cash_limit,
            )
