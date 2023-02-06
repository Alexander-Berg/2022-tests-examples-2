# pylint: disable=protected-access
import pytest


@pytest.mark.translations(
    chatterbox={
        'email.sent_from': {
            'en': 'Sent from the address',
            'ru': 'Отправлено с адреса',
        },
    },
)
@pytest.mark.parametrize(
    'messages, reply_to, expected_result, locale',
    [
        (
            [
                {
                    'id': 'first_id',
                    'sender': {'id': 'client_login', 'role': 'client'},
                    'text': 'client\nlogin text\n',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
                {
                    'id': 'second_id',
                    'sender': {'id': 'support_login', 'role': 'support'},
                    'text': 'support login\ntext',
                    'metadata': {'created': '2018-05-05T15:35:16'},
                },
                {
                    'id': 'third_id',
                    'sender': {'id': 'client_login', 'role': 'client'},
                    'text': 'client\nlogin\ntext\n',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
                {
                    'id': 'fourth_id',
                    'sender': {'id': 'support_login', 'role': 'support'},
                    'text': 'support login\ntext',
                    'metadata': {'created': '2018-05-05T15:35:16'},
                },
            ],
            ['first_id', 'third_id', 'fourth_id'],
            'Отправлено с адреса: support@email.ru\n'
            '> support login\n'
            '> text\n\n'
            'Отправлено с адреса: client@email.ru\n'
            '> client\n'
            '> login\n'
            '> text\n\n'
            'Отправлено с адреса: client@email.ru\n'
            '> client\n'
            '> login text',
            'ru',
        ),
        (
            [
                {
                    'id': 'first_id',
                    'sender': {'id': 'client_login', 'role': 'client'},
                    'text': 'client\nlogin text\n',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
                {
                    'id': 'fourth_id',
                    'sender': {'id': 'support_login', 'role': 'support'},
                    'text': 'support login\ntext',
                    'metadata': {'created': '2018-05-05T15:35:16'},
                },
            ],
            ['first_id'],
            'Sent from the address: client@email.ru\n'
            '> client\n'
            '> login text',
            'en',
        ),
        (
            [
                {
                    'id': 'first_id',
                    'sender': {'id': 'client_login', 'role': 'client'},
                    'text': 'client\nlogin text\n',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
            ],
            ['first_id'],
            'Sent from the address: client@email.ru\n'
            '> client\n'
            '> login text',
            '',
        ),
        ([], [], None, None),
        (
            [
                {
                    'id': 'first_id',
                    'sender': {'id': 'client_login', 'role': 'client'},
                    'text': '> client\n> login text\n',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
            ],
            ['first_id'],
            'Sent from the address: client@email.ru\n'
            '>> client\n'
            '>> login text',
            None,
        ),
        (
            [
                {
                    'id': 'first_id',
                    'sender': {'id': 'client_login', 'role': 'client'},
                    'text': '>> second_reply\n> first_reply\nno_reply',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
            ],
            ['first_id'],
            'Sent from the address: client@email.ru\n'
            '>>> second_reply\n'
            '>> first_reply\n'
            '> no_reply',
            None,
        ),
        (
            [
                {
                    'id': 'first_id',
                    'sender': {'id': 'client_login', 'role': 'client'},
                    'text': 'client\nlogin text\n',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
            ],
            ['first_id'],
            'Sent from the address: client@email.ru\n'
            '> client\n'
            '> login text',
            'bad_locale',
        ),
    ],
)
async def test_replied_messages_text(
        cbox,
        mock_st_get_messages,
        messages,
        reply_to,
        expected_result,
        locale,
):
    mock_st_get_messages(
        {'messages': messages, 'total': 0, 'hidden_comments': []},
    )

    task = await cbox.app.db.support_chatterbox.find_one(
        {'_id': 'some_task_id'},
    )

    if locale:
        task['meta_info']['task_language'] = locale

    startrack_source = cbox.app.task_source_manager.startrack_source
    result = await startrack_source._get_replied_messages_text(
        task=task,
        reply_to=reply_to,
        client_email='client@email.ru',
        support_email='support@email.ru',
    )

    assert result == expected_result
