# pylint: disable=redefined-outer-name

import bson
import pytest

from taxi.clients import messenger_chat_mirror
from taxi.clients import support_info


CHATTERBOX_CHAT_INIT_CONFIG = {
    'lavka_messenger': {
        'messenger_enabled': True,
        'bot_id': 'special_id',
        'default_platform': 'yandex',
        'fields': [
            {
                'checks': ['not-empty'],
                'id': 'platform',
                'options': [
                    {'tanker': 'platform.yandex', 'value': 'yandex'},
                    {'tanker': 'platform.yango', 'value': 'yango'},
                ],
                'tanker': 'chat_init.platform',
                'type': 'select',
            },
            {
                'checks': ['not-empty'],
                'id': 'yandex_uid',
                'metadata': True,
                'save_as': 'user_uid',
                'tanker': 'chat_init.yandex_uid',
                'type': 'string',
            },
            {
                'checks': [],
                'id': 'user_id',
                'metadata': True,
                'tanker': 'chat_init.user_id',
                'type': 'string',
            },
            {
                'checks': [],
                'id': 'user_phone',
                'metadata': True,
                'tanker': 'chat_init.user_phone',
                'type': 'string',
            },
            {
                'checks': [],
                'id': 'order_id',
                'metadata': True,
                'tanker': 'chat_init.order_id',
                'type': 'string',
            },
            {
                'checks': ['not-empty'],
                'id': 'message',
                'tanker': 'chat_init.message',
                'type': 'text',
            },
            {
                'checks': ['not-empty'],
                'id': 'user_locale',
                'metadata': True,
                'options': [
                    {'tanker': 'chat_init.ru', 'value': 'ru'},
                    {'tanker': 'chat_init.he', 'value': 'he'},
                    {'tanker': 'chat_init.en', 'value': 'en'},
                    {'tanker': 'chat_init.fr', 'value': 'fr'},
                ],
                'tanker': 'chat_init.user_locale',
                'type': 'select',
            },
            {
                'checks': ['not-empty'],
                'id': 'country',
                'metadata': True,
                'options': [
                    {'tanker': 'chat_init.rus', 'value': 'rus'},
                    {'tanker': 'chat_init.isr', 'value': 'isr'},
                    {'tanker': 'chat_init.gbr', 'value': 'gbr'},
                    {'tanker': 'chat_init.fra', 'value': 'fra'},
                ],
                'tanker': 'chat_init.country',
                'type': 'select',
            },
            {
                'checks': [],
                'id': 'status',
                'options': [
                    {'tanker': 'chat_init.status_new', 'value': 'new'},
                    {'tanker': 'chat_init.status_closed', 'value': 'closed'},
                    {'tanker': 'chat_init.status_waiting', 'value': 'waiting'},
                    {
                        'tanker': 'chat_init.status_closed_with_csat',
                        'value': 'closed_with_csat',
                    },
                ],
                'tanker': 'chat_init.status',
                'type': 'select',
            },
        ],
        'owner_id': 'yandex_uid',
        'owner_role': 'lavka_client',
    },
}


@pytest.fixture
def mock_send_message(monkeypatch, mock):
    def _wrap(response_code, chatterbox_id):
        @mock
        async def send_message(*args, **kwargs):
            if response_code == 409:
                resp = messenger_chat_mirror.Response.error(
                    code='409', text='', external_id=chatterbox_id,
                )
                raise messenger_chat_mirror.Conflict(
                    'Conflict on {}'.format('/send_message'), response=resp,
                )
            return {'external_id': chatterbox_id}

        monkeypatch.setattr(
            messenger_chat_mirror.MessengerChatMirrorApiClient,
            'send_message',
            send_message,
        )
        return mock_send_message

    return _wrap


@pytest.fixture
def mock_get_additional_meta(monkeypatch, mock):
    @mock
    async def _dummy_get_additional_meta(**kwargs):
        metadata = kwargs['data']['metadata'].copy()
        if metadata.get('user_phone'):
            if metadata['user_phone'] == 'missing_user_phone':
                return {'metadata': metadata, 'status': 'no_data'}
            if metadata['user_phone'] == 'user_phone_task_exists':
                user_phone_id = 'task_exists'
            elif metadata['user_phone'] == 'user_phone_task_broken':
                user_phone_id = 'task_broken'
            elif metadata['user_phone'] == 'user_phone_task_closed':
                user_phone_id = 'task_closed'
            elif metadata['user_phone'] == 'user_phone_race_task':
                user_phone_id = 'race_task'
            else:
                user_phone_id = 'phone_id'
            metadata.update({'user_phone_id': user_phone_id})
            if 'use_last_order' in kwargs['data']:
                metadata.update(
                    {
                        'customer_user_id': 'some_user_id',
                        'user_locale': 'ru',
                        'user_platform': 'android',
                        'city': 'moscow',
                        'country': 'rus',
                    },
                )
        if metadata.get('driver_uuid'):
            if metadata['driver_uuid'] == 'missing_uuid':
                return {'metadata': metadata, 'status': 'no_data'}
            if metadata['driver_uuid'] == 'driver_uuid_task_exists':
                unique_driver_id = 'task_exists'
            elif metadata['driver_uuid'] == 'driver_uuid_task_broken':
                unique_driver_id = 'task_broken'
            else:
                unique_driver_id = 'some_unique_driver_id'
            metadata.update(
                {
                    'park_db_id': 'some_park_id',
                    'driver_license': 'some_driver_license',
                    'driver_name': 'Швабрэ Старая Пристарая',
                    'driver_phone': '+70000000000',
                    'driver_locale': 'ru',
                    'taximeter_version': '0.1.2',
                    'clid': 'some_clid',
                    'park_name': 'Лещ',
                    'park_city': 'moscow',
                    'park_country': 'rus',
                    'car_number': '123XYZ',
                    'unique_driver_id': unique_driver_id,
                },
            )
        if metadata.get('order_id'):
            metadata.update(
                {
                    'car_number': '123XYZ',
                    'city': 'moscow',
                    'country': 'rus',
                    'clid': 'some_clid',
                    'coupon': False,
                    'coupon_used': False,
                    'driver_id': 'some_driver_id',
                    'order_alias_id': 'some_alias_id',
                    'park_db_id': 'some_park_id',
                    'payment_type': 'cash',
                    'precomment': 'ahaha',
                    'tariff': 'econom',
                    'customer_user_id': 'some_user_id',
                    'user_platform': 'android',
                    'user_locale': 'ru',
                },
            )
        else:
            assert 'use_last_order' in kwargs['data']
        if kwargs['data'].get('applications'):
            if 'vezet' not in kwargs['data']['applications'][0]:
                metadata.update(
                    {'user_platform': kwargs['data']['applications'][0]},
                )
        return {'metadata': metadata, 'status': 'ok'}

    monkeypatch.setattr(
        support_info.SupportInfoApiClient,
        'get_additional_meta',
        _dummy_get_additional_meta,
    )
    return _dummy_get_additional_meta


