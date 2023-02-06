import json

import pytest


@pytest.mark.servicetest
@pytest.mark.parametrize(
    ['query_params', 'expected_code', 'expected_result'],
    [
        (
            {'action_id': 'action_1'},
            200,
            {
                'always_merge': False,
                'children_edges': [
                    {
                        'id': 'action_2',
                        'rank': 0,
                        'trigger_tanker': 'scenarios.yes',
                    },
                    {
                        'id': 'action_3',
                        'rank': 0,
                        'trigger_tanker': 'scenarios.no',
                    },
                ],
                'parents_edges': [],
                'id': 'action_1',
                'is_enabled': False,
                'view_params': {},
                'client_callback_params': {},
                'show_message_input': False,
                'text_tanker_key': 'text1',
                'client_callback': 'text',
                'type': 'questionary',
            },
        ),
        (
            {'action_id': 'action_11234'},
            404,
            {'code': 'not_found', 'message': 'Action was not found'},
        ),
    ],
)
async def test_get_action_by_id(
        taxi_support_scenarios, query_params, expected_code, expected_result,
):
    response = await taxi_support_scenarios.get(
        'v1/actions/', params=query_params,
    )
    assert response.status_code == expected_code
    assert json.loads(response.content) == expected_result
