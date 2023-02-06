async def test_save_settings(
        taxi_cargo_claims,
        mocker_misc_payments_token,
        get_default_corp_client_id,
):

    mocker_misc_payments_token(status=404)

    response = await taxi_cargo_claims.post(
        'v1/admin/claims/payments/settings',
        params={'corp_client_id': get_default_corp_client_id},
        json={'enabled': True},
    )
    assert response.status == 200
    assert response.json() == {
        'corp_client_id': '01234567890123456789012345678912',
        'enabled': True,
    }


async def test_update_settings(
        taxi_cargo_claims,
        mocker_misc_payments_token,
        set_pay_on_delivering_settings,
        get_default_corp_client_id,
):
    mocker_misc_payments_token(status=404)

    await set_pay_on_delivering_settings(
        corp_client_id=get_default_corp_client_id, enabled=True,
    )

    response = await taxi_cargo_claims.post(
        'v1/admin/claims/payments/settings',
        params={'corp_client_id': get_default_corp_client_id},
        json={'enabled': False},
    )
    assert response.status == 200
    assert response.json() == {
        'corp_client_id': '01234567890123456789012345678912',
        'enabled': False,
    }
