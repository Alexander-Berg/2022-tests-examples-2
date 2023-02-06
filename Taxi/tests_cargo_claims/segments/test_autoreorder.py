import pytest


async def test_forbidden_no_experiment(
        taxi_cargo_claims, create_segment_with_performer,
):
    segment = await create_segment_with_performer()
    response = await taxi_cargo_claims.post(
        '/v1/claims/autoreorder',
        params={'claim_id': f'order/{segment.cargo_order_id}'},
    )
    assert response.status_code == 200

    assert response.json() == {
        'reason': 'disabled_for_dragon',
        'is_autoreorder_enabled': False,
    }


@pytest.mark.parametrize('autoreorder_flow', ['oldway', 'newway'])
async def test_autoreorder_flow(
        taxi_cargo_claims,
        exp_cargo_reorder_decision_maker,
        create_segment_with_performer,
        mock_order_proc_for_autoreorder,
        autoreorder_flow: str,
):
    segment = await create_segment_with_performer(
        autoreorder_flow=autoreorder_flow,
    )

    mock_order_proc_for_autoreorder('taxi_order_id')

    response = await taxi_cargo_claims.post(
        '/v1/claims/autoreorder',
        params={'claim_id': f'order/{segment.cargo_order_id}'},
    )
    assert response.status_code == 200

    if autoreorder_flow == 'oldway':
        assert response.json() == {
            'reason': 'foobar',
            'is_autoreorder_enabled': True,
        }
    else:
        assert response.json() == {
            'reason': 'disabled_for_dragon',
            'is_autoreorder_enabled': False,
        }


async def test_no_such_cargo_order_id(
        taxi_cargo_claims,
        bad_cargo_order_id='1aa9cee6-fabc-43a1-aa71-c5b6ec9ed2eb',
):
    response = await taxi_cargo_claims.post(
        '/v1/claims/autoreorder',
        params={'claim_id': f'order/{bad_cargo_order_id}'},
    )
    assert response.status_code == 200

    assert response.json() == {
        'reason': 'disabled_for_dragon',
        'is_autoreorder_enabled': False,
    }


async def test_oldway_autoreorder_batch(
        taxi_cargo_claims,
        create_segment_with_performer,
        mock_order_proc_for_autoreorder,
        exp_cargo_reorder_decision_maker,
):
    segment_1 = await create_segment_with_performer(
        claim_index=0, autoreorder_flow='oldway',
    )
    await create_segment_with_performer(
        claim_index=1, autoreorder_flow='oldway',
    )

    mock_order_proc_for_autoreorder('taxi_order_id')

    response = await taxi_cargo_claims.post(
        '/v1/claims/autoreorder',
        params={'claim_id': f'order/{segment_1.cargo_order_id}'},
    )
    assert response.status_code == 200

    assert response.json() == {
        'reason': 'foobar',
        'is_autoreorder_enabled': True,
    }
