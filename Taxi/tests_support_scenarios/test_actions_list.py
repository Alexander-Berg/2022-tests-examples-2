import json

import pytest


@pytest.mark.servicetest
@pytest.mark.parametrize(
    ['query_params', 'expected_result'],
    [
        (
            {'limit': 10},
            {
                'actions': [
                    {'id': 'action_1', 'client_callback': 'text'},
                    {'id': 'action_2', 'client_callback': 'text'},
                    {'id': 'action_3', 'client_callback': 'call'},
                    {
                        'id': 'action_4',
                        'description': 'Описание',
                        'client_callback': 'text',
                    },
                ],
            },
        ),
        (
            {'limit': 1, 'only_root': True},
            {'actions': [{'id': 'action_1', 'client_callback': 'text'}]},
        ),
        (
            {'limit': 1, 'offset': 1, 'only_root': True},
            {
                'actions': [
                    {
                        'id': 'action_4',
                        'description': 'Описание',
                        'client_callback': 'text',
                    },
                ],
            },
        ),
    ],
)
async def test_get_actions_list(
        taxi_support_scenarios, query_params, expected_result,
):
    response = await taxi_support_scenarios.get(
        'v1/actions/list', params=query_params,
    )
    assert response.status_code == 200
    assert json.loads(response.content) == expected_result
