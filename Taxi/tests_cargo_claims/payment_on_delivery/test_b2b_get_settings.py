import pytest


@pytest.mark.parametrize(
    'is_cargo_corp_down, is_agent_scheme, expected_result',
    [
        pytest.param(
            False, False, True, id='cargo-corp ok, usual default is True',
        ),
        pytest.param(
            False, True, False, id='cargo-corp ok, phoenix default is False',
        ),
        pytest.param(
            True, False, True, id='cargo-corp is down, suppose as not phoenix',
        ),
    ],
)
async def test_get_default_settings(
        taxi_cargo_claims,
        get_default_headers,
        mock_cargo_corp,
        is_cargo_corp_down,
        is_agent_scheme,
        expected_result,
):
    mock_cargo_corp.is_cargo_corp_down = is_cargo_corp_down
    mock_cargo_corp.is_agent_scheme = is_agent_scheme

    response = await taxi_cargo_claims.get(
        'api/integration/v1/claims/payments/settings',
        headers=get_default_headers(),
    )
    assert response.status == 200
    assert response.json() == {
        'corp_client_id': '01234567890123456789012345678912',
        'enabled': expected_result,
    }


async def test_get_settings(
        taxi_cargo_claims,
        mocker_misc_payments_token,
        set_pay_on_delivering_settings,
        get_default_corp_client_id,
        get_default_headers,
):
    mocker_misc_payments_token(status=404)

    await set_pay_on_delivering_settings(
        corp_client_id=get_default_corp_client_id, enabled=True,
    )

    response = await taxi_cargo_claims.get(
        'api/integration/v1/claims/payments/settings',
        headers=get_default_headers(),
    )
    assert response.status == 200
    assert response.json() == {
        'corp_client_id': '01234567890123456789012345678912',
        'enabled': True,
    }


@pytest.mark.parametrize('enabled', [True, False])
async def test_setting_disabled_by_exp(
        taxi_cargo_claims,
        exp_cargo_claims_post_payment_clients,
        get_default_corp_client_id,
        get_default_headers,
        enabled: bool,
):
    """
        Check postpayment setting is disabled by experiment.
        (cargo_claims_post_payment_clients)
    """
    await exp_cargo_claims_post_payment_clients(enabled=enabled)

    response = await taxi_cargo_claims.get(
        'api/integration/v1/claims/payments/settings',
        headers=get_default_headers(),
    )
    assert response.status == 200
    assert response.json() == {
        'corp_client_id': get_default_corp_client_id,
        'enabled': enabled,
    }
