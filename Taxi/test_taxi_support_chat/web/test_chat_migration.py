import pytest

from taxi_support_chat.internal import chat_migration


@pytest.mark.now('2021-05-24 16:18:15')
@pytest.mark.parametrize(
    ('input_params_set', 'expected_data_set'),
    [
        ('simple_open', 'simple_open'),
        ('simple_closed', 'simple_closed'),
        ('change_owner', 'change_owner'),
        ('dry_run', 'dry_run'),
        ('only_owners', 'only_owners'),
        ('two_types', 'two_types'),
    ],
)
async def test_migrations(
        web_context,
        load_json,
        input_params_set,
        expected_data_set,
        mock_get_users,
):
    input_params = load_json('input_params.json')[input_params_set]

    await chat_migration.migrate_chats(web_context, **input_params)

    expected_data = load_json('expected_data.json')[expected_data_set]

    chats_cursor = web_context.mongo.user_chat_messages.find(
        {'type': expected_data['type']},
        projection=['owner_id', 'type', 'messages'],
    )
    chats = []
    async for chat in chats_cursor:
        chats.append(chat)

    assert chats == expected_data['chats']
