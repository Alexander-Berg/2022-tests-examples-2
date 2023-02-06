async def test_pricing_payment_methods(
        taxi_cargo_claims,
        state_controller,
        pgsql,
        get_default_headers,
        mock_cargo_corp_up,
):
    state_controller.set_options(cargo_pricing_flow=True)
    state_controller.set_options(is_phoenix_corp=True)
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/accept',
        headers=get_default_headers(),
        params={'claim_id': claim_info.claim_id},
        json={'version': 1},
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""SELECT final_price, price_multiplier FROM cargo_claims.claims
            WHERE uuid_id= '{claim_info.claim_id}'""",
    )
    (final_price, price_multiplier) = list(cursor)[0]
    assert final_price is not None
    assert price_multiplier == 1
