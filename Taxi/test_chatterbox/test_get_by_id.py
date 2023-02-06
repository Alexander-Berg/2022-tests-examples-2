# pylint: disable=no-self-use, too-many-arguments, too-many-locals
# pylint: disable=too-many-lines
import http

import bson
import pytest

from taxi import settings
from taxi.clients import support_chat
from taxi.util import permissions

from chatterbox.api import rights
from chatterbox.internal.tasks_manager import _constants
from test_chatterbox import plugins as conftest


CHATTERBOX_TRANSLATIONS = {
    'links.all_orders': {'ru': 'все'},
    'links.all_payments': {'ru': 'все'},
    'links.order': {'ru': 'Заказ'},
    'links.payments': {'ru': 'Платежи'},
    'links.balance-admin': {'ru': 'Админка баланса'},
}


@pytest.mark.parametrize('check_legacy', [True, False])
@pytest.mark.parametrize(
    'task_id, task_type, task_status, external_id, last_message_id,'
    'expected_status',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            'chat',
            'new',
            'some_user_chat_message_id',
            None,
            200,
        ),
        (
            '5c2cae5cb2682a976914c2a1',
            'messenger',
            'new',
            'some_user_chat_message_id',
            None,
            200,
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            'chat',
            'new',
            'some_user_chat_message_id',
            None,
            200,
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            'chat',
            'new',
            'some_user_chat_message_id',
            '0',
            200,
        ),
        (
            '5b2cae5cb2682a976914c2a3',
            'chat',
            'new',
            'some_user_chat_message_id',
            None,
            404,
        ),
        (
            '5b2cae5cb2682a976914c2a5',
            'startrack',
            'new',
            'TESTQUEUE-1',
            None,
            200,
        ),
        (
            '5b2cae5cb2682a976914c2a5',
            'startrack',
            'new',
            'TESTQUEUE-1',
            None,
            200,
        ),
        (
            '5b2cae5cb2682a976914c2a5',
            'startrack',
            'new',
            'TESTQUEUE-1',
            '123',
            400,
        ),
        (
            '5b2cae5cb2682a976914c2a9',
            'chat',
            'new',
            'some_user_chat_message_id_4',
            None,
            200,
        ),
    ],
)
async def test_get_by_id(
        cbox,
        patch_aiohttp_session,
        response_mock,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        check_legacy,
        task_id,
        task_type,
        task_status,
        external_id,
        last_message_id,
        expected_status,
):
    mocked_chat_history = mock_chat_get_history(
        {
            'messages': [
                {
                    'id': '0',
                    'sender': {'id': '1130000029893851', 'role': 'client'},
                    'text': 'some description',
                    'metadata': {
                        'created': '2018-01-02T03:45:00.000Z',
                        'updated': '2018-01-02T03:45:00.000Z',
                        'ticket_subject': 'some summary',
                        'attachments': [
                            {'id': 'attachment_id', 'source': 'mds'},
                            {'id': 'attachment_id_1', 'source': 'mds'},
                            {
                                'id': 'attachment_id_2',
                                'source': 'facebook',
                                'link': 'test_link',
                            },
                        ],
                    },
                },
            ],
            'participants': [
                {'id': '1130000029893851', 'role': 'client'},
                {'id': '1130000031170322', 'role': 'support'},
            ],
            'total': 1,
            'newest_message_id': '0',
        },
    )
    startrack_comment = {
        'id': 'test_comment',
        'longId': 'long_id',
        'text': 'Test Comment',
        'createdAt': '2018-05-05T15:34:56+0000',
        'updatedAt': '2018-05-05T15:34:56+0000',
        'createdBy': {'id': 111, 'display': 'support name'},
    }
    mocked_st_comments = mock_st_get_comments([startrack_comment])
    mock_st_get_all_attachments()

    archive_doc = await cbox.app.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId('5b2cae5cb2682a976914c2a1')},
    )
    if check_legacy:
        archive_doc['user_chat_message_id'] = archive_doc.pop('external_id')
    archive_doc['_id'] = bson.ObjectId(task_id)

    @patch_aiohttp_session(
        'http://archive-api.taxi.yandex.net/v1/yt/lookup_rows', 'POST',
    )
    def lookup_rows_request(*args, **kwargs):
        if task_id == '5b2cae5cb2682a976914c2a2':
            return response_mock(
                read=bson.BSON.encode({'items': [{'doc': archive_doc}]}),
                headers={'Content-Type': 'application/bson'},
            )
        return response_mock(
            read=bson.BSON.encode({'items': []}),
            headers={'Content-Type': 'application/bson'},
        )

    if last_message_id is None:
        params = None
    else:
        params = {'last_message_id': last_message_id}
    await cbox.query('/v1/tasks/{}/'.format(task_id), params=params)
    assert cbox.status == expected_status
    if expected_status == 200:
        expected_data = {
            'chat_messages': {
                'messages': [
                    {
                        'id': '0',
                        'sender': {'id': '1130000029893851', 'role': 'client'},
                        'text': 'some description',
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'ticket_subject': 'some summary',
                        },
                    },
                ],
                'participants': [
                    {'id': '1130000029893851', 'role': 'client'},
                    {'id': '1130000031170322', 'role': 'support'},
                ],
                'total': 1,
                'newest_message_id': '0',
            },
            'chat_type': 'client',
            'external_id': external_id,
            'id': task_id,
            'line': 'first',
            'meta_info': {'ml_suggestions': [], 'user_id': 'some_user_id'},
            'meta_to_show': [],
            'tags': ['some_tag'],
            'type': task_type,
            'status': task_status,
            'history': [
                {
                    'action': 'hidden_comment',
                    'login': 'support_login',
                    'created': '2018-06-27T15:00:00+0000',
                },
            ],
            'hidden_comments': [
                {
                    'comment': 'comment',
                    'login': 'support_login',
                    'created': '2018-06-27T15:00:00+0000',
                },
            ],
            'created': '2018-06-27T15:00:00+0000',
            'updated': '2018-06-27T15:00:00+0000',
            'actions': [
                {
                    'action_id': 'export',
                    'query_params': {'chatterbox_button': 'chatterbox_zen'},
                    'title': '✍️ Ручное',
                    'view': {'position': 'statusbar', 'type': 'button'},
                },
            ],
            'orders_links': [],
            'comment_is_read_only': False,
        }
        if str(last_message_id) == '0':
            expected_data['chat_messages']['messages'] = []
        elif task_type in ('chat', 'messenger'):
            message = expected_data['chat_messages']['messages'][0]
            message['metadata']['attachments'] = [
                {
                    'id': 'attachment_id',
                    'source': 'mds',
                    'link': (
                        'https://supchat.taxi.dev.'
                        'yandex-team.ru/chatterbox-api/v1/'
                        'tasks/%s/attachment/'
                        'attachment_id' % task_id
                    ),
                },
                {
                    'id': 'attachment_id_1',
                    'source': 'mds',
                    'link': (
                        'https://supchat.taxi.dev.'
                        'yandex-team.ru/chatterbox-api/v1/'
                        'tasks/%s/attachment/'
                        'attachment_id_1' % task_id
                    ),
                },
                {
                    'id': 'attachment_id_2',
                    'source': 'facebook',
                    'link': 'test_link',
                },
            ]

            get_history_call = mocked_chat_history.calls[0]
            assert get_history_call['args'] == (external_id,)
            del get_history_call['kwargs']['log_extra']
            if task_type == 'messenger':
                del get_history_call['kwargs']['user_guid']
            assert get_history_call['kwargs'] == {
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': None,
            }

        elif task_type == 'startrack':
            comment_from_startrack = {
                'comment': startrack_comment['text'],
                'created': startrack_comment['createdAt'],
                'login': startrack_comment['createdBy']['display'],
                'external_comment_id': 'test_comment',
            }

            expected_data['hidden_comments'].append(comment_from_startrack)
            if last_message_id is not None:
                expected_data['chat_messages']['messages'] = []
                expected_data['chat_messages']['total'] = 0
                del expected_data['chat_messages']['newest_message_id']
            get_comments_call = mocked_st_comments.calls[0]
            assert get_comments_call['ticket'] == external_id
            assert get_comments_call['kwargs'] == {
                'short_id': last_message_id,
                'per_page': 2000,
            }

        if task_id == '5b2cae5cb2682a976914c2a9':
            expected_data['meta_info']['user_promocodes_count'] = 0
            expected_data['meta_info']['driver_promocodes_count'] = 1
            expected_data['meta_info']['user_refund_count'] = 2
            expected_data['meta_info']['driver_activity_return_count'] = 3
            expected_data['meta_to_show'] = [
                {'label': 'meta.driver_activity_return_count', 'value': '3'},
                {'label': 'meta.driver_promocodes_count', 'value': '1'},
                {'label': 'meta.user_promocodes_count', 'value': '0'},
                {'label': 'meta.user_refund_count', 'value': '2'},
            ]

        cbox.body_data['meta_to_show'].sort(key=lambda item: item['label'])
        assert cbox.body_data == expected_data
    if task_id in ['5b2cae5cb2682a976914c2a2', '5b2cae5cb2682a976914c2a3']:
        lookup_row_call = lookup_rows_request.calls[0]
        assert lookup_row_call['kwargs']['json'] == {
            'query': [{'id': task_id}],
            'replication_rule': {
                'name': 'support_chatterbox_bson_runtime',
                'max_delay': 43200,
            },
            'column_names': ['doc'],
            'bson': True,
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
    'expected_orders_links, custom_config, last_message_id',
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
                        'updated': '2018-01-03T03:45:00.000Z',
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
            None,
        ),
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
                        'updated': '2018-01-03T03:45:00.000Z',
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
            '0',
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
                        'created': '2018-01-03T03:45:00.000Z',
                        'updated': '2018-01-03T03:45:00.000Z',
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
                        'created': '2018-01-03T03:45:00.000Z',
                        'updated': '2018-01-03T03:45:00.000Z',
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
            '0',
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
                        'created': '2018-01-03T03:45:00.000Z',
                        'updated': '2018-01-03T03:45:00.000Z',
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
            '1',
        ),
    ],
)
async def test_get_by_id_links(
        cbox,
        patch_aiohttp_session,
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
        last_message_id,
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

    settings_urls = _constants.LINKS_HOST_URLS

    if last_message_id is None:
        params = None
    else:
        params = {'last_message_id': last_message_id}
    await cbox.query('/v1/tasks/{}/'.format(task_id), params=params)

    order_links = cbox.body_data['orders_links']

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


@pytest.mark.parametrize(
    'tvm_enabled, authorize, status',
    [
        (False, permissions.unrestricted_perm(), http.HTTPStatus.OK),
        (True, permissions.unrestricted_perm(), http.HTTPStatus.OK),
        (False, None, http.HTTPStatus.OK),
        (True, None, http.HTTPStatus.FORBIDDEN),
    ],
)
async def test_get_by_id_auth(
        cbox, monkeypatch, tvm_enabled, authorize, status,
):
    async def authorize_request(*args, **kwargs):
        return authorize

    async def get_history(self, *args, **kwargs):
        return {'messages': [{'text': 'some message'}], 'total': 1}

    cbox.app.config.TVM_ENABLED = tvm_enabled
    monkeypatch.setattr(permissions, 'authorize_request', authorize_request)
    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_history', get_history,
    )

    await cbox.query('/v1/tasks/5b2cae5cb2682a976914c2a1/')
    assert cbox.status == status


