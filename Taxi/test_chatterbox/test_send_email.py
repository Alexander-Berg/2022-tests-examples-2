import datetime

import bson
import pytest

NOW = datetime.datetime(2018, 6, 15, 12, 34)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ('task_id', 'request_body', 'expected_action_history'),
    [
        (
            '5b2cae6662682a976914c2a1',
            {
                'comment': 'text',
                'email_from': 'from@yandex-team.ru',
                'email_to': ['to@yandex-team.ru'],
                'email_subject': 'subject',
            },
            {
                'action': 'send_email',
                'created': NOW,
                'email_from': 'from@yandex-team.ru',
                'email_subject': 'subject',
                'email_to': ['to@yandex-team.ru'],
                'line': 'something_line',
                'login': 'superuser',
            },
        ),
        (
            '5b2cae7772682a976914c2a1',
            {
                'comment': 'text',
                'email_from': 'from@yandex-team.ru',
                'email_to': ['to@yandex-team.ru'],
                'email_subject': 'subject',
                'email_cc': ['cc@yandex-team.ru'],
            },
            {
                'action': 'send_email',
                'created': NOW,
                'email_from': 'from@yandex-team.ru',
                'email_subject': 'subject',
                'email_to': ['to@yandex-team.ru'],
                'line': 'something_line',
                'login': 'superuser',
                'email_cc': ['cc@yandex-team.ru'],
            },
        ),
        (
            '5b2cae8882682a976914c222',
            {
                'comment': 'text',
                'email_from': 'from@yandex-team.ru',
                'email_to': ['to@yandex-team.ru'],
                'email_subject': 'subject',
                'email_cc': ['cc@yandex-team.ru'],
                'attachment_ids': ['1', '2', '3'],
            },
            {
                'action': 'send_email',
                'created': NOW,
                'email_from': 'from@yandex-team.ru',
                'email_subject': 'subject',
                'email_to': ['to@yandex-team.ru'],
                'line': 'something_line',
                'login': 'superuser',
                'email_cc': ['cc@yandex-team.ru'],
            },
        ),
    ],
)
@pytest.mark.config(
    CHATTERBOX_SETTINGS_SEND_EMAIL={
        'something_line': {
            'default_email_from': 'chatterbox@yandex.ru',
            'tracker_queue': 'CHATTERBOX',
        },
    },
)
async def test_send_email(
        cbox,
        task_id,
        request_body,
        expected_action_history,
        mock_st_create_comment,
        mock_st_create_ticket,
):
    await cbox.post(f'/v1/tasks/{task_id}/send_email', data=request_body)
    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id)},
    )
    if task_id == '5b2cae6662682a976914c2a1':
        assert len(mock_st_create_comment.calls) == 1
    elif task_id == '5b2cae7772682a976914c2a1':
        assert len(mock_st_create_comment.calls) == 1
    else:
        assert len(mock_st_create_ticket.calls) == 1
        assert task['tracker_id'] == 'CHATTERBOX-1'
    assert task['history']
    assert task['history'][-1] == expected_action_history
    assert cbox.status == 200
