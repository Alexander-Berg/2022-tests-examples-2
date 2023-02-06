import pytest


@pytest.mark.pgsql('eats_robocall', files=['add_calls.sql'])
@pytest.mark.parametrize(
    'request_body, expected_response_body',
    [
        (
            {'call_ids': ['3', '2', '1']},
            {
                'calls_info': [
                    {
                        'call_id': '1',
                        'scenario_name': 'scenario_1',
                        'status': 'waiting_for_call_creation',
                    },
                    {
                        'call_id': '2',
                        'scenario_name': 'scenario_1',
                        'status': 'waiting_for_call_creation',
                    },
                    {
                        'call_id': '3',
                        'scenario_name': 'scenario_1',
                        'status': 'telephony_error',
                    },
                ],
                'not_found_call_ids': [],
            },
        ),
        ({'call_ids': ['4']}, {'calls_info': [], 'not_found_call_ids': ['4']}),
    ],
    ids=['greenflow', 'nonexistent call_id'],
)
async def test_calls_status(
        # ---- fixtures ----
        taxi_eats_robocall,
        # ---- parameters ----
        request_body,
        expected_response_body,
):
    response = await taxi_eats_robocall.post(
        '/internal/eats-robocall/v1/get-calls-status', json=request_body,
    )

    assert response.json() == expected_response_body


@pytest.mark.pgsql(
    'eats_robocall', files=['add_call_with_unparsable_status.sql'],
)
@pytest.mark.parametrize(
    'request_body, expected_response_code',
    [({'call_ids': ['100500']}, 500)],
    ids=['error flow'],
)
async def test_calls_unparsable_status(
        # ---- fixtures ----
        taxi_eats_robocall,
        # ---- parameters ----
        request_body,
        expected_response_code,
):
    response = await taxi_eats_robocall.post(
        '/internal/eats-robocall/v1/get-calls-status', json=request_body,
    )

    assert response.status_code == expected_response_code
