import copy
import datetime

import pytest


CORP_CLIENT_ID = '01234567890123456789012345678912'
EMPLOYER_NAME = 'test_employer_name'


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: EMPLOYER_NAME},
)
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
                    name='cargo_reorder_decision_maker',
                    consumers=['cargo-claims/autoreorder'],
                    clauses=[],
                    default_value={'reason': 'foobar'},
                ),
            ],
            id='default_value_matching',
        ),
        pytest.param(
            {'reason': 'matched', 'is_autoreorder_enabled': True},
            marks=[
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': True,
                    },
                    name='cargo_reorder_decision_maker',
                    consumers=['cargo-claims/autoreorder'],
                    clauses=[
                        {
                            'title': 'experiment_1',
                            'value': {
                                'reason': 'matched',
                                'is_autoreorder_enabled': True,
                            },
                            'predicate': {
                                'init': {
                                    'set': [CORP_CLIENT_ID],
                                    'arg_name': 'corp_client_id',
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                        },
                    ],
                    default_value={'reason': 'foobar'},
                ),
            ],
            id='clause_by_corp_matching',
        ),
        pytest.param(
            {'reason': 'foobar', 'is_autoreorder_enabled': False},
            marks=[
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': True,
                    },
                    name='cargo_reorder_decision_maker',
                    consumers=['cargo-claims/autoreorder'],
                    clauses=[],
                    default_value={
                        'reason': 'foobar',
                        'is_autoreorder_enabled': False,
                    },
                ),
            ],
            id='default_false',
        ),
    ),
)
@pytest.mark.now('2020-04-15T00:11:00+0000')
async def test_autoreorder(
        taxi_cargo_claims,
        state_controller,
        mock_order_proc_for_autoreorder,
        testpoint,
        to_iso8601,
        get_default_request,
        now,
        expected_result,
):
    @testpoint('cargo_reorder_decision_maker')
    def point(data):
        assert data == {
            'corp_client_id': CORP_CLIENT_ID,
            'has_svo_car_number': True,
            'has_paid_supply_price': False,
            'payment_type': 'corp',
            'autoreorder_times': 1,
            'seconds_from_created': 630,
            'seconds_from_waiting': 59,
            'seconds_from_due': 577,
            'employer_name': EMPLOYER_NAME,
        }

    await taxi_cargo_claims.enable_testpoints()

    request = copy.deepcopy(get_default_request())
    request['due'] = to_iso8601(now - datetime.timedelta(seconds=577))
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    mock_order_proc_for_autoreorder()

    response = await taxi_cargo_claims.post(
        '/v1/claims/autoreorder', params={'claim_id': claim_id},
    )
    assert point.has_calls
    assert response.status_code == 200
    assert response.json() == expected_result