@pytest.mark.config(
    CHATTERBOX_NON_ACTIVE_BUTTONS=[
        {
            'action_id': 'export',
            'title': '✍️ Ручное',
            'query_params': {'chatterbox_button': 'chatterbox_zen'},
            'title_tanker': 'buttons.zen',
        },
    ],
)
@pytest.mark.translations(
    chatterbox={'buttons.zen': {'ru': '✍️ Ручное', 'en': '✍️ Export'}},
)
@pytest.mark.parametrize(
    'task_id, locale, expected_title',
    [
        ('5b2cae5cb2682a976914c2a1', 'ru', '✍️ Ручное'),
        ('5b2cae5cb2682a976914c2a1', 'en', '✍️ Export'),
    ],
)
async def test_translations(
        cbox,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        response_mock,
        task_id,
        locale,
        expected_title,
):
    mock_chat_get_history(
        {
            'messages': [],
            'participants': [
                {'id': '1130000029893851', 'role': 'client'},
                {'id': '1130000031170322', 'role': 'support'},
            ],
            'total': 1,
        },
    )
    mock_st_get_comments([])
    mock_st_get_all_attachments()

    archive_doc = await cbox.app.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId('5b2cae5cb2682a976914c2a1')},
    )
    archive_doc['_id'] = bson.ObjectId(task_id)

    await cbox.query(
        '/v1/tasks/{}/'.format(task_id), headers={'Accept-Language': locale},
    )

    assert cbox.body_data['actions'] == [
        {
            'action_id': 'export',
            'query_params': {'chatterbox_button': 'chatterbox_zen'},
            'title': expected_title,
            'view': {'position': 'statusbar', 'type': 'button'},
        },
    ]


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    ('login', 'config_lines', 'expected_response'),
    (
        (
            'superuser',
            [],
            {'allow_call': False, 'allow_call_any_number': False},
        ),
        (
            'superuser',
            ['first'],
            {'allow_call': True, 'allow_call_any_number': True},
        ),
        (
            'user_with_sip_permitted',
            [],
            {'allow_call': False, 'allow_call_any_number': False},
        ),
        (
            'user_with_sip_permitted',
            ['first'],
            {'allow_call': True, 'allow_call_any_number': True},
        ),
        (
            'user_with_sip_not_permitted',
            [],
            {'allow_call': False, 'allow_call_any_number': False},
        ),
        (
            'user_with_sip_not_permitted',
            ['first'],
            {'allow_call': False, 'allow_call_any_number': False},
        ),
    ),
)
async def test_get_by_id_sip(
        cbox: conftest.CboxWrap,
        patch_auth,
        patch_support_chat_get_history,
        login,
        config_lines,
        expected_response,
):
    patch_auth(login=login)
    patch_support_chat_get_history()
    cbox.app.config.CHATTERBOX_SIP_ENABLED_LINES = config_lines

    await cbox.query('/v1/tasks/5b2cae5cb2682a976914c2a1/')
    assert cbox.status == 200
    assert cbox.body_data['sip_settings'] == expected_response


