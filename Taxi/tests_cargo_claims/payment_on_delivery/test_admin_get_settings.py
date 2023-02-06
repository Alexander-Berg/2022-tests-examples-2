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
        get_default_corp_client_id,
        mock_cargo_corp,
        is_cargo_corp_down,
        is_agent_scheme,
        expected_result,
):
    mock_cargo_corp.is_cargo_corp_down = is_cargo_corp_down
    mock_cargo_corp.is_agent_scheme = is_agent_scheme

    response = await taxi_cargo_claims.get(
        'v1/admin/claims/payments/settings',
        params={'corp_client_id': get_default_corp_client_id},
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
):
    mocker_misc_payments_token(status=404)

    await set_pay_on_delivering_settings(
        corp_client_id=get_default_corp_client_id, enabled=True,
    )

    response = await taxi_cargo_claims.get(
        'v1/admin/claims/payments/settings',
        params={'corp_client_id': get_default_corp_client_id},
    )
    assert response.status == 200
    assert response.json() == {
        'corp_client_id': '01234567890123456789012345678912',
        'enabled': True,
    }
