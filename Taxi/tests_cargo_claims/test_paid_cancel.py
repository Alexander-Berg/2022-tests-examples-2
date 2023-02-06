import pytest


@pytest.mark.parametrize(
    ['expected_result'],
    (
        pytest.param(
            {'reason': 'foobar'},
            marks=[
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': True,
                    },
                    name='cargo_driver_waiting_control',
                    consumers=['cargo-claims/paid_cancel'],
                    clauses=[],
                    default_value={'reason': 'foobar'},
                ),
            ],
            id='default_value_matching',
        ),
        pytest.param(
            {'reason': 'foobar', 'paid_cancel_max_waiting_time': 600},
            marks=[
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': True,
                    },
                    name='cargo_driver_waiting_control',
                    consumers=['cargo-claims/paid_cancel'],
                    clauses=[],
                    default_value={
                        'reason': 'foobar',
                        'paid_cancel_max_waiting_time': 600,
                    },
                ),
            ],
            id='default_false',
        ),
        pytest.param(
            {'reason': 'disabled_experiment'},
            marks=[
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': False,
                    },
                    name='cargo_driver_waiting_control',
                    consumers=['cargo-claims/paid_cancel'],
                    clauses=[],
                    default_value={
                        'reason': 'foobar',
                        'paid_cancel_max_waiting_time': 600,
                    },
                ),
            ],
            id='default_false',
        ),
    ),
)
@pytest.mark.now('2020-04-15T00:11:00+0000')
async def test_paid_cancel(
        taxi_cargo_claims, state_controller, expected_result,
):
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    await taxi_cargo_claims.enable_testpoints()

    response = await taxi_cargo_claims.post(
        '/v1/claims/paid-cancel', params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json() == expected_result


async def test_dragon_order(taxi_cargo_claims, create_segment_with_performer):
    segment = await create_segment_with_performer()
    response = await taxi_cargo_claims.post(
        '/v1/claims/paid-cancel',
        params={'claim_id': f'order/{segment.cargo_order_id}'},
    )
    assert response.status_code == 200
