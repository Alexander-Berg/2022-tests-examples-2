import pytest


@pytest.mark.parametrize(
    ['body', 'expected_row', 'expected_tree'],
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
                'children_edges': [
                    {
                        'id': 'action_1',
                        'trigger_tanker': 'scenarios.yes',
                        'rank': 0,
                    },
                    {
                        'id': 'action_2',
                        'trigger_tanker': 'scenarios.no',
                        'rank': 1,
                    },
                ],
            },
            ('action101', 'Корень', 'tanker', 'call', False, {}, None),
            [
                ('action101', 'action_1', 'scenarios.yes', 0),
                ('action101', 'action_2', 'scenarios.no', 1),
            ],
        ),
        (
            {
                'id': 'string102',
                'text_tanker_key': 'string',
                'client_callback': 'string',
                'show_message_input': True,
                'view_params': {},
                'client_callback_params': {'text': '123'},
                'type': 'buttons_group',
                'is_enabled': True,
                'always_merge': True,
                'conditions': {
                    'init': {'predicates': [{'init': {}, 'type': 'true'}]},
                    'type': 'all_of',
                },
                'parents_edges': [
                    {'id': 'action_3', 'trigger_tanker': 'string', 'rank': 0},
                ],
                'children_edges': [
                    {'id': 'action_1', 'trigger_tanker': 'string', 'rank': 0},
                ],
            },
            (
                'string102',
                None,
                'string',
                'string',
                True,
                {'text': '123'},
                {
                    'init': {'predicates': [{'init': {}, 'type': 'true'}]},
                    'type': 'all_of',
                },
            ),
            [
                ('action_3', 'string102', 'string', 0),
                ('string102', 'action_1', 'string', 0),
            ],
        ),
    ],
)
async def test_create_action(
        taxi_support_scenarios, pgsql, body, expected_row, expected_tree,
):
    response = await taxi_support_scenarios.post('v1/actions/', json=body)
    assert response.status_code == 200

    cursor = pgsql['support_scenarios'].cursor()
    cursor.execute(
        f'SELECT id, description, text_tanker_key, client_callback,'
        f' show_message_input, client_callback_params, conditions'
        f' FROM scenarios.action WHERE id = \'{body["id"]}\'',
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
    assert response.status_code == 200


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
    response = await taxi_support_scenarios.post('v1/actions/', json=body)
    assert response.status_code == expected_code
    assert response.json() == expected_response
