import pytest


@pytest.mark.pgsql(
    'eats_moderation', files=['pg_eats_moderation_happy_path.sql'],
)
async def test_internal_moderator_post_happy_path(
        taxi_eats_moderation,
        get_moderation_task,
        get_moderation,
        get_moderator,
):

    task_id = '123'

    response = await taxi_eats_moderation.post(
        '/internal/v1/moderator',
        json={'task_id': task_id, 'context': {'moderator_id': 'moderator'}},
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
    assert moderation[0]['payload_id'] == 1
    assert moderation[0]['status'] == 'process'
    assert moderation[0]['moderator_id']
    assert moderation[0]['created_at']
    assert not moderation[0]['tag']
    assert not moderation[0]['reasons']
    moderator_id = moderation[0]['moderator_id']
    moderator = get_moderator(moderator_id)
    assert moderator['moderator_id'] == moderator_id
    assert moderator['moderator_context'] == '{"moderator_id":"moderator"}'


@pytest.mark.pgsql(
    'eats_moderation', files=['pg_eats_moderation_with_tag.sql'],
)
async def test_internal_moderator_post_with_tag(
        taxi_eats_moderation,
        get_moderation_task,
        get_moderation,
        get_moderator,
):

    task_id = '123'

    response = await taxi_eats_moderation.post(
        '/internal/v1/moderator',
        json={'task_id': task_id, 'context': {'moderator_id': 'moderator'}},
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
    assert moderation[0]['payload_id'] == 1
    assert moderation[0]['status'] == 'process'
    assert moderation[0]['moderator_id']
    assert moderation[0]['created_at']
    assert moderation[0]['tag'] == '456'
    assert not moderation[0]['reasons']
    moderator_id = moderation[0]['moderator_id']
    moderator = get_moderator(moderator_id)
    assert moderator['moderator_id'] == moderator_id
    assert moderator['moderator_context'] == '{"moderator_id":"moderator"}'


async def test_internal_moderator_post_404(
        taxi_eats_moderation, get_moderation_task,
):
    task_id = '123'

    response = await taxi_eats_moderation.post(
        '/internal/v1/moderator',
        json={'task_id': task_id, 'context': {'moderator_id': 'moderator'}},
    )

    assert response.status_code == 404
