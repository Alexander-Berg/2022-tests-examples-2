async def test_corp_not_found(taxi_cargo_claims):
    response = await taxi_cargo_claims.post(
        '/v2/claims/corp-stats',
        params={'corp_client_id': 'b04a64bb1d0147258337412c01176fa1'},
        json={},
    )
    assert response.status_code == 200
    assert response.json() == {'completed': 0, 'total': 0}


async def test_corp_stats(
        taxi_cargo_claims, state_controller, get_default_corp_client_id,
):
    state_controller.use_create_version('v2')
    await state_controller.apply(target_status='new', next_point_order=1)

    response = await taxi_cargo_claims.post(
        '/v2/claims/corp-stats',
        params={'corp_client_id': get_default_corp_client_id},
        json={},
    )
    assert response.status_code == 200
    assert response.json() == {'completed': 0, 'total': 1}
