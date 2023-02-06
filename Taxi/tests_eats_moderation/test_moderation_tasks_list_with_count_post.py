import pytest


def make_item(
        task_id,
        status,
        queue,
        data,
        moderator_context,
        context='',
        reasons=None,
):
    if not reasons:
        reasons = []
    return {
        'task_id': task_id,
        'status': status,
        'payload': ('{"data":"' + data + '"}'),
        'reasons': reasons,
        'moderator_context': moderator_context,
        'context': context,
        'queue': queue,
    }


def make_item_a(
        task_id, status, queue, data, adata, moderator_context, context='',
):
    return {
        'task_id': task_id,
        'status': status,
        'payload': ('{"data":"' + data + '"}'),
        'actual_payload': ('{"data":"' + adata + '"}'),
        'reasons': [],
        'moderator_context': moderator_context,
        'context': context,
        'queue': queue,
    }


def make_history(status, queue, data, moderator):
    return {
        'status': status,
        'payload': ('{"data":"' + data + '"}'),
        'reasons': [],
        'moderator_context': moderator,
    }


def make_item_history(
        task_id, status, queue, data, moderator_context, history, context='',
):
    return {
        'task_id': task_id,
        'status': status,
        'payload': ('{"data":"' + data + '"}'),
        'reasons': [],
        'moderator_context': moderator_context,
        'context': context,
        'history': history,
        'queue': queue,
    }


def make_item_history_a(
        task_id,
        status,
        queue,
        data,
        adata,
        moderator_context,
        history,
        context='',
):
    return {
        'task_id': task_id,
        'status': status,
        'payload': ('{"data":"' + data + '"}'),
        'actual_payload': ('{"data":"' + adata + '"}'),
        'reasons': [],
        'moderator_context': moderator_context,
        'context': context,
        'history': history,
        'queue': queue,
    }


