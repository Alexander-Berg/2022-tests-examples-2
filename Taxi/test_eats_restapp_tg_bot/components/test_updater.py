# pylint: disable=protected-access

import pytest

from eats_restapp_tg_bot.components.telegram import update


@pytest.mark.config(
    EATS_RESTAPP_TG_BOT_COMMANDS_SETTINGS={
        'available_commands': [
            '/start',
            '/stop',
            '/about_notifications',
            '/how_to_read_reports',
            '/help',
        ],
        'command_messages': {
            '/start': ['welcome'],
            '/stop': ['stop'],
            '/about_notifications': ['about', 'smth'],
            '/how_to_read_reports': ['how to read'],
            '/help': ['help'],
        },
        'default_message': ['not available'],
        'new_user_command': '/start',
    },
    EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL=False,
)
async def test_should_send_all_needed_messages(stq3_context, stq, load_json):
    json_list = load_json('updates.json')
    updates = [update.Update.de_json(x, {}) for x in json_list]

    await stq3_context.updater._process_updates(updates)

    expected = load_json('stq_kwargs.json')

    for task in expected:
        check_stq_kwargs(stq.eats_restapp_tg_bot_send_message, **task)


def check_stq_kwargs(stq_mock, **kwargs):
    call_args = stq_mock.next_call()
    print(call_args['kwargs'])
    print(kwargs)
    assert call_args['kwargs'] == kwargs


@pytest.mark.config(
    EATS_RESTAPP_TG_BOT_COMMANDS_SETTINGS={
        'available_commands': [
            '/start',
            '/stop',
            '/about_notifications',
            '/how_to_read_reports',
            '/help',
        ],
        'command_messages': {
            '/start': ['welcome'],
            '/stop': ['stop'],
            '/about_notifications': ['about', 'smth'],
            '/how_to_read_reports': ['how to read'],
            '/help': ['help'],
        },
        'default_message': ['not available'],
        'new_user_command': '/start',
    },
)
@pytest.mark.parametrize(
    'enable_personal,testcase',
    [[True, 'with_personal'], [False, 'without_personal']],
)
@pytest.mark.pgsql('eats_restapp_tg_bot', files=['default.sql'])
async def test_should_add_new_personal_logins(
        stq3_context,
        stq,
        load_json,
        taxi_config,
        mock_personal,
        pgsql,
        enable_personal,
        testcase,
):
    @mock_personal('/v2/telegram_logins/bulk_store')
    async def mock_tg_login(request):
        return {
            'items': [
                {'id': 'personal_login', 'value': 'test_login'},
                {'id': 'personal_existed', 'value': 'existed'},
            ],
        }

    @mock_personal('/v2/telegram_ids/bulk_store')
    async def mock_tg_user_id(request):
        return {
            'items': [
                {'id': 'personal_123', 'value': '123'},
                {'id': 'existed123', 'value': '1234'},
            ],
        }

    json_list = load_json('updates.json')
    updates = [update.Update.de_json(x, {}) for x in json_list]

    stq3_context.config._set_values(
        {'EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL': enable_personal},
    )

    await stq3_context.updater._process_updates(updates)

    assert mock_tg_login.has_calls == enable_personal
    assert mock_tg_user_id.has_calls == enable_personal

    # enable personal
    # mock_personal for tg_login
    # mock_personal for tg_chat_id
    # pgsql check that new login is added
    with pgsql['eats_restapp_tg_bot'].dict_cursor() as cursor:
        cursor.execute(
            'SELECT login,personal_login,personal_user_id,user_id FROM logins',
        )
        data = [row.copy() for row in cursor]
        assert data == load_json('expected.json')[testcase]
