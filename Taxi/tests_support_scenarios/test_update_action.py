import pytest


@pytest.mark.parametrize(
    ['body', 'expected_result', 'expected_row', 'expected_tree'],
    [
        (
            {
                'id': 'action_1',
                'show_message_input': True,
                'text_tanker_key': 'text',
                'client_callback': 'text',
                'description': 'Корень',
                'type': 'buttons_group',
                'is_enabled': True,
                'always_merge': True,
                'parents_edges': [
                    {
                        'id': 'action_2',
                        'trigger_tanker': 'scenarios.no',
                        'rank': 0,
                    },
                ],
                'view_params': {'theme': 'warning'},
                'client_callback_params': {'text': 'aaa'},
                'children_edges': [
                    {
                        'id': 'action_3',
                        'trigger_tanker': 'scenarios.yes',
                        'rank': 0,
                    },
                ],
            },
            {
                'id': 'action_1',
                'show_message_input': True,
                'text_tanker_key': 'text',
                'client_callback': 'text',
                'description': 'Корень',
                'type': 'buttons_group',
                'is_enabled': True,
                'always_merge': True,
                'parents_edges': [
                    {
                        'id': 'action_2',
                        'trigger_tanker': 'scenarios.no',
                        'rank': 0,
                    },
                ],
                'view_params': {'theme': 'warning'},
                'client_callback_params': {'text': 'aaa'},
                'children_edges': [
                    {
                        'id': 'action_3',
                        'trigger_tanker': 'scenarios.yes',
                        'rank': 0,
                    },
                ],
            },
            (
                'action_1',
                'Корень',
                'text',
                'text',
                True,
                {'text': 'aaa'},
                None,
                'buttons_group',
                True,
                True,
                {'theme': 'warning'},
            ),
            [
                ('action_2', 'action_1', 'scenarios.no', 0),
                ('action_1', 'action_3', 'scenarios.yes', 0),
            ],
        ),
    ],
)
async def test_update_action(
        taxi_support_scenarios,
        pgsql,
        body,
        expected_result,
        expected_row,
        expected_tree,
):
    response = await taxi_support_scenarios.put('v1/actions/', json=body)
    assert response.status_code == 200
    assert response.json() == expected_result
    cursor = pgsql['support_scenarios'].cursor()
    cursor.execute(
        f'SELECT * FROM scenarios.action WHERE id = \'{body["id"]}\'',
    )
    row = list(row for row in cursor)[0]
    cursor.execute(
        'SELECT * FROM scenarios.actions_tree '
        f'WHERE parent_id = \'{body["id"]}\' OR child_id = \'{body["id"]}\'',
    )
    edges = list(edge for edge in cursor)
    cursor.close()
    assert row == expected_row
    assert edges == expected_tree


@pytest.mark.parametrize(
    ['body', 'expected_code', 'expected_response'],
    [
        (
            {
                'id': 'action101',
                'description': 'Корень',
                'text_tanker_key': 'tanker',
                'client_callback': 'call',
                'show_message_input': False,
                'parents_edges': [],
                'view_params': {},
                'client_callback_params': {},
                'type': 'buttons_group',
                'is_enabled': True,
                'always_merge': True,
                'conditions': {
                    'init': {'predicates': [{'init': {}, 'type': 'true'}]},
                    'type': None,
                },
                'children_edges': [],
            },
            400,
            {'code': 'bad_request', 'message': 'Wrong conditions format'},
        ),
    ],
)
async def test_bad_request(
        taxi_support_scenarios, pgsql, body, expected_code, expected_response,
):
    response = await taxi_support_scenarios.put('v1/actions/', json=body)
    assert response.status_code == expected_code
    assert response.json() == expected_response