async def test_get_by_id_sip_meta_info(
        cbox: conftest.CboxWrap, patch_support_chat_get_history,
):
    patch_support_chat_get_history()

    await cbox.query('/v1/tasks/5b2cae5cb2682a976914c2a6/')
    assert cbox.status == 200
    assert cbox.body_data['meta_info'] == {
        'calls': [
            {
                'id': 'id_1',
                'record_urls': [
                    'https://supchat.taxi.dev.yandex-team.ru/chatterbox-api'
                    '/v1/tasks/5b2cae5cb2682a976914c2a6/sip_record/id_1/0',
                    'https://supchat.taxi.dev.yandex-team.ru/chatterbox-api'
                    '/v1/tasks/5b2cae5cb2682a976914c2a6/sip_record/id_1/1',
                ],
                'stat_created': '2018-06-27T15:00:00+0000',
            },
            {
                'id': 'id_2',
                'record_urls': [
                    'https://supchat.taxi.dev.yandex-team.ru/chatterbox-api'
                    '/v1/tasks/5b2cae5cb2682a976914c2a6/sip_record/id_2/0',
                    'https://supchat.taxi.dev.yandex-team.ru/chatterbox-api'
                    '/v1/tasks/5b2cae5cb2682a976914c2a6/sip_record/id_2/1',
                ],
                'stat_created': '2018-06-27T15:00:00+0000',
            },
            {
                'id': 'id_3',
                'source': 'ivr',
                'record_urls': [
                    'https://supchat.taxi.dev.yandex-team.ru/chatterbox-api'
                    '/v1/tasks/5b2cae5cb2682a976914c2a6/sip_record/id_3/0',
                ],
                'stat_created': '2018-06-27T15:00:00+0000',
            },
        ],
    }


