import pytest


@pytest.mark.parametrize(
    ' etalon_request, etalon_response, status',
    [
        pytest.param({'requests': [{}]}, {'counts': [0]}, 200, id='empty db'),
        pytest.param(
            {'requests': [{}]},
            {'counts': [1]},
            200,
            id='one task',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{}]},
            {'counts': [1]},
            200,
            id='one task, two payload',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_two_payload.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{}]},
            {'counts': [2]},
            200,
            id='two task',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_two_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {'scope': ['eda'], 'queue': ['restapp_moderation_hero']},
                ],
            },
            {'counts': [2]},
            200,
            id='four task, two result, scope+queue',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_four_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{'moderator_contexts': ['Ivanov']}]},
            {'counts': [2]},
            200,
            id='four task, two result, one moderator',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_four_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {'context': [{'field': 'place_id', 'value': '1234567'}]},
                ],
            },
            {'counts': [2]},
            200,
            id='four task, two result, context',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_four_task_filt.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{'statuses': ['process']}]},
            {'counts': [1]},
            200,
            id='two task, one result, status',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_two_task_three_moderation.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{'moderator_contexts': ['Petrov']}]},
            {},
            400,
            id='status 400, one moderator',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_no_moderator.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {
                        'context': [{'field': 'place_id', 'value': '1234567'}],
                        'queue': ['restapp_moderation_menu'],
                    },
                ],
            },
            {'counts': [0]},
            200,
            id='one task, no result',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {
                        'context': [{'field': 'place_id', 'value': '1234567'}],
                        'moderator_contexts': ['Petrov'],
                        'queue': ['restapp_moderation_menu'],
                    },
                ],
            },
            {'counts': [0]},
            200,
            id='two task, no result, two filters',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_two_task_two_moderator.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {
                        'payload': [{'field': 'data', 'value': 'qwerty'}],
                        'context': [{'field': 'place_id', 'value': '1234567'}],
                        'moderator_contexts': ['Petrov'],
                        'reasons': ['reason_title'],
                        'statuses': ['process'],
                        'queue': ['restapp_moderation_hero'],
                        'scope': ['eda'],
                        'add_period': {
                            'from': '1970-01-01T12:12:12Z',
                            'to': '2500-01-01T12:12:12Z',
                        },
                        'moderation_period': {
                            'from': '1970-01-01T12:12:12Z',
                            'to': '2500-01-01T12:12:12Z',
                        },
                    },
                ],
            },
            {'counts': [1]},
            200,
            id='one task, all filters',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_reason.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {
                        'context': [{'field': 'place_id', 'value': '1234567'}],
                        'moderator_contexts': ['Petrov'],
                        'reasons': ['reason_title'],
                        'statuses': ['process'],
                        'queue': ['restapp_moderation_hero'],
                        'scope': ['eda'],
                        'add_period': {
                            'from': '1970-01-01T12:12:12Z',
                            'to': '2500-01-01T12:12:12Z',
                        },
                        'moderation_period': {
                            'from': '1970-01-01T12:12:12Z',
                            'to': '2500-01-01T12:12:12Z',
                        },
                    },
                ],
            },
            {'counts': [1]},
            200,
            id='one task, no payload filter',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_reason.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {
                        'moderator_contexts': ['Petrov'],
                        'reasons': ['reason_title'],
                        'statuses': ['process'],
                        'queue': ['restapp_moderation_hero'],
                        'scope': ['eda'],
                    },
                ],
            },
            {'counts': [1]},
            200,
            id='one task, no context filter',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_reason.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {
                        'reasons': ['reason_title'],
                        'statuses': ['process'],
                        'queue': ['restapp_moderation_hero'],
                        'scope': ['eda'],
                    },
                ],
            },
            {'counts': [1]},
            200,
            id='one task, no context and moderator filter',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_reason.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {
                        'statuses': ['process'],
                        'queue': ['restapp_moderation_hero'],
                        'scope': ['eda'],
                    },
                ],
            },
            {'counts': [1]},
            200,
            id='one task, no context moderator and reasons filter',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{'scope': ['eda']}]},
            {'counts': [1]},
            200,
            id='one task, scope filter',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {
                        'moderation_period': {
                            'from': '1970-01-01T12:12:12Z',
                            'to': '2500-01-01T12:12:12Z',
                        },
                    },
                ],
            },
            {'counts': [1]},
            200,
            id='one task, date filter',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_data.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'requests': [
                    {
                        'moderation_period': {
                            'from': '1970-01-01T12:12:12Z',
                            'to': '2000-01-01T12:12:12Z',
                        },
                    },
                ],
            },
            {'counts': [0]},
            200,
            id='one task, date filter no result',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_data.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{'statuses': ['qwerty']}]},
            {'counts': [0]},
            200,
            id='one task, bad status filter',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{'moderator_contexts': ['Ivanov', 'Petrov']}]},
            {'counts': [4]},
            200,
            id='four task, four result, two moderator',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_four_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{'moderator_contexts': ['Ivanov', 'Petrov']}]},
            {'counts': [1]},
            200,
            id='one task, one result, two moderator',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {'requests': [{'moderator_contexts': ['Petrov', 'Ivanov']}]},
            {},
            400,
            id='status 400, two moderator',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_no_moderator.sql'],
                ),
            ),
        ),
    ],
)
async def test_moderation_tasks_count_post(
        taxi_eats_moderation, etalon_request, etalon_response, status,
):
    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks/count', json=etalon_request,
    )
    assert response.status_code == status
    if status == 200:
        json = response.json()
        assert json == etalon_response
