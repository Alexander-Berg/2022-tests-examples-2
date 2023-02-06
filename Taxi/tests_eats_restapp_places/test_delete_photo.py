async def test_delete_photo_happy_path(taxi_eats_restapp_places, stq):
    response = await taxi_eats_restapp_places.post(
        '/internal/moderation/delete_photo',
        json={'avatarnica_identity': 'fake/identity'},
    )

    assert response.status_code == 202
    assert stq.eats_restapp_places_photo_delete.times_called == 1
    arg = stq.eats_restapp_places_photo_delete.next_call()
    assert arg['queue'] == 'eats_restapp_places_photo_delete'
    assert arg['args'] == []
    assert arg['kwargs']['identity'] == 'fake/identity'


async def test_delete_photo_stq(stq_runner, mock_avatars_delete_200):
    await stq_runner.eats_restapp_places_photo_delete.call(
        task_id='fake_task', kwargs={'identity': 'fake/identity'},
    )

    assert mock_avatars_delete_200.times_called == 1


async def test_delete_photo_stq_202(stq_runner, mock_avatars_delete_202):
    await stq_runner.eats_restapp_places_photo_delete.call(
        task_id='fake_task', kwargs={'identity': 'fake/identity'},
    )

    assert mock_avatars_delete_202.times_called == 1


async def test_delete_photo_stq_404(stq_runner, mock_avatars_delete_404):
    await stq_runner.eats_restapp_places_photo_delete.call(
        task_id='fake_task', kwargs={'identity': 'fake/identity'},
    )

    assert mock_avatars_delete_404.times_called == 1
