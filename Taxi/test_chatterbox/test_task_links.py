# pylint: disable=no-self-use, too-many-arguments, too-many-locals
import bson
import pytest

from taxi import settings

from chatterbox.internal.tasks_manager import _constants

CHATTERBOX_TRANSLATIONS = {
    'links.all_orders': {'ru': 'все'},
    'links.all_payments': {'ru': 'все'},
    'links.order': {'ru': 'Заказ'},
    'links.payments': {'ru': 'Платежи'},
    'links.balance-admin': {'ru': 'Админка баланса'},
}


@pytest.mark.config(
    CHATTERBOX_LINKS=[
        {
            'name': 'order',
            'chat_type': [
                'startrack',
                'driver',
                'client',
                'client_eats',
                'sms',
                'facebook_support',
            ],
            'link': '{TARIFF_EDITOR_URL}/orders/{order_id}',
            'iframe_url': '{TARIFF_EDITOR_URL}/orders/{order_id}',
            'iframe': True,
            'default_iframe_url': True,
            'params': {'custom_param': {'default': 'some'}},
        },
        {
            'name': 'all_orders',
            'chat_type': [
                'startrack',
                'client',
                'client_eats',
                'sms',
                'facebook_support',
            ],
            'conditions': {'fields/phone_type': {'#exists': True}},
            'link': (
                '{TARIFF_EDITOR_URL}/orders?phone={user_phone}&'
                'phone_type={phone_type}'
            ),
            'with_previous': 'order',
        },
        {
            'name': 'all_orders',
            'chat_type': [
                'startrack',
                'client',
                'client_eats',
                'sms',
                'facebook_support',
            ],
            'link': '{TARIFF_EDITOR_URL}/orders?phone={user_phone}',
            'with_previous': 'order',
        },
        {
            'name': 'payments',
            'chat_type': [
                'startrack',
                'driver',
                'client',
                'client_eats',
                'sms',
                'facebook_support',
            ],
            'link': '{TARIFF_EDITOR_URL}/payments/?order_id={order_id}',
        },
        {
            'name': 'all_payments',
            'chat_type': [
                'startrack',
                'client',
                'client_eats',
                'sms',
                'facebook_support',
            ],
            'link': '{TARIFF_EDITOR_URL}/payments?phone={user_phone}',
            'with_previous': 'payments',
        },
        {
            'name': 'logs',
            'chat_type': [
                'startrack',
                'client',
                'client_eats',
                'sms',
                'facebook_support',
            ],
            'link': '{TARIFF_EDITOR_URL}/logs?order_id={order_id}',
        },
        {
            'name': 'taximeter',
            'chat_type': ['client', 'client_eats', 'sms', 'facebook_support'],
            'link': (
                '{TAXIMETER_ADMIN_URL}/redirect/to/order?'
                'db={park_db_id}&order={order_alias_id}'
            ),
        },
        {
            'name': 'driver',
            'chat_type': [
                'startrack',
                'driver',
                'client',
                'client_eats',
                'sms',
                'facebook_support',
            ],
            'link': '{TARIFF_EDITOR_URL}/show-driver?uuid={driver_uuid}',
        },
        {
            'name': 'promocode',
            'chat_type': ['startrack', 'driver'],
            'link': (
                '{TARIFF_EDITOR_URL}/promocodes-support/'
                'for-drivers/create?'
                'clid={clid}&uuid={driver_uuid}&zendesk_ticket={_id}'
            ),
        },
        {
            'name': 'taxi',
            'chat_type': ['startrack', 'driver'],
            'link': '{TARIFF_EDITOR_URL}/parks/edit/{clid}',
        },
        {
            'name': 'chats-client',
            'chat_type': [
                'startrack',
                'client',
                'client_eats',
                'sms',
                'facebook_support',
            ],
            'conditions': {'fields/user_phone': {'#exists': True}},
            'link': '{SUPCHAT_URL}/chat?user_phone={user_phone}',
        },
        {
            'name': 'chats-client',
            'chat_type': [
                'startrack',
                'client',
                'client_eats',
                'sms',
                'facebook_support',
            ],
            'conditions': {'fields/user_email': {'#exists': True}},
            'link': '{SUPCHAT_URL}/chat?user_email={user_email}',
        },
        {
            'name': 'chats-driver',
            'chat_type': ['startrack', 'driver'],
            'link': '{SUPCHAT_URL}/chat?driver_license={driver_license}',
        },
        {
            'name': 'amocrm',
            'chat_type': ['startrack', 'driver'],
            'link': (
                '{AMOCRM_URL}/dashboard/?sel=all&period=week&'
                'view=conversion&typing=y&term={driver_phone}'
            ),
        },
        {
            'name': 'startrack',
            'chat_type': ['startrack'],
            'link': '{TRACKER_HOST}/{external_id}',
        },
        {
            'name': 'eats-order',
            'chat_type': ['client', 'client_eats'],
            'link': '{EATS_ADMIN_URL}/orders/{eats_order_id}/edit',
        },
        {
            'name': 'eats-orders',
            'chat_type': ['client', 'client_eats'],
            'link': (
                '{EATS_ADMIN_URL}/crm-users/?'
                'crm_user_search%5BphoneNumber%5D={user_phone}'
            ),
            'with_previous': 'eats-order',
        },
        {
            'name': 'd-office',
            'chat_type': ['startrack', 'driver'],
            'link': '{TAXIMETER_ADMIN_URL}/db/login/{park_db_id}',
        },
        {
            'name': 'opteum',
            'chat_type': ['startrack', 'driver'],
            'link': '{TAXIMETER_ADMIN_URL}/db/opteum/{park_db_id}',
        },
        {
            'name': 'park',
            'chat_type': ['startrack', 'driver'],
            'link': '{TAXIMETER_ADMIN_URL}/db/{park_db_id}',
        },
        {
            'name': 'taximeter',
            'chat_type': ['startrack', 'driver'],
            'link': (
                '{TAXIMETER_ADMIN_URL}/redirect/to/order?'
                'db={park_db_id}&order={order_alias_id}'
            ),
        },
        {
            'name': 'balance-admin',
            'chat_type': ['startrack', 'driver'],
            'link': '{BALANCE_ADMIN_URL}/passports.xml',
        },
    ],
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'driver_phone': 'phones',
            'driver_license': 'driver_licenses',
        },
    },
)
@pytest.mark.translations(chatterbox=CHATTERBOX_TRANSLATIONS)
@pytest.mark.parametrize(
    'task_id, chat_type, locale, messages, '
    'expected_orders_links, custom_config',
    [
        (
            '5b2cae5cb2682a976914c2a7',
            'client',
            'ru',
            [
                {
                    'id': '0',
                    'sender': {'id': '1130000029893851', 'role': 'client'},
                    'text': 'message1',
                    'metadata': {
                        'created': '2018-01-02T03:45:00.000Z',
                        'updated': '2018-01-02T03:45:00.000Z',
                    },
                },
            ],
            [
                {
                    'order_id': 'order_id',
                    'default_url': '{TARIFF_EDITOR_URL}/orders/order_id',
                    'links': [
                        [
                            {
                                'url': '{TARIFF_EDITOR_URL}/orders/order_id',
                                'iframe_url': (
                                    '{TARIFF_EDITOR_URL}/orders/order_id'
                                ),
                                'label': 'Заказ',
                                'iframe': True,
                                'params': {
                                    'custom_param': {'default': 'some'},
                                },
                            },
                            {
                                'url': (
                                    '{TARIFF_EDITOR_URL}/'
                                    'orders?phone=%2B79999999999&'
                                    'phone_type=yandex'
                                ),
                                'label': 'все',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TARIFF_EDITOR_URL}/payments/?'
                                    'order_id=order_id'
                                ),
                                'label': 'Платежи',
                            },
                            {
                                'url': (
                                    '{TARIFF_EDITOR_URL}/'
                                    'payments?phone=%2B79999999999'
                                ),
                                'label': 'все',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TARIFF_EDITOR_URL}/logs?'
                                    'order_id=order_id'
                                ),
                                'label': 'logs',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TAXIMETER_ADMIN_URL}/'
                                    'redirect/to/order?db=park_db_id&'
                                    'order=order_alias_id'
                                ),
                                'label': 'taximeter',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TARIFF_EDITOR_URL}/'
                                    'show-driver?uuid=driver_uuid'
                                ),
                                'label': 'driver',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{SUPCHAT_URL}/'
                                    'chat?user_phone=%2B79999999999'
                                ),
                                'label': 'chats-client',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{EATS_ADMIN_URL}/'
                                    'orders/eats_order_id/edit'
                                ),
                                'label': 'eats-order',
                            },
                            {
                                'url': (
                                    '{EATS_ADMIN_URL}/'
                                    'crm-users/?crm_user_search'
                                    '%5BphoneNumber%5D=%2B79999999999'
                                ),
                                'label': 'eats-orders',
                            },
                        ],
                    ],
                },
            ],
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a7',
            'driver',
            'ru',
            [],
            [
                {
                    'order_id': 'order_id',
                    'default_url': '{TARIFF_EDITOR_URL}/orders/order_id',
                    'links': [
                        [
                            {
                                'url': '{TARIFF_EDITOR_URL}/orders/order_id',
                                'iframe_url': (
                                    '{TARIFF_EDITOR_URL}/orders/order_id'
                                ),
                                'label': 'Заказ',
                                'iframe': True,
                                'params': {
                                    'custom_param': {'default': 'some'},
                                },
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TARIFF_EDITOR_URL}/payments/?'
                                    'order_id=order_id'
                                ),
                                'label': 'Платежи',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TARIFF_EDITOR_URL}/'
                                    'show-driver?uuid=driver_uuid'
                                ),
                                'label': 'driver',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TARIFF_EDITOR_URL}/'
                                    'promocodes-support/for-drivers/'
                                    'create?clid=clid&uuid=driver_uuid&'
                                    'zendesk_ticket='
                                    '5b2cae5cb2682a976914c2a7'
                                ),
                                'label': 'promocode',
                            },
                        ],
                        [
                            {
                                'url': '{TARIFF_EDITOR_URL}/parks/edit/clid',
                                'label': 'taxi',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{SUPCHAT_URL}/'
                                    'chat?driver_license=driver_license'
                                ),
                                'label': 'chats-driver',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{AMOCRM_URL}/'
                                    'dashboard/?sel=all&period=week&'
                                    'view=conversion&'
                                    'typing=y&term=%2B78888888888'
                                ),
                                'label': 'amocrm',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TAXIMETER_ADMIN_URL}/'
                                    'db/login/park_db_id'
                                ),
                                'label': 'd-office',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TAXIMETER_ADMIN_URL}/'
                                    'db/opteum/park_db_id'
                                ),
                                'label': 'opteum',
                            },
                        ],
                        [
                            {
                                'url': '{TAXIMETER_ADMIN_URL}/db/park_db_id',
                                'label': 'park',
                            },
                        ],
                        [
                            {
                                'url': (
                                    '{TAXIMETER_ADMIN_URL}/'
                                    'redirect/to/order?db=park_db_id&'
                                    'order=order_alias_id'
                                ),
                                'label': 'taximeter',
                            },
                        ],
                        [
                            {
                                'url': '{BALANCE_ADMIN_URL}/' 'passports.xml',
                                'label': 'Админка баланса',
                            },
                        ],
                    ],
                },
            ],
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'startrack',
            'en',
            [],
            [
                {
                    'links': [
                        [
                            {
                                'label': 'startrack',
                                'url': (
                                    'http://tracker-unstable.taxi.tst'
                                    '.yandex.net/'
                                    'some_user_chat_message_id'
                                ),
                            },
                        ],
                        [
                            {
                                'label': 'balance-admin',
                                'url': (
                                    'https://admin.balance.yandex-team.ru/'
                                    'passports.xml'
                                ),
                            },
                        ],
                    ],
                },
            ],
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a8',
            'client',
            'ru',
            [
                {
                    'id': '0',
                    'sender': {'id': '1130000029893851', 'role': 'client'},
                    'text': 'message1',
                    'metadata': {
                        'created': '2018-01-02T03:45:00.000Z',
                        'updated': '2018-01-02T03:45:00.000Z',
                        'order_id': 'order2',
                        'driver_uuid': 'driver_uuid2',
                    },
                },
                {
                    'id': '1',
                    'sender': {'id': '1130000029893851', 'role': 'client'},
                    'text': 'message2',
                    'metadata': {
                        'created': '2018-01-02T03:45:00.000Z',
                        'updated': '2018-01-02T03:45:00.000Z',
                        'order_id': 'order3',
                        'driver_uuid': 'driver_uuid3',
                    },
                },
            ],
            [
                {
                    'default_url': '{TARIFF_EDITOR_URL}/orders/order2',
                    'links': [
                        [
                            {
                                'iframe': True,
                                'label': 'Заказ',
                                'url': '{TARIFF_EDITOR_URL}/orders/order2',
                                'iframe_url': (
                                    '{TARIFF_EDITOR_URL}/orders/order2'
                                ),
                                'params': {
                                    'custom_param': {'default': 'some'},
                                },
                            },
                        ],
                        [
                            {
                                'label': 'Платежи',
                                'url': (
                                    '{TARIFF_EDITOR_URL}/payments/'
                                    '?order_id=order2'
                                ),
                            },
                        ],
                        [
                            {
                                'label': 'logs',
                                'url': (
                                    '{TARIFF_EDITOR_URL}/logs?order_id=order2'
                                ),
                            },
                        ],
                        [
                            {
                                'label': 'driver',
                                'url': (
                                    '{TARIFF_EDITOR_URL}/'
                                    'show-driver?uuid=driver_uuid2'
                                ),
                            },
                        ],
                    ],
                    'order_id': 'order2',
                },
                {
                    'default_url': '{TARIFF_EDITOR_URL}/orders/order3',
                    'links': [
                        [
                            {
                                'iframe': True,
                                'label': 'Заказ',
                                'url': '{TARIFF_EDITOR_URL}/orders/order3',
                                'iframe_url': (
                                    '{TARIFF_EDITOR_URL}/orders/order3'
                                ),
                                'params': {
                                    'custom_param': {'default': 'some'},
                                },
                            },
                        ],
                        [
                            {
                                'label': 'Платежи',
                                'url': (
                                    '{TARIFF_EDITOR_URL}/payments/'
                                    '?order_id=order3'
                                ),
                            },
                        ],
                        [
                            {
                                'label': 'logs',
                                'url': (
                                    '{TARIFF_EDITOR_URL}/logs?order_id=order3'
                                ),
                            },
                        ],
                        [
                            {
                                'label': 'driver',
                                'url': (
                                    '{TARIFF_EDITOR_URL}/'
                                    'show-driver?uuid=driver_uuid3'
                                ),
                            },
                        ],
                    ],
                    'order_id': 'order3',
                },
                {
                    'default_url': '{TARIFF_EDITOR_URL}/orders/order_id',
                    'links': [
                        [
                            {
                                'iframe': True,
                                'label': 'Заказ',
                                'url': '{TARIFF_EDITOR_URL}/orders/order_id',
                                'iframe_url': (
                                    '{TARIFF_EDITOR_URL}/orders/order_id'
                                ),
                                'params': {
                                    'custom_param': {'default': 'some'},
                                },
                            },
                        ],
                        [
                            {
                                'label': 'Платежи',
                                'url': (
                                    '{TARIFF_EDITOR_URL}/payments/'
                                    '?order_id=order_id'
                                ),
                            },
                        ],
                        [
                            {
                                'label': 'logs',
                                'url': (
                                    '{TARIFF_EDITOR_URL}/logs'
                                    '?order_id=order_id'
                                ),
                            },
                        ],
                    ],
                    'order_id': 'order_id',
                },
            ],
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'client',
            'ru',
            [],
            [
                {
                    'default_url': '4',
                    'links': [
                        [
                            {
                                'label': '1',
                                'url': '1',
                                'iframe_url': '1',
                                'iframe': True,
                            },
                            {
                                'label': '2',
                                'url': '2',
                                'iframe_url': '2',
                                'iframe': True,
                            },
                        ],
                        [
                            {
                                'label': '4',
                                'url': '4',
                                'iframe_url': '4',
                                'iframe': True,
                            },
                        ],
                    ],
                },
            ],
            [
                {
                    'name': '1',
                    'chat_type': ['client'],
                    'link': '1',
                    'iframe_url': '1',
                    'iframe': True,
                },
                {
                    'name': '2',
                    'chat_type': ['client'],
                    'link': '2',
                    'iframe_url': '2',
                    'iframe': True,
                    'default_iframe_url': True,
                    'with_previous': '1',
                },
                {
                    'name': '3',
                    'chat_type': ['driver'],
                    'link': '3',
                    'iframe_url': '3',
                    'iframe': True,
                    'default_iframe_url': True,
                    'with_previous': '2',
                },
                {
                    'name': '4',
                    'chat_type': ['client'],
                    'link': '4',
                    'iframe_url': '4',
                    'iframe': True,
                    'default_iframe_url': True,
                    'with_previous': '3',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a8',
            'client',
            'ru',
            [],
            [
                {
                    'links': [
                        [{'label': '2', 'url': 'not_encode**///\\ %-.,'}],
                    ],
                    'order_id': 'order_id',
                },
            ],
            [
                {
                    'name': '1',
                    'chat_type': ['client'],
                    'link': '{not_encode}',
                    'not_encode_fields': ['not_encode'],
                    'conditions': {'line': 'second'},
                },
                {
                    'name': '2',
                    'chat_type': ['client'],
                    'link': '{not_encode}',
                    'not_encode_fields': ['not_encode'],
                    'conditions': {'line': 'first'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a7',
            'client',
            'ru',
            [],
            [
                {
                    'links': [
                        [{'label': '1', 'url': 'order_id'}],
                        [
                            {
                                'label': '3',
                                'url': 'order_id',
                                'iframe_url': 'order_id',
                            },
                        ],
                    ],
                    'order_id': 'order_id',
                },
            ],
            [
                {'name': '1', 'chat_type': ['client'], 'link': '{order_id}'},
                {'name': '2', 'chat_type': ['client'], 'link': 'order_id}'},
                {
                    'name': '3',
                    'chat_type': ['client'],
                    'link': '{order_id}',
                    'iframe_url': '{order_id}',
                },
                {
                    'name': '4',
                    'chat_type': ['client'],
                    'link': '{order_id}',
                    'iframe_url': 'order_id}',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a7',
            'client',
            'ru',
            [],
            [
                {
                    'links': [
                        [{'label': '1', 'url': 'order_id'}],
                        [
                            {
                                'label': '3',
                                'url': 'order_id',
                                'iframe_url': 'order_id',
                            },
                        ],
                    ],
                    'order_id': 'order_id',
                },
            ],
            [
                {
                    'name': '1',
                    'chat_type': ['client'],
                    'link': '{wrong_order_id}',
                    'fallback_link': '{order_id}',
                },
                {
                    'name': '2',
                    'chat_type': ['client'],
                    'link': 'wrong_order_id}',
                    'fallback_link': 'order_id}',
                },
                {
                    'name': '3',
                    'chat_type': ['client'],
                    'link': '{wrong_order_id}',
                    'fallback_link': '{order_id}',
                    'iframe_url': '{wrong_order_id}',
                    'fallback_iframe_url': '{order_id}',
                },
                {
                    'name': '4',
                    'chat_type': ['client'],
                    'fallback_link': '{order_id}',
                    'link': '{wrong_order_id}',
                    'fallback_iframe_url': 'order_id}',
                    'iframe_url': 'wrong_order_id}',
                },
            ],
        ),
    ],
)
async def test_get_task_links(
        cbox,
        monkeypatch,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_personal,
        response_mock,
        task_id,
        chat_type,
        locale,
        messages,
        expected_orders_links,
        custom_config,
):
    monkeypatch.setattr(settings, 'ENVIRONMENT', settings.TESTING)

    if custom_config:
        cbox.app.config.CHATTERBOX_LINKS = custom_config

    mock_chat_get_history(
        {
            'messages': messages,
            'participants': [
                {'id': '1130000029893851', 'role': 'client'},
                {'id': '1130000031170322', 'role': 'support'},
            ],
            'total': len(messages),
        },
    )
    mock_st_get_comments([])
    mock_st_get_all_attachments()

    task = await cbox.app.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id)},
    )

    task['chat_type'] = chat_type

    settings_urls = _constants.LINKS_HOST_URLS

    chat_messages = await cbox.app.task_source_manager.get_messages(
        task, include_metadata=True,
    )
    order_links = await cbox.app.tasks_manager.get_task_links(
        task, chat_messages, locale,
    )
    for order_data in expected_orders_links:
        if 'default_url' in order_data:
            order_data['default_url'] = order_data['default_url'].format(
                **settings_urls,
            )
        for links in order_data['links']:
            for link in links:
                link['url'] = link['url'].format(**settings_urls)
                if link.get('iframe_url'):
                    link['iframe_url'] = link['iframe_url'].format(
                        **settings_urls,
                    )
    assert order_links == expected_orders_links
