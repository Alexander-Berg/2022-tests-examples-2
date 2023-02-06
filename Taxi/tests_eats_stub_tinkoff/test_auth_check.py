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


@pytest.fixture(name='check_response_with_modes')
def _check_response_with_modes():
    async def do_check_response_with_modes(
            response,
            expected_status,
            headers_ok,
            strict_mode,
            error_mode,
            mock_error_code,
            config,
    ):
        if headers_ok:
            if error_mode:
                assert response.status == int(mock_error_code)
                assert response.json()['errorId'] == mock_error_code
                assert (
                    response.json()['errorMessage'] == config[mock_error_code]
                )
            elif strict_mode:
                assert response.status == expected_status
            else:
                assert response.status == 200
        else:
            assert response.status == 401

    return do_check_response_with_modes


@pytest.mark.parametrize(
    'headers, ucid, expected_status',
    [
        pytest.param({}, 12345, 401, id='empty auth header'),
        pytest.param(
            {'Authorization': 'Bearer '}, 12345, 401, id='invalid auth header',
        ),
        pytest.param(HEADERS, 12345, 200, id='auth ok-card ok'),
        pytest.param(HEADERS, 12346, 404, id='auth ok-not found'),
    ],
)
async def test_simple_auth_check(
        taxi_eats_stub_tinkoff, create_card, headers, ucid, expected_status,
):
    existing_ucid = 12345
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

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{ucid}/limits', headers=headers,
    )
    assert response.status == expected_status

    new_spend_limit = 2000
    response = await taxi_eats_stub_tinkoff.post(
        f'/api/v1/card/{ucid}/spend-limit',
        headers=headers,
        json={'limitValue': new_spend_limit, 'limitPeriod': spend_period},
    )
    assert response.status == expected_status

    new_cash_limit = 2000
    response = await taxi_eats_stub_tinkoff.post(
        f'/api/v1/card/{ucid}/cash-limit',
        headers=headers,
        json={'limitValue': new_cash_limit, 'limitPeriod': cash_period},
    )
    assert response.status == expected_status


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
    'headers, headers_ok',
    [
        pytest.param({}, False, id='empty auth'),
        pytest.param({'Authorization': 'Bearer '}, False, id='invalid auth'),
        pytest.param(HEADERS, True, id='auth ok'),
    ],
)
@pytest.mark.parametrize(
    'ucid, expected_status',
    [
        pytest.param(12345, 200, id='card ok'),
        pytest.param(12346, 404, id='card not found'),
    ],
)
async def test_auth_check_with_modes(
        taxi_eats_stub_tinkoff,
        taxi_config,
        init_settings,
        create_card,
        set_strict_and_error_modes,
        check_response_with_modes,
        strict_mode,
        error_mode,
        mock_error_code,
        headers,
        headers_ok,
        ucid,
        expected_status,
):
    config = taxi_config.get('EATS_STUB_TINKOFF_ERROR_MODE_SETTINGS')[
        'error_codes'
    ]

    existing_ucid = 12345
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

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{ucid}/limits', headers=headers,
    )
    await check_response_with_modes(
        response=response,
        expected_status=expected_status,
        headers_ok=headers_ok,
        strict_mode=strict_mode,
        error_mode=error_mode,
        mock_error_code=mock_error_code,
        config=config,
    )

    new_spend_limit = 2000
    response = await taxi_eats_stub_tinkoff.post(
        f'/api/v1/card/{ucid}/spend-limit',
        headers=headers,
        json={'limitValue': new_spend_limit, 'limitPeriod': spend_period},
    )
    await check_response_with_modes(
        response=response,
        expected_status=expected_status,
        headers_ok=headers_ok,
        strict_mode=strict_mode,
        error_mode=error_mode,
        mock_error_code=mock_error_code,
        config=config,
    )

    new_cash_limit = 2000
    response = await taxi_eats_stub_tinkoff.post(
        f'/api/v1/card/{ucid}/cash-limit',
        headers=headers,
        json={'limitValue': new_cash_limit, 'limitPeriod': cash_period},
    )
    await check_response_with_modes(
        response=response,
        expected_status=expected_status,
        headers_ok=headers_ok,
        strict_mode=strict_mode,
        error_mode=error_mode,
        mock_error_code=mock_error_code,
        config=config,
    )