@pytest.mark.config(
    TVM_ENABLED=True,
    CHATTERBOX_LINES={'first': {'name': '1 · DM РФ', 'priority': 3}},
    CHATTERBOX_LINES_PERMISSIONS={
        'first': {
            'take': [{'permissions': ['take_permission']}],
            'search': [
                {'permissions': ['search_permission']},
                {
                    'permissions': ['search_permission_by_country'],
                    'countries': ['eng'],
                },
            ],
        },
    },
)
@pytest.mark.parametrize(
    ('tvm_enabled', 'groups', 'is_superuser', 'expected_status'),
    (
        (False, [], False, 200),
        (True, [], True, 200),
        (True, [], True, 200),
        (True, ['readonly', 'client_first'], False, 200),
        (True, ['readonly', 'client_first_search'], False, 200),
        (True, ['readonly', 'client_first_search_english'], False, 200),
        (
            True,
            ['readonly', rights.CHATTERBOX_SEARCH_AND_VIEW_FULL],
            False,
            200,
        ),
        (True, ['readonly', rights.CHATTERBOX_TAKE_FULL], False, 200),
        (True, [], False, 403),
        (True, ['readonly', 'client_first_search_russia'], False, 403),
        (True, ['readonly'], False, 403),
    ),
)
async def test_get_by_id_lines_permissions(
        cbox: conftest.CboxWrap,
        patch_auth,
        patch_support_chat_get_history,
        tvm_enabled: bool,
        groups: list,
        is_superuser: bool,
        expected_status: int,
):
    cbox.app.config.TVM_ENABLED = tvm_enabled
    if tvm_enabled:
        patch_auth(superuser=is_superuser, groups=groups)

    patch_support_chat_get_history()

    await cbox.query('/v1/tasks/5b2cae5cb2682a976914c2a1/')
    assert cbox.status == expected_status


@pytest.mark.config(TVM_ENABLED=True, CHATTERBOX_LINES={})
@pytest.mark.parametrize(
    ('groups', 'is_superuser', 'expected_status'),
    (
        ([], False, 403),
        ([], True, 200),
        (['readonly', 'client_first'], False, 403),
        (['readonly', rights.CHATTERBOX_SEARCH_AND_VIEW_FULL], False, 200),
        (['readonly', rights.CHATTERBOX_TAKE_FULL], False, 200),
    ),
)
async def test_get_by_id_old_lines(
        cbox: conftest.CboxWrap,
        patch_auth,
        patch_support_chat_get_history,
        groups: list,
        is_superuser: bool,
        expected_status: int,
):
    patch_auth(superuser=is_superuser, groups=groups)

    patch_support_chat_get_history()

    await cbox.query('/v1/tasks/5b2cae5cb2682a976914c2a1/')
    assert cbox.status == expected_status
