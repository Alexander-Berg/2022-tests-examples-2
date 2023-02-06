async def test_get_cut(taxi_cargo_claims, state_controller):
    claim_info = await state_controller.apply(target_status='new')
    response = await taxi_cargo_claims.get(
        'v1/claims/cut', params={'claim_id': claim_info.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': claim_info.claim_id,
        'status': 'new',
        'version': 1,
        'user_request_revision': '1',
        'skip_client_notify': False,
    }

    await state_controller.apply(
        target_status='performer_draft', fresh_claim=False,
    )
    response = await taxi_cargo_claims.get(
        'v1/claims/cut', params={'claim_id': claim_info.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': claim_info.claim_id,
        'status': 'performer_draft',
        'version': 1,
        'user_request_revision': '1',
        'taxi_order_id': 'taxi_order_id_1',
        'skip_client_notify': False,
    }


async def test_get_cut_bulk(taxi_cargo_claims, state_controller):
    claim_info = await state_controller.apply(target_status='new')
    response = await taxi_cargo_claims.post(
        '/v1/claims/bulk-info/cut',
        json={'claims': [{'claim_id': claim_info.claim_id}]},
    )
    assert response.status_code == 200
    assert response.json() == {
        'claims': [
            {
                'id': claim_info.claim_id,
                'status': 'new',
                'version': 1,
                'user_request_revision': '1',
                'skip_client_notify': False,
            },
        ],
    }
