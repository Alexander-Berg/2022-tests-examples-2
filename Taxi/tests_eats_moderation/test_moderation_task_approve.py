import pytest


@pytest.fixture(name='mock_processing', autouse=True)
def _mock_processing(mockserver):
    @mockserver.json_handler(
        '/processing/v1/eda/restapp_moderation_hero/create-event',
    )
    def _create_event(request):

        return mockserver.make_response(status=200, json={'event_id': '123'})

    return _create_event


PAYLOAD_VALUE1 = {
    'data': {
        'context': {'place_id': 1234567},
        'origin_data': {'data': 'qwerty'},
    },
    'kind': 'approve',
}

PAYLOAD_VALUE3 = {
    'data': {
        'context': {'place_id': 1234567},
        'origin_data': {'data': 'asdfgh'},
    },
    'kind': 'approve',
}

PAYLOAD_VALUE4 = {
    'data': {
        'context': {'place_id': 7654321},
        'moderator': 'Petrov',
        'origin_data': ['data1', 'data2'],
    },
    'kind': 'approve',
}


@pytest.mark.parametrize(
    'etalon_request, status, count, proc_request',
    [
        pytest.param(
            {'task_id': '123', 'moderator_context': 'qwerty'},
            404,
            0,
            [],
            id='empty db, task not found',
        ),
        pytest.param(
            {'task_id': '123', 'tag': 'abc', 'moderator_context': 'qwerty'},
            400,
            0,
            [],
            id='tag+task_id',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_tag_task_id.sql'],
                ),
            ),
        ),
        pytest.param(
            {'task_id': '234', 'moderator_context': 'qwerty'},
            404,
            0,
            [],
            id='task by task_id not found',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_task_not_found.sql'],
                ),
            ),
        ),
        pytest.param(
            {'moderator_context': 'qwerty'},
            400,
            0,
            [],
            id='without task_id and tag',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_no_tag_task_id.sql'],
                ),
            ),
        ),
        pytest.param(
            {'tag': '234', 'moderator_context': 'qwerty'},
            404,
            0,
            [],
            id='task by tag not found',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_tag_not_found.sql'],
                ),
            ),
        ),
        pytest.param(
            {'task_id': '123', 'moderator_context': 'Petrov'},
            400,
            0,
            [],
            id='two task, task with tag by task_id',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_two_task_with_tag.sql'],
                ),
            ),
        ),
        pytest.param(
            {'tag': 'abc', 'moderator_context': 'Petrov'},
            204,
            1,
            [PAYLOAD_VALUE1],
            id='two task, task with tag by tag, happy path',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_two_task_happy_path.sql'],
                ),
            ),
        ),
        pytest.param(
            {'task_id': '098', 'moderator_context': 'Petrov'},
            204,
            1,
            [PAYLOAD_VALUE4],
            id='four task, task without tag by task_id, happy_path',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_four_task_happy_path.sql'],
                ),
            ),
        ),
        pytest.param(
            {'tag': 'abc', 'moderator_context': 'Petrov'},
            204,
            2,
            [PAYLOAD_VALUE1, PAYLOAD_VALUE3],
            id='four task, two task approve by tag, happy path',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_approve_by_tag.sql'],
                ),
            ),
        ),
        pytest.param(
            {'tag': 'abc', 'moderator_context': 'Petrov'},
            204,
            1,
            [PAYLOAD_VALUE1],
            id='approve new moderator',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_approve_new_moderator.sql'],
                ),
            ),
        ),
    ],
)
async def test_moderation_task_approve_post(
        taxi_eats_moderation,
        mock_processing,
        etalon_request,
        status,
        count,
        proc_request,
):

    response = await taxi_eats_moderation.post(
        '/moderation/v1/task/approve', json=etalon_request,
    )

    assert response.status_code == status

    assert mock_processing.times_called == count
    for etalon in proc_request:
        assert mock_processing.next_call()['request'].json == etalon


@pytest.mark.parametrize(
    'proc_status, proc_json, ' 'etalon_request, status, count, proc_request',
    [
        pytest.param(
            400,
            {'code': 'invalid_payload', 'message': 'error'},
            {'tag': 'abc', 'moderator_context': 'Petrov'},
            400,
            1,
            [PAYLOAD_VALUE1],
            id='ProcaaS error 400',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_approve_procaas.sql'],
                ),
            ),
        ),
        pytest.param(
            409,
            {'code': 'race_condition', 'message': 'error'},
            {'tag': 'abc', 'moderator_context': 'Petrov'},
            400,
            1,
            [PAYLOAD_VALUE1],
            id='ProcaaS error 409',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_approve_procaas.sql'],
                ),
            ),
        ),
        pytest.param(
            404,
            {'code': 'race_condition', 'message': 'error'},
            {
                'tag': 'abc',
                'moderator_context': 'Petrov',
                'reasons': ['орфография'],
            },
            400,
            1,
            [PAYLOAD_VALUE1],
            id='ProcaaS error 404',
            marks=(
                pytest.mark.pgsql(
                    'eats_moderation',
                    files=['pg_eats_moderation_approve_procaas.sql'],
                ),
            ),
        ),
    ],
)
async def test_moderation_task_approve_proc_error_post(
        taxi_eats_moderation,
        mockserver,
        proc_status,
        proc_json,
        etalon_request,
        status,
        count,
        proc_request,
):
    @mockserver.json_handler(
        '/processing/v1/eda/restapp_moderation_hero/create-event',
    )
    def _create_event(request):

        return mockserver.make_response(status=proc_status, json=proc_json)

    response = await taxi_eats_moderation.post(
        '/moderation/v1/task/approve', json=etalon_request,
    )

    assert response.status_code == status

    assert _create_event.times_called == count
    for etalon in proc_request:
        assert _create_event.next_call()['request'].json == etalon


@pytest.mark.pgsql(
    'eats_moderation',
    files=['pg_eats_moderation_approve_post_without_payload.sql'],
)
async def test_moderation_task_approve_post_without_payload(
        taxi_eats_moderation, remove_payload, mock_processing,
):

    await taxi_eats_moderation.post(
        '/moderation/v1/task/approve',
        json={'tag': 'abc', 'moderator_context': 'Petrov'},
    )

    assert mock_processing.times_called == 1
    assert mock_processing.next_call()['request'].json == {
        'data': {
            'context': {'place_id': 1234567},
            'origin_data': {'data': 'qwerty'},
        },
        'kind': 'approve',
    }

    remove_payload(1)

    response = await taxi_eats_moderation.post(
        '/moderation/v1/task/approve',
        json={'tag': 'abc', 'moderator_context': 'Petrov'},
    )

    assert response.status_code == 400

    assert mock_processing.times_called == 0
