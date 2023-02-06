import pytest


@pytest.mark.parametrize(
    'action',
    [
        'close',
        'comment',
        'communicate',
        'external_comment',
        'external_request',
    ],
)
@pytest.mark.parametrize(
    'task_id, comment, expected_status, login',
    [
        ('5b2cae5cb2682a976914c2a1', 'some test inner comment', 422, 'user1'),
        (
            '5b2cae5cb2682a976914c2a2',
            'some test inner comment',
            200,
            'superuser',
        ),
        ('5b2cae5cb2682a976914c2a1', 'comment\n\nmacro_1337', 200, 'user1'),
        ('5a2cae5cb2682a976914c2a1', 'some test inner comment', 200, 'user1'),
    ],
)
@pytest.mark.config(CHATTERBOX_STRICT_COMMENT_LINES=['first'])
async def test_strict_comments(
        mock_chat_get_history,
        patch,
        patch_auth,
        cbox_client,
        task_id,
        comment,
        action,
        expected_status,
        login,
):
    patch_auth(login=login, superuser=True)
    mock_chat_get_history({'messages': []})

    @patch('taxi.clients.support_chat.SupportChatApiClient.add_update')
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    response = await cbox_client.post(
        f'/v1/tasks/{task_id}/{action}',
        json={'comment': comment, 'macro_ids': ['1', '1337']},
    )
    assert response.status == expected_status
