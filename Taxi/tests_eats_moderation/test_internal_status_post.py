import pytest


@pytest.mark.pgsql(
    'eats_moderation', files=['pg_eats_moderation_happy_path.sql'],
)
async def test_internal_status_post_happy_path(
        taxi_eats_moderation,
        get_moderation_task,
        get_moderation,
        get_moderator,
):

    task_id = '123'
    payload_id = 1

    response = await taxi_eats_moderation.post(
        '/internal/v1/status',
        json={
            'task_id': task_id,
            'subject': 'subject',
            'status': 'ml_approve',
            'resolution': 'success',
            'reasons': ['reason1', 'reason2'],
        },
    )

    assert response.status_code == 204
    task = get_moderation_task(task_id)
    assert task['task_id'] == task_id
    assert task['context_id'] == 1
    assert task['payload_id'] == 1
    assert task['created_at']
    assert task['updated_at']
    assert not task['tag']
    moderation = get_moderation(task_id)
    assert moderation[0]['id']
    assert moderation[0]['task_id'] == task_id
    assert moderation[0]['payload_id'] == payload_id
    assert moderation[0]['status'] == 'ml_approve'
    assert moderation[0]['moderator_id']
    assert moderation[0]['created_at']
    assert not moderation[0]['tag']
    assert moderation[0]['reasons'] == [1, 2]
    moderator_id = moderation[0]['moderator_id']
    moderator = get_moderator(moderator_id)
    assert moderator[0] == moderator_id
    assert moderator[1] == 'subject'


@pytest.mark.pgsql(
    'eats_moderation', files=['pg_eats_moderation_with_tag.sql'],
)
async def test_internal_status_post_with_tag(
        taxi_eats_moderation,
        get_moderation_task,
        get_moderation,
        get_moderator,
):

    payload_id = 1
    task_id = '123'

    response = await taxi_eats_moderation.post(
        '/internal/v1/status',
        json={
            'task_id': task_id,
            'subject': 'subject',
            'status': 'ml_approve',
            'resolution': 'success',
            'reasons': ['reason1', 'reason2'],
        },
    )

    assert response.status_code == 204
    task = get_moderation_task(task_id)
    assert task['task_id'] == task_id
    assert task['context_id'] == 1
    assert task['payload_id'] == 1
    assert task['created_at']
    assert task['updated_at']
    assert task['tag'] == '456'
    moderation = get_moderation(task_id)
    assert moderation[0]['id']
    assert moderation[0]['task_id'] == task_id
    assert moderation[0]['payload_id'] == payload_id
    assert moderation[0]['status'] == 'ml_approve'
    assert moderation[0]['moderator_id']
    assert moderation[0]['created_at']
    assert moderation[0]['tag'] == '456'
    assert moderation[0]['reasons'] == [1, 2]
    moderator_id = moderation[0]['moderator_id']
    moderator = get_moderator(moderator_id)
    assert moderator['moderator_id'] == moderator_id
    assert moderator['moderator_context'] == 'subject'


async def test_internal_status_post_404(
        taxi_eats_moderation, get_moderation_task,
):
    task_id = '123'

    response = await taxi_eats_moderation.post(
        '/internal/v1/status',
        json={
            'task_id': task_id,
            'subject': 'subject',
            'status': 'ml_approve',
            'resolution': 'approve',
            'reasons': ['reason1', 'reason2'],
        },
    )

    assert response.status_code == 404


@pytest.mark.pgsql(
    'eats_moderation', files=['pg_eats_moderation_old_moderation.sql'],
)
async def test_internal_status_post_old_moderation(
        taxi_eats_moderation,
        get_moderation_task,
        get_moderation,
        get_moderator,
):

    payload_id = 1
    moderator_id = 1
    moderation_id = 'qwerty'
    task_id = '123'

    response = await taxi_eats_moderation.post(
        '/internal/v1/status',
        json={
            'task_id': task_id,
            'subject': 'subject',
            'status': 'ml_approve',
            'resolution': 'success',
            'reasons': ['reason1', 'reason2'],
        },
    )

    assert response.status_code == 204
    task = get_moderation_task(task_id)
    assert task['task_id'] == task_id
    assert task['context_id'] == 1
    assert task['payload_id'] == 1
    assert task['created_at']
    assert task['updated_at']
    assert not task['tag']
    moderation = get_moderation(task_id)
    assert moderation[0]['id'] == moderation_id
    assert moderation[0]['task_id'] == task_id
    assert moderation[0]['payload_id'] == payload_id
    assert moderation[0]['status'] == 'ml_process'
    assert moderation[0]['moderator_id'] == moderator_id
    assert moderation[0]['created_at']
    assert not moderation[0]['tag']
    assert moderation[0]['reasons'] == []

    assert moderation[1]['id']
    assert moderation[1]['task_id'] == task_id
    assert moderation[1]['payload_id'] == payload_id
    assert moderation[1]['status'] == 'ml_approve'
    assert moderation[1]['moderator_id']
    assert moderation[1]['created_at']
    assert not moderation[1]['tag']
    assert moderation[1]['reasons'] == [1, 2]
    moderator_id2 = moderation[1][4]
    moderator = get_moderator(moderator_id2)
    assert moderator['moderator_id'] == moderator_id2
    assert moderator['moderator_context'] == 'subject'


@pytest.mark.pgsql(
    'eats_moderation', files=['pg_eats_moderation_old_moderator.sql'],
)
async def test_internal_status_post_old_moderator(
        taxi_eats_moderation,
        get_moderation_task,
        get_moderation,
        get_moderator,
):

    payload_id = 1
    moderator_id = 1
    moderation_id = 'qwerty'
    task_id = '123'

    response = await taxi_eats_moderation.post(
        '/internal/v1/status',
        json={
            'task_id': task_id,
            'subject': 'subject',
            'status': 'ml_approve',
            'resolution': 'success',
            'reasons': ['reason1', 'reason2'],
        },
    )

    assert response.status_code == 204
    task = get_moderation_task(task_id)
    assert task['task_id'] == task_id
    assert task['context_id'] == 1
    assert task['payload_id'] == 1
    assert task['created_at']
    assert task['updated_at']
    assert not task['tag']
    moderation = get_moderation(task_id)
    assert moderation[0]['id'] == moderation_id
    assert moderation[0]['task_id'] == task_id
    assert moderation[0]['payload_id'] == payload_id
    assert moderation[0]['status'] == 'ml_process'
    assert moderation[0]['moderator_id'] == moderator_id
    assert moderation[0]['created_at']
    assert not moderation[0]['tag']
    assert moderation[0]['reasons'] == []

    assert moderation[1]['id']
    assert moderation[1]['task_id'] == task_id
    assert moderation[1]['payload_id'] == payload_id
    assert moderation[1]['status'] == 'ml_approve'
    assert moderation[1]['moderator_id'] == moderator_id
    assert moderation[1]['created_at']
    assert not moderation[1]['tag']
    assert moderation[1]['reasons'] == [1, 2]

    moderator = get_moderator(moderator_id)
    assert moderator['moderator_id'] == moderator_id
    assert moderator['moderator_context'] == 'subject'
