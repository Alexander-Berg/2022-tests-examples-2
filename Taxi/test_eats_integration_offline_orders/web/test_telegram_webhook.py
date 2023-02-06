import pytest

MANAGER_CHAT_ID = 1000
MANAGER_USERNAME = 'resoranoff_manager'
MANAGER_USERNAME_WITH_AT = '@resoranoff_manager'
GROUP_CHAT_ID = 1000000
HASHED_TOKEN = '$2b$12$FyBEFI4kdGIzJUj0lC7eaO.iBk004xParYyNIE2ZocyEMCOCC/TJG'
PLACE_ID = 'place_id__1'
PLACE_SLUG = 'place_id__1_slug'


def get_text(context, template_name: str) -> str:
    templates = (
        context.config.EATS_INTEGRATION_OFFLINE_ORDERS_TELEGRAM_TEMPLATES
    )
    return templates[template_name]


async def test_start_in_private(web_context, web_app_client, load_json, patch):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text, **kwargs):
        assert chat_id == MANAGER_CHAT_ID
        assert text == get_text(web_context, 'start_from_private_chat')

    response = await web_app_client.post(
        f'/v1/webhook', json=load_json('start_command_from_private.json'),
    )
    assert response.status == 200


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_TELEGRAM_MANAGERS={'restaurants': {}},
)
async def test_start_in_group_no_place(
        web_context, web_app_client, load_json, patch,
):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text, **kwargs):
        assert chat_id == GROUP_CHAT_ID
        assert text == get_text(web_context, 'start_no_place')

    response = await web_app_client.post(
        f'/v1/webhook', json=load_json('start_command_from_group.json'),
    )
    assert response.status == 200


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={
        'telegram_managers_source': 'db',
    },
)
async def test_start_in_group_no_place_db(
        web_context, web_app_client, load_json, patch,
):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text, **kwargs):
        assert chat_id == GROUP_CHAT_ID
        assert text == get_text(web_context, 'start_no_place')

    response = await web_app_client.post(
        f'/v1/webhook', json=load_json('start_command_from_group.json'),
    )
    assert response.status == 200


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_TELEGRAM_MANAGERS={
        'restaurants': {PLACE_SLUG: {'place_id': PLACE_ID, 'managers': []}},
    },
)
async def test_start_in_group_unauthorized(
        web_context, web_app_client, load_json, patch,
):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text, **kwargs):
        assert chat_id == GROUP_CHAT_ID
        assert text == get_text(web_context, 'start_no_permissions')

    response = await web_app_client.post(
        f'/v1/webhook', json=load_json('start_command_from_group.json'),
    )
    assert response.status == 200


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_TELEGRAM_MANAGERS={
        'restaurants': {PLACE_SLUG: {'place_id': PLACE_ID, 'managers': []}},
    },
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={
        'telegram_managers_source': 'db',
    },
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql'],
)
async def test_start_in_group_unauthorized_db(
        web_context, web_app_client, load_json, patch,
):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text, **kwargs):
        assert chat_id == GROUP_CHAT_ID
        assert text == get_text(web_context, 'start_no_permissions')

    response = await web_app_client.post(
        f'/v1/webhook', json=load_json('start_command_from_group.json'),
    )
    assert response.status == 200


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_TELEGRAM_MANAGERS={
        'restaurants': {
            PLACE_SLUG: {
                'place_id': PLACE_ID,
                'managers': [
                    MANAGER_USERNAME,
                    MANAGER_USERNAME_WITH_AT,
                    str(MANAGER_CHAT_ID),
                ],
            },
        },
    },
)
@pytest.mark.parametrize(
    'webhook_data',
    [
        'start_command_from_group.json',
        'start_command_from_group_with_at.json',
        'start_command_from_group_no_username.json',
    ],
)
async def test_start_in_group_with_access(
        web_context, web_app_client, load_json, patch, pgsql, webhook_data,
):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text, **kwargs):
        assert chat_id == GROUP_CHAT_ID
        assert text == get_text(web_context, 'start_from_group_success')

    response = await web_app_client.post(
        f'/v1/webhook', json=load_json(webhook_data),
    )
    assert response.status == 200

    chat = get_chats(pgsql, GROUP_CHAT_ID)[0]
    assert chat[1] == 'group'
    assert chat[2] == PLACE_ID


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={
        'telegram_managers_source': 'db',
    },
    TVM_RULES=[{'src': 'eats-integration-offline-orders', 'dst': 'personal'}],
)
@pytest.mark.parametrize(
    'webhook_data',
    ['start_command_from_group.json', 'start_command_from_group_with_at.json'],
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'telegram_managers.sql'],
)
async def test_start_in_group_with_access_db(
        web_context,
        web_app_client,
        mockserver,
        load_json,
        patch,
        pgsql,
        webhook_data,
):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text, **kwargs):
        assert chat_id == GROUP_CHAT_ID
        assert text == get_text(web_context, 'start_from_group_success')

    @mockserver.json_handler('/personal/v1/telegram_logins/bulk_retrieve')
    def _bulk_retrieve_telegram_logins(request):
        mapper = {'personal_telegram_login_id_1': MANAGER_USERNAME}
        result = {
            'items': [
                {'id': item['id'], 'value': mapper.get(item['id'], '')}
                for item in request.json['items']
            ],
        }
        return result

    response = await web_app_client.post(
        f'/v1/webhook', json=load_json(webhook_data),
    )
    assert response.status == 200

    chat = get_chats(pgsql, GROUP_CHAT_ID)[0]
    assert chat[1] == 'group'
    assert chat[2] == PLACE_ID


def get_chats(pgsql, chat_id):
    with pgsql['eats_integration_offline_orders'].cursor() as cursor:
        cursor.execute(f'SELECT * FROM telegram_chats WHERE chat_id={chat_id}')
        return cursor.fetchall()