@pytest.fixture
def mock_get_chat_messenger(monkeypatch, mock):
    @mock
    async def _dummy_get_chat(*args, **kwargs):
        return {
            'id': 'some_chat_id',
            'type': 'messenger',
            'status': {'is_visible': True, 'is_open': True},
            'participants': [
                {'id': 'owner_id', 'role': 'client', 'is_owner': True},
            ],
        }

    monkeypatch.setattr(
        messenger_chat_mirror.MessengerChatMirrorApiClient,
        'get_chat',
        _dummy_get_chat,
    )
    return _dummy_get_chat


@pytest.mark.config(CHATTERBOX_CHAT_INIT=CHATTERBOX_CHAT_INIT_CONFIG)
@pytest.mark.config(
    CHATTERBOX_DEFAULT_LINES={'lavka_messenger': 'first_messenger'},
    CHATTERBOX_SOURCE_TYPE_MAPPING={'lavka_messenger': 'client_lavka'},
)
async def test_task_init_messenger(
        cbox,
        mock_send_message,
        mock_get_additional_meta,
        mock_get_chat_messenger,
        mock_chat_add_update,
        mock_chat_get_history,
):
    mock_chat_get_history({'messages': []})
    mock_send_message(200, 'new_id')
    data = {
        'country': 'RUS',
        'message': (
            'Здравствуйте!\\n\\nНедавно мы получили от вас низкую '
            'оценку по заказу.\\n\\nЧто именно пошло не так?'
        ),
        'order_id': '57aead293a8f48bb93c30708dd307de3-grocery',
        'platform': 'yandex',
        'request_id': '57aead293a8f48bb93c30708dd307de3-grocery-0',
        'status': 'waiting',
        'user_id': '064fe8a7d6ef426882787003f49ba40d',
        'user_locale': 'ru',
        'user_phone': '+79817580983',
        'yandex_uid': '931682628',
    }
    await cbox.post('/v2/tasks/init_with_tvm/lavka_messenger/', data=data)
    assert cbox.status == 200

    assert cbox.body_data['status'] == 'waiting'

    task = await cbox.app.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(cbox.body_data['id'])},
    )
    assert task['status'] == 'waiting'
    assert task['support_admin'] == 'superuser'
    assert 'support_init' in task['tags']
    assert 'type' in task
    assert task['meta_info']['user_phone'] == '+79817580983'
    assert task['meta_info']['yandex_uid'] == '931682628'
    assert task['meta_info']['user_id'] == '064fe8a7d6ef426882787003f49ba40d'
    assert not task.get('inner_comments')


@pytest.mark.config(CHATTERBOX_CHAT_INIT=CHATTERBOX_CHAT_INIT_CONFIG)
@pytest.mark.config(
    CHATTERBOX_DEFAULT_LINES={'lavka_messenger': 'first_messenger'},
    CHATTERBOX_SOURCE_TYPE_MAPPING={'lavka_messenger': 'client_lavka'},
)
async def test_task_init_messenger_created_already(
        cbox,
        mock_send_message,
        mock_get_additional_meta,
        mock_get_chat_messenger,
        mock_chat_add_update,
        mock_chat_get_history,
):
    mock_chat_get_history({'messages': []})
    mock_send_message(409, 'external_id')
    await cbox.app.db.support_chatterbox.insert(
        {'_id': 'existing_task_id', 'external_id': 'external_id'},
    )
    data = {
        'country': 'RUS',
        'message': (
            'Здравствуйте!\\n\\nНедавно мы получили от вас низкую '
            'оценку по заказу.\\n\\nЧто именно пошло не так?'
        ),
        'order_id': '57aead293a8f48bb93c30708dd307de3-grocery',
        'platform': 'yandex',
        'request_id': '57aead293a8f48bb93c30708dd307de3-grocery-0',
        'status': 'waiting',
        'user_id': '064fe8a7d6ef426882787003f49ba40d',
        'user_locale': 'ru',
        'user_phone': '+79817580983',
        'yandex_uid': '931682628',
    }
    await cbox.post('/v2/tasks/init_with_tvm/lavka_messenger/', data=data)
    assert cbox.status == 409
    assert cbox.body_data['task_id'] == 'existing_task_id'
    assert cbox.body_data['status'] == 'Chat already opened'
