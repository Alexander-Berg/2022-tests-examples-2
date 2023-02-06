import pytest


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['default.sql', 'data.sql']),
]


def _get_json_node(
        action: dict = None,
        title: str = 'node',
        type_: str = 'response',
        counter: int = 1,
        tag: str = 'tag1',
):
    action = action or {'type': 'response', 'texts': ['text']}
    return {
        'id': '1',
        'title': title,
        'version': '1',
        'type': type_,
        'action': action,
        'meta': {'x': 0, 'y': 0},
        'tags': [{'id': '0', 'slug': tag}],
        'counter': counter,
    }


@pytest.mark.parametrize(
    ('invalid_params', 'valid_params'),
    [
        ({'title': ''}, {'title': 'Title'}),
        ({'counter': 0}, {'counter': 1}),
        ({'tag': 'totalchest'}, {'tag': 'tag1'}),
    ],
)
async def test_validate_node(web_app_client, invalid_params, valid_params):
    response = await web_app_client.post(
        '/v2/scenarios/node/validate?user_id=1&project_slug=ya_lavka',
        json=_get_json_node(**invalid_params),
    )
    assert response.status == 200

    response_json = await response.json()
    assert not response_json['is_valid']

    response = await web_app_client.post(
        '/v2/scenarios/node/validate?user_id=1&project_slug=ya_lavka',
        json=_get_json_node(**valid_params),
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['is_valid']


@pytest.mark.parametrize(
    ('type_', 'action', 'is_valid'),
    [
        (
            'response',
            {'type': 'response', 'texts': ['{feature1}'], 'buttons': ['9']},
            True,
        ),
        ('response', {'type': 'response', 'texts': ['   ', '456']}, False),
        (
            'response',
            {'type': 'response', 'texts': ['456'], 'buttons': ['   ', '123']},
            False,
        ),
        ('response', {'type': 'response', 'texts': ['{totalchest}']}, False),
        (
            'condition',
            {'type': 'condition', 'predicate': 'feature1 = 123'},
            True,
        ),
        (
            'condition',
            {'type': 'condition', 'predicate': 'sure_topic is \'qwerty\''},
            True,
        ),
        (
            'condition',
            {'type': 'condition', 'predicate': 'totalchest is \'best\''},
            False,
        ),
        (
            'condition',
            {'type': 'condition', 'predicate': 'feature1 = '},
            False,
        ),
        (
            'condition',
            {
                'type': 'condition',
                'predicate': {
                    'predicates': [
                        {
                            'is_active': True,
                            'type': 'form',
                            'form_predicate': [
                                {
                                    'feature': 'feature1',
                                    'operator': '=',
                                    'value': '10',
                                },
                            ],
                        },
                    ],
                },
            },
            True,
        ),
        (
            'condition',
            {
                'type': 'condition',
                'predicate': {
                    'predicates': [
                        {
                            'is_active': True,
                            'type': 'form',
                            'form_predicate': [
                                {
                                    'feature': 'feature1',
                                    'operator': '=',
                                    'value': '',
                                },
                            ],
                        },
                    ],
                },
            },
            False,
        ),
        (
            'condition',
            {
                'type': 'condition',
                'predicate': {
                    'predicates': [
                        {
                            'is_active': True,
                            'type': 'form',
                            'form_predicate': [
                                {
                                    'feature': 'totalchest',
                                    'operator': '=',
                                    'value': 'best',
                                },
                            ],
                        },
                    ],
                },
            },
            False,
        ),
        (
            'condition',
            {
                'type': 'condition',
                'predicate': {
                    'predicates': [
                        {
                            'is_active': True,
                            'type': 'code',
                            'code_predicate': 'feature1 = \'day\'',
                        },
                    ],
                },
            },
            True,
        ),
        (
            'condition',
            {
                'type': 'condition',
                'predicate': {
                    'predicates': [
                        {
                            'is_active': True,
                            'type': 'code',
                            'code_predicate': 'feature1 = \'day\')',
                        },
                    ],
                },
            },
            False,
        ),
        (
            'action',
            {
                'type': 'change_state',
                'features': [{'key': 'feature1', 'value': '10'}],
            },
            True,
        ),
        ('action', {'type': 'change_state', 'features': []}, False),
        (
            'action',
            {
                'type': 'change_state',
                'features': [{'key': 'feature1', 'value': '  '}],
            },
            False,
        ),
        (
            'action',
            {'type': 'change_state', 'features': [{'key': 'a', 'value': '1'}]},
            False,
        ),
        (
            'action',
            {
                'type': 'change_state',
                'features': [{'key': 'last_user_message', 'value': 'xxx'}],
            },
            False,
        ),
        (
            'action',
            {'type': 'custom', 'action_type': 'ev', 'parameters': {'a': 'b'}},
            True,
        ),
        (
            'action',
            {'type': 'custom', 'action_type': '', 'parameters': {}},
            False,
        ),
        (
            'action',
            {
                'type': 'integration_action',
                'integration_id': '1',
                'version': '1',
            },
            True,
        ),
        (
            'action',
            {
                'type': 'integration_action',
                'integration_id': '2',
                'version': '1',
                'parameters': {'param1': '1', 'param2': '2'},
            },
            True,
        ),
        (
            'action',
            {
                'type': 'integration_action',
                'integration_id': '  ',
                'version': '1',
            },
            False,
        ),
        (
            'action',
            {
                'type': 'integration_action',
                'integration_id': '2',
                'version': '  ',
            },
            False,
        ),
        (
            'action',
            {
                'type': 'integration_action',
                'integration_id': '2',
                'version': '1',
                'parameters': {'param1': '1', 'param2': ''},
            },
            False,
        ),
        (
            'select_scenario',
            {'type': 'select_scenario', 'scenarios': ['123']},
            True,
        ),
        ('select_scenario', {'type': 'select_scenario'}, False),
        (
            'select_scenario',
            {'type': 'select_scenario', 'scenarios': []},
            False,
        ),
        ('operator', {'type': 'operator', 'forward_line': '12345'}, False),
        ('operator', {'type': 'operator', 'forward_line': 'line1'}, True),
    ],
)
async def test_validate_action(web_app_client, type_, action, is_valid):
    response = await web_app_client.post(
        '/v2/scenarios/node/validate?user_id=1&project_slug=ya_lavka',
        json=_get_json_node(type_=type_, action=action),
    )

    assert response.status == 200

    response_json = await response.json()
    assert response_json['is_valid'] == is_valid
