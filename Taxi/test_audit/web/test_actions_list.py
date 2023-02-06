import pytest


SYSTEM_1_ACTION_1 = {
    'action': 'system_1_action_1',
    'title': 'system_1_action_1',
    'system_name': 'system_1',
}
SYSTEM_1_ACTION_2 = {
    'action': 'system_1_action_2',
    'title': 'system_1_action_2',
    'system_name': 'system_1',
}
SYSTEM_2_ACTION_1 = {
    'action': 'system_2_action_1',
    'title': 'system_2_action_1',
    'system_name': 'system_2',
}


@pytest.mark.parametrize(
    'data, expected_data, status',
    [
        (
            {},
            {
                'actions': [
                    SYSTEM_1_ACTION_1,
                    SYSTEM_1_ACTION_2,
                    SYSTEM_2_ACTION_1,
                ],
            },
            200,
        ),
        (
            {'limit': 1},
            {
                'actions': [SYSTEM_1_ACTION_1],
                'cursor': {'action': 'system_1_action_1'},
            },
            200,
        ),
        (
            {'filters': {'system_name': 'system_1'}},
            {'actions': [SYSTEM_1_ACTION_1, SYSTEM_1_ACTION_2]},
            200,
        ),
        (
            {
                'filters': {
                    'system_name': 'system_1',
                    'action_name_part': 'action_2',
                },
            },
            {'actions': [SYSTEM_1_ACTION_2]},
            200,
        ),
        (
            {'filters': {'system_name': 'system_2'}},
            {'actions': [SYSTEM_2_ACTION_1]},
            200,
        ),
        (
            {
                'filters': {
                    'system_name': 'system_2',
                    'action_name_part': 'action_2',
                },
            },
            {'actions': []},
            200,
        ),
        (
            {'filters': {'action_name_part': 'action_1'}},
            {'actions': [SYSTEM_1_ACTION_1, SYSTEM_2_ACTION_1]},
            200,
        ),
        (
            {
                'filters': {'system_name': 'system_1'},
                'cursor': {'action': 'system_1_action_1'},
            },
            {'actions': [SYSTEM_1_ACTION_2]},
            200,
        ),
        ({'filters': {'system_name': 'system_3'}}, {'actions': []}, 200),
    ],
)
@pytest.mark.pgsql('audit_events', files=['test_actions_list.sql'])
async def test_actions_list_response(
        web_app_client, data, expected_data, status,
):
    response = await web_app_client.request(
        'POST',
        f'/v1/client/actions/retrieve/',
        json=data,
        params={},
        headers={},
    )
    assert response.status == status
    response_json = await response.json()
    assert response_json == expected_data