@pytest.mark.parametrize(
    ' etalon_request, etalon_response, status',
    [
        pytest.param(
            {'with_count': True},
            {'count': 0, 'items': []},
            200,
            id='empty db',
        ),
        pytest.param(
            {'with_count': True},
            {
                'count': 1,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
            {'with_count': True},
            {
                'count': 1,
                'items': [
                    make_item_a(
                        '123',
                        'approved',
                        'restapp_moderation_hero',
                        'qwerty',
                        'ytrewq',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
            {'with_count': True, 'with_history': True},
            {
                'count': 1,
                'items': [
                    make_item_history(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        [
                            make_history(
                                'process',
                                'restapp_moderation_hero',
                                'qwerty',
                                'Petrov',
                            ),
                        ],
                        '{"place_id":1234567}',
                    ),
                ],
            },
            200,
            id='one task with history',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {'with_count': True, 'with_history': True},
            {
                'count': 1,
                'items': [
                    make_item_history_a(
                        '123',
                        'approved',
                        'restapp_moderation_hero',
                        'qwerty',
                        'ytrewq',
                        'Petrov',
                        [
                            make_history(
                                'approved',
                                'restapp_moderation_hero',
                                'ytrewq',
                                'Petrov',
                            ),
                            make_history(
                                'process',
                                'restapp_moderation_hero',
                                'qwerty',
                                'Petrov',
                            ),
                        ],
                        '{"place_id":1234567}',
                    ),
                ],
            },
            200,
            id='one task, two payload with history',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_two_payload.sql'],
                ),
            ),
        ),
        pytest.param(
            {'with_count': True, 'with_history': True},
            {
                'count': 1,
                'items': [
                    make_item_history_a(
                        '123',
                        'approved',
                        'restapp_moderation_hero',
                        'qwerty',
                        'ytrewq',
                        'Petrov',
                        [
                            make_history(
                                'approved',
                                'restapp_moderation_hero',
                                'ytrewq',
                                'Petrov',
                            ),
                            make_history(
                                'approved',
                                'restapp_moderation_menu',
                                'asdfgh',
                                'Ivanov',
                            ),
                            make_history(
                                'process',
                                'restapp_moderation_hero',
                                'qwerty',
                                'Petrov',
                            ),
                        ],
                        '{"place_id":1234567}',
                    ),
                ],
            },
            200,
            id='one task, three payloads with history',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_three_payload.sql'],
                ),
            ),
        ),
        pytest.param(
            {'with_count': True},
            {
                'count': 2,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                    make_item(
                        '456',
                        'process',
                        'restapp_moderation_hero',
                        'ytrewq',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
            {'with_count': True, 'with_history': True},
            {
                'count': 2,
                'items': [
                    make_item_history(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        [
                            make_history(
                                'process',
                                'restapp_moderation_hero',
                                'qwerty',
                                'Petrov',
                            ),
                        ],
                        '{"place_id":1234567}',
                    ),
                    make_item_history(
                        '456',
                        'process',
                        'restapp_moderation_hero',
                        'ytrewq',
                        'Petrov',
                        [
                            make_history(
                                'process',
                                'restapp_moderation_hero',
                                'ytrewq',
                                'Petrov',
                            ),
                        ],
                        '{"place_id":1234567}',
                    ),
                ],
            },
            200,
            id='two task with history',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_two_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'with_count': True,
                'scope': ['eda'],
                'queue': ['restapp_moderation_hero'],
            },
            {
                'count': 2,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                    make_item(
                        '456',
                        'process',
                        'restapp_moderation_hero',
                        'ytrewq',
                        'Ivanov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
            {'with_count': True, 'moderator_contexts': ['Ivanov']},
            {
                'count': 2,
                'items': [
                    make_item(
                        '456',
                        'process',
                        'restapp_moderation_hero',
                        'ytrewq',
                        'Ivanov',
                        '{"place_id":1234567}',
                    ),
                    make_item(
                        '789',
                        'process',
                        'restapp_moderation_menu',
                        'asdfgh',
                        'Ivanov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
                'with_count': True,
                'moderator_contexts': ['Ivanov'],
                'pagination': {'limit': 1, 'after': '456'},
            },
            {
                'count': 2,
                'items': [
                    make_item(
                        '789',
                        'process',
                        'restapp_moderation_menu',
                        'asdfgh',
                        'Ivanov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
            200,
            id='four task, one result, one moderator+pagination',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_four_task.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'with_count': True,
                'context': [{'field': 'place_id', 'value': '1234567'}],
            },
            {
                'count': 2,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                    make_item(
                        '789',
                        'process',
                        'restapp_moderation_menu',
                        'asdfgh',
                        'Ivanov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
            {'with_count': True, 'statuses': ['process']},
            {
                'count': 1,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
            {
                'with_count': True,
                'statuses': ['approve'],
                'with_history': True,
            },
            {
                'count': 1,
                'items': [
                    make_item_history(
                        '456',
                        'approve',
                        'restapp_moderation_hero',
                        'ytrewq',
                        'Petrov',
                        [
                            make_history(
                                'approve',
                                'restapp_moderation_hero',
                                'ytrewq',
                                'Petrov',
                            ),
                            make_history(
                                'process',
                                'restapp_moderation_hero',
                                'ytrewq',
                                'Petrov',
                            ),
                        ],
                        '{"place_id":1234567}',
                    ),
                ],
            },
            200,
            id='two task, one result, status with history',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_two_task_three_moderation.sql'],
                ),
            ),
        ),
        pytest.param(
            {'with_count': True, 'moderator_contexts': ['Petrov']},
            {'count': 0, 'items': []},
            200,
            id='status 200, one moderator',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task_no_moderator.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'with_count': True,
                'context': [{'field': 'place_id', 'value': '1234567'}],
                'queue': ['restapp_moderation_menu'],
            },
            {'count': 0, 'items': []},
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
                'with_count': True,
                'context': [{'field': 'place_id', 'value': '1234567'}],
                'moderator_contexts': ['Petrov'],
                'queue': ['restapp_moderation_menu'],
            },
            {'count': 0, 'items': []},
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
                'with_count': True,
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
            {
                'count': 1,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                        [
                            {
                                'reason_code': 'restapp_moderation_hero::1::1',
                                'reason_text': 'reason_text',
                                'reason_title': 'reason_title',
                            },
                        ],
                    ),
                ],
            },
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
                'with_count': True,
                'moderator_contexts': ['Petrov'],
                'reasons': ['reason_title'],
                'statuses': ['process'],
                'queue': ['restapp_moderation_hero'],
                'scope': ['eda'],
            },
            {
                'count': 1,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                        [
                            {
                                'reason_code': 'restapp_moderation_hero::1::1',
                                'reason_text': 'reason_text',
                                'reason_title': 'reason_title',
                            },
                        ],
                    ),
                ],
            },
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
                'with_count': True,
                'reasons': ['reason_title'],
                'statuses': ['process'],
                'queue': ['restapp_moderation_hero'],
                'scope': ['eda'],
            },
            {
                'count': 1,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                        [
                            {
                                'reason_code': 'restapp_moderation_hero::1::1',
                                'reason_text': 'reason_text',
                                'reason_title': 'reason_title',
                            },
                        ],
                    ),
                ],
            },
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
                'with_count': True,
                'statuses': ['process'],
                'queue': ['restapp_moderation_hero'],
                'scope': ['eda'],
            },
            {
                'count': 1,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
            {'with_count': True, 'scope': ['eda']},
            {
                'count': 1,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
                'with_count': True,
                'moderation_period': {
                    'from': '1970-01-01T12:12:12Z',
                    'to': '2500-01-01T12:12:12Z',
                },
            },
            {
                'count': 1,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
                'with_count': True,
                'moderation_period': {
                    'from': '1970-01-01T12:12:12Z',
                    'to': '2000-01-01T12:12:12Z',
                },
            },
            {'count': 0, 'items': []},
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
            {'with_count': True, 'statuses': ['qwerty']},
            {'count': 0, 'items': []},
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
            {'with_count': True, 'moderator_contexts': ['Ivanov', 'Petrov']},
            {
                'count': 4,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                    make_item(
                        '456',
                        'process',
                        'restapp_moderation_hero',
                        'ytrewq',
                        'Ivanov',
                        '{"place_id":1234567}',
                    ),
                    make_item(
                        '789',
                        'process',
                        'restapp_moderation_menu',
                        'asdfgh',
                        'Ivanov',
                        '{"place_id":1234567}',
                    ),
                    make_item(
                        '098',
                        'process',
                        'restapp_moderation_menu',
                        'hgfdsa',
                        'Petrov',
                        '{"place_id":7654321}',
                    ),
                ],
            },
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
            {'with_count': True, 'moderator_contexts': ['Ivanov', 'Petrov']},
            {
                'count': 1,
                'items': [
                    make_item(
                        '123',
                        'process',
                        'restapp_moderation_hero',
                        'qwerty',
                        'Petrov',
                        '{"place_id":1234567}',
                    ),
                ],
            },
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
            {'with_count': True, 'queue': ['undefined'], 'with_history': True},
            {'count': 0, 'items': []},
            200,
            id='status 200, bad filter',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_one_task.sql'],
                ),
            ),
        ),
    ],
)
async def test_moderation_tasks_list_post(
        taxi_eats_moderation, etalon_request, etalon_response, status,
):
    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks/list', json=etalon_request,
    )
    assert response.status_code == status
    if status == 200:
        json = response.json()
        for item in json['items']:
            if 'history' in item:
                for history_moderation in item['history']:
                    assert 'created_at' in history_moderation
                    del history_moderation['created_at']
        assert json == etalon_response
