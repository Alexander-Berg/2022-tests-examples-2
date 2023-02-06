import copy

import pytest


DEFAULT_BODY = {
    'messages': [
        {'text': 'Авария', 'message_timestamp': '2017-12-11T18:08:56+0300'},
    ],
    'chat_data': {'locale': 'ru', 'chat_type': 'driver_support'},
    'scenario_context': {},
}

SUPPORT_SCENARIOS_KEYSET = {
    'scenarios.yes': {'ru': 'Да'},
    'scenarios.no': {'ru': 'Нет'},
    'text1': {'ru': 'боже как же я хорош'},
    'text2': {'ru': 'текст2'},
}

ALWAYS_TRUE_CONDITION = {
    'init': {'predicates': [{'init': {}, 'type': 'true'}]},
    'type': 'all_of',
}


def insert_condition(cursor, action_id, conditions):
    action_conditions = str(conditions).replace('\'', '"')
    cursor.execute(
        'UPDATE scenarios.action '
        f'SET conditions=\'{action_conditions}\'::jsonb '
        f'WHERE id = \'{action_id}\'',
    )


@pytest.mark.translations(support_scenarios=SUPPORT_SCENARIOS_KEYSET)
@pytest.mark.parametrize(
    ['body', 'action_conditions', 'expected_result'],
    [
        (
            DEFAULT_BODY,
            ALWAYS_TRUE_CONDITION,
            {
                'actions': [
                    {
                        'id': 'action_1',
                        'content': {
                            'items': [
                                {
                                    'id': 'action_2',
                                    'view': {'title': 'Да'},
                                    'params': {
                                        'style': 'italic',
                                        'text': 'Да',
                                    },
                                    'type': 'text',
                                },
                                {
                                    'id': 'action_3',
                                    'view': {'title': 'Нет'},
                                    'params': {'style': 'italic'},
                                    'type': 'call',
                                },
                            ],
                            'text': 'боже как же я хорош',
                        },
                        'type': 'questionary',
                    },
                ],
                'view': {'show_message_input': False},
            },
        ),
        (
            DEFAULT_BODY,
            {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'set': ['moscow', 'spb'],
                                'arg_name': 'text',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                    ],
                },
                'type': 'all_of',
            },
            {'actions': [], 'view': {'show_message_input': True}},
        ),
        (
            DEFAULT_BODY,
            {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'set': ['Авария', 'spb'],
                                'arg_name': 'text',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                    ],
                },
                'type': 'all_of',
            },
            {
                'actions': [
                    {
                        'id': 'action_1',
                        'content': {
                            'items': [
                                {
                                    'id': 'action_2',
                                    'view': {'title': 'Да'},
                                    'params': {
                                        'style': 'italic',
                                        'text': 'Да',
                                    },
                                    'type': 'text',
                                },
                                {
                                    'id': 'action_3',
                                    'view': {'title': 'Нет'},
                                    'params': {'style': 'italic'},
                                    'type': 'call',
                                },
                            ],
                            'text': 'боже как же я хорош',
                        },
                        'type': 'questionary',
                    },
                ],
                'view': {'show_message_input': False},
            },
        ),
        (
            {
                'messages': [],
                'chat_data': {'locale': 'ru', 'chat_type': 'driver_support'},
                'scenario_context': {'last_id': None},
            },
            {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'predicate': {
                                    'init': {
                                        'predicates': [
                                            {
                                                'init': {'arg_name': 'text'},
                                                'type': 'not_null',
                                            },
                                        ],
                                    },
                                    'type': 'all_of',
                                },
                            },
                            'type': 'not',
                        },
                    ],
                },
                'type': 'all_of',
            },
            {
                'actions': [
                    {
                        'id': 'action_1',
                        'content': {
                            'items': [
                                {
                                    'id': 'action_2',
                                    'view': {'title': 'Да'},
                                    'params': {
                                        'style': 'italic',
                                        'text': 'Да',
                                    },
                                    'type': 'text',
                                },
                                {
                                    'id': 'action_3',
                                    'view': {'title': 'Нет'},
                                    'params': {'style': 'italic'},
                                    'type': 'call',
                                },
                            ],
                            'text': 'боже как же я хорош',
                        },
                        'type': 'questionary',
                    },
                ],
                'view': {'show_message_input': False},
            },
        ),
    ],
)
async def test_match_action_without_context(
        taxi_support_scenarios,
        pgsql,
        body,
        action_conditions,
        expected_result,
):
    cursor = pgsql['support_scenarios'].cursor()
    insert_condition(
        cursor=cursor, action_id='action_1', conditions=action_conditions,
    )

    response = await taxi_support_scenarios.post('v1/actions/match', json=body)
    assert response.status_code == 200

    assert response.json() == expected_result


@pytest.mark.translations(support_scenarios=SUPPORT_SCENARIOS_KEYSET)
@pytest.mark.parametrize(
    ['body', 'action_conditions', 'expected_result'],
    [
        (
            DEFAULT_BODY,
            {
                'init': {'predicates': [{'init': {}, 'type': 'false'}]},
                'type': 'all_of',
            },
            {
                'actions': [
                    {
                        'id': 'action_2',
                        'content': {
                            'items': [
                                {
                                    'id': 'action_3',
                                    'view': {'title': 'Да'},
                                    'params': {'style': 'italic'},
                                    'type': 'call',
                                },
                            ],
                            'text': 'текст2',
                        },
                        'type': 'questionary',
                    },
                ],
                'view': {'show_message_input': True},
            },
        ),
    ],
)
async def test_match_action_with_last_id(
        taxi_support_scenarios,
        pgsql,
        body,
        action_conditions,
        expected_result,
):
    body = copy.deepcopy(DEFAULT_BODY)
    body['scenario_context']['last_action_id'] = 'action_1'
    body['scenario_context']['next_action_id'] = 'action_2'
    cursor = pgsql['support_scenarios'].cursor()
    insert_condition(
        cursor=cursor, action_id='action_4', conditions=action_conditions,
    )
    response = await taxi_support_scenarios.post('v1/actions/match', json=body)
    assert response.status_code == 200

    assert response.json() == expected_result


@pytest.mark.translations(support_scenarios=SUPPORT_SCENARIOS_KEYSET)
async def test_match_with_common_action(taxi_support_scenarios, pgsql):
    body = copy.deepcopy(DEFAULT_BODY)
    body['scenario_context']['last_action_id'] = 'action_1'
    body['scenario_context']['next_action_id'] = 'action_2'
    cursor = pgsql['support_scenarios'].cursor()

    insert_condition(
        cursor=cursor,
        action_id='always_merge_action_6',
        conditions=ALWAYS_TRUE_CONDITION,
    )
    response = await taxi_support_scenarios.post('v1/actions/match', json=body)
    assert response.status_code == 200
    resp = response.json()

    assert ['action_2', 'always_merge_action_6'] == [
        action['id'] for action in resp['actions']
    ]
    assert {'show_message_input': False} == resp['view']


async def test_match_with_missing_translations(taxi_support_scenarios, pgsql):
    cursor = pgsql['support_scenarios'].cursor()
    insert_condition(
        cursor=cursor, action_id='action_1', conditions=ALWAYS_TRUE_CONDITION,
    )
    response = await taxi_support_scenarios.post(
        'v1/actions/match', json=DEFAULT_BODY,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'not_found',
        'message': 'Translation [support_scenarios][text1]',
    }
