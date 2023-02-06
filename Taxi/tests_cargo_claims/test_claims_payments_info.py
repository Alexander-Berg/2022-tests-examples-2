async def test_ok(
        taxi_cargo_claims, state_controller, get_default_headers, stq_runner,
):
    claim_info = await state_controller.apply(target_status='delivered_finish')

    response = await taxi_cargo_claims.post(
        '/internal/cargo-claims/v1/claims/payments-info',
        json={'taxi_order_id': 'taxi_order_id_1'},
        headers=get_default_headers(),
    )
    assert response.status == 200
    assert response.json() == {
        'claims': [
            {'claim_id': claim_info.claim_id, 'is_logistic_contract': False},
        ],
    }

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_info.claim_id,
        args=[claim_info.claim_id, '123.0', 'some reason'],
        expect_fail=False,
    )

    response = await taxi_cargo_claims.post(
        '/internal/cargo-claims/v1/claims/payments-info',
        json={'taxi_order_id': 'taxi_order_id_1'},
        headers=get_default_headers(),
    )
    assert response.status == 200
    assert response.json() == {
        'claims': [
            {
                'claim_id': claim_info.claim_id,
                'final_price': '123.0000',
                'final_price_mult': '147.6000',
                'is_logistic_contract': False,
            },
        ],
    }
