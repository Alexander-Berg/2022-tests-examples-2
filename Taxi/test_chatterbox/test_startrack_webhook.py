# pylint: disable=redefined-outer-name,too-many-arguments,too-many-lines
# pylint: disable=protected-access
import datetime

import bson
import pymongo
import pytest

from taxi.clients import startrack
from taxi.util import dates

from chatterbox.generated.service.config import plugin as config
from test_chatterbox import plugins as conftest


NOW = datetime.datetime(2018, 6, 15, 12, 34)
CLIENT_ID = str(config.Config.STARTRACK_EMAIL_USER_ID)
SUPPORT_ID = str(config.Config.STARTRACK_SUPPORT_USER_ID)


@pytest.mark.config(
    CHATTERBOX_LINES={
        'mail': {
            'name': 'First line',
            'priority': 2,
            'sort_order': 1,
            'autoreply': False,
        },
        'second': {
            'name': 'Second line',
            'priority': 1,
            'sort_order': 2,
            'autoreply': False,
            'conditions': {'fields/queue': 'another_queue'},
        },
    },
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'user_email': 'emails',
            'driver_license': 'driver_licenses',
            'driver_phone': 'phones',
            'park_phone': 'phones',
            'park_email': 'emails',
        },
    },
)
@pytest.mark.parametrize(
    'data, ticket_status, tags, custom_fields, '
    'expected_line, expected_status,expected_tags, expected_meta,'
    'delete_emails',
    [
        (
            {'ticket': 'some_queue-1'},
            'open',
            ['email_task'],
            None,
            'mail',
            'predispatch',
            ['email_task'],
            {
                'queue': 'some_queue',
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'ticket_subject': 'some summary',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
                'support_email': 'test@support',
            },
            False,
        ),
        (
            {'ticket': 'some_queue-1'},
            'open',
            ['email_task'],
            {
                'add_user_email': 'changed_user_email@mail.ru',
                'add_support_email': 'changed_support_email@mail.ru',
            },
            'mail',
            'predispatch',
            ['email_task'],
            {
                'queue': 'some_queue',
                'ticket_subject': 'some summary',
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
                'support_email': 'test@support',
            },
            False,
        ),
        (
            {'ticket': 'some_queue-1'},
            'open',
            ['email_task'],
            {
                'add_user_email': 'changed_user_email@mail.ru',
                'add_support_email': 'changed_support_email@mail.ru',
            },
            'mail',
            'predispatch',
            ['email_task'],
            {
                'queue': 'some_queue',
                'ticket_subject': 'some summary',
                'user_email': 'changed_user_email@mail.ru',
                'user_email_pd_id': 'test_pd_id',
                'support_email': 'changed_support_email@mail.ru',
            },
            True,
        ),
        (
            {'ticket': 'another_queue-2'},
            'open',
            ['email_task'],
            {
                'OrderId': 'some_order_id',
                'paymentType': 'cash',
                'userType': 'general',
                'userEmail': 'some_client@email',
                'userPhone': 'some_user_phone',
                'userPlatform': 'android',
                'appVersion': '2.0',
                'city': 'Moscow',
                'driverLicense': 'some_driver_license',
                'driverPhone': 'some_driver_phone',
                'coupon': 'some_promocode',
                'couponUsed': 'False',
                'tariff': 'econom',
                'webhookStatus': 'pending',
                'mlSuggestions': '[]',
            },
            'second',
            'reopened',
            ['more', 'tags', 'email_task'],
            {
                'order_id': 'some_order_id',
                'payment_type': 'cash',
                'queue': 'another_queue',
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'ticket_subject': 'some summary',
                'support_email': 'test@support',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
                'user_type': 'general',
                'user_phone': 'some_user_phone',
                'user_phone_pd_id': 'phone_pd_id_7',
                'user_platform': 'android',
                'app_version': '2.0',
                'city': 'moscow',
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'driver_phone': 'some_driver_phone',
                'driver_phone_pd_id': 'phone_pd_id_8',
                'coupon': 'some_promocode',
                'coupon_used': 'False',
                'tariff': 'econom',
            },
            False,
        ),
        (
            {'ticket': 'another_queue-3'},
            'closed',
            ['email_task'],
            {
                'OrderId': 'some_order_id',
                'paymentType': 'cash',
                'userType': 'general',
                'userEmail': 'some_client@email',
                'userPhone': 'some_user_phone',
                'userPlatform': 'android',
                'appVersion': '2.0',
                'city': 'Moscow',
                'driverLicense': 'some_driver_license',
                'driverPhone': 'some_driver_phone',
                'coupon': 'some_promocode',
                'couponUsed': 'False',
                'tariff': 'econom',
                'webhookStatus': 'pending',
                'mlSuggestions': '[]',
            },
            'mail',
            'ready_to_archive',
            ['email_task'],
            {
                'order_id': 'some_order_id',
                'ask_csat': False,
                'payment_type': 'cash',
                'queue': 'another_queue',
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'ticket_subject': 'some summary',
                'support_email': 'test@support',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
                'user_type': 'general',
                'user_phone': 'some_user_phone',
                'user_phone_pd_id': 'phone_pd_id_7',
                'user_platform': 'android',
                'app_version': '2.0',
                'city': 'moscow',
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'driver_phone': 'some_driver_phone',
                'driver_phone_pd_id': 'phone_pd_id_8',
                'coupon': 'some_promocode',
                'coupon_used': 'False',
                'tariff': 'econom',
            },
            False,
        ),
        (
            {'ticket': 'another_queue-3'},
            'closed',
            ['email_task'],
            {
                'OrderId': 'some_order_id',
                'paymentType': 'cash',
                'userType': 'general',
                'userEmail': 'some_client@email',
                'userPhone': {
                    'display': '+7 977 887-57-63',
                    'formatE164': '+79778875763',
                    'value': '+7 977 887 57 63',
                },
                'userPlatform': 'android',
                'appVersion': '2.0',
                'city': 'Moscow',
                'driverLicense': 'some_driver_license',
                'driverPhone': 'some_driver_phone',
                'coupon': 'some_promocode',
                'couponUsed': 'False',
                'tariff': 'econom',
                'webhookStatus': 'pending',
                'mlSuggestions': '[]',
            },
            'mail',
            'ready_to_archive',
            ['email_task'],
            {
                'order_id': 'some_order_id',
                'ask_csat': False,
                'payment_type': 'cash',
                'queue': 'another_queue',
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'ticket_subject': 'some summary',
                'support_email': 'test@support',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
                'user_type': 'general',
                'user_phone': '+79778875763',
                'user_phone_pd_id': 'test_pd_id',
                'user_platform': 'android',
                'app_version': '2.0',
                'city': 'moscow',
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'driver_phone': 'some_driver_phone',
                'driver_phone_pd_id': 'phone_pd_id_8',
                'coupon': 'some_promocode',
                'coupon_used': 'False',
                'tariff': 'econom',
            },
            False,
        ),
        (
            {'ticket': 'another_queue-4'},
            'closed',
            ['email_task'],
            {'clientThematic': ['client_thematic']},
            'mail',
            'ready_to_archive',
            ['email_task'],
            {
                'client_thematic': 'client_thematic',
                'ask_csat': False,
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'queue': 'another_queue',
                'support_email': 'test@support',
                'ticket_subject': 'some summary',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
            },
            False,
        ),
        (
            {'ticket': 'another_queue-5'},
            'closed',
            ['email_task'],
            {'clientThematic': ['client_thematic_1', 'client_thematic_2']},
            'mail',
            'ready_to_archive',
            ['email_task'],
            {
                'ask_csat': False,
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'queue': 'another_queue',
                'support_email': 'test@support',
                'ticket_subject': 'some summary',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
            },
            False,
        ),
        (
            {'ticket': 'another_queue-2', 'keep_task_status': True},
            'closed',
            ['email_task'],
            {
                'OrderId': 'some_order_id',
                'paymentType': 'cash',
                'userType': 'general',
                'userEmail': 'some_client@email',
                'userPhone': 'some_user_phone',
                'userPlatform': 'android',
                'appVersion': '2.0',
                'city': 'Moscow',
                'driverLicense': 'some_driver_license',
                'driverPhone': 'some_driver_phone',
                'coupon': 'some_promocode',
                'couponUsed': 'False',
                'tariff': 'econom',
                'webhookStatus': 'pending',
                'mlSuggestions': '[]',
                'csatValue': 1,
            },
            'second',
            'waiting',
            ['more', 'tags', 'email_task'],
            {
                'order_id': 'some_order_id',
                'payment_type': 'cash',
                'queue': 'another_queue',
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'ticket_subject': 'some summary',
                'support_email': 'test@support',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
                'user_type': 'general',
                'user_phone': 'some_user_phone',
                'user_phone_pd_id': 'phone_pd_id_7',
                'user_platform': 'android',
                'app_version': '2.0',
                'city': 'moscow',
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'driver_phone': 'some_driver_phone',
                'driver_phone_pd_id': 'phone_pd_id_8',
                'coupon': 'some_promocode',
                'coupon_used': 'False',
                'tariff': 'econom',
                'csat_value': 'horrible',
            },
            False,
        ),
        (
            {'ticket': 'another_queue-2', 'keep_task_status': True},
            'closed',
            ['email_task'],
            {
                'OrderId': 'some_order_id',
                'paymentType': 'cash',
                'userType': 'general',
                'userEmail': 'some_client@email',
                'userPhone': 'some_user_phone',
                'userPlatform': 'android',
                'appVersion': '2.0',
                'city': 'Moscow',
                'driverLicense': 'some_driver_license',
                'driverPhone': 'some_driver_phone',
                'coupon': 'some_promocode',
                'couponUsed': 'False',
                'tariff': 'econom',
                'webhookStatus': 'pending',
                'mlSuggestions': '[]',
                'csatValue': 10,
            },
            'second',
            'waiting',
            ['more', 'tags', 'email_task'],
            {
                'order_id': 'some_order_id',
                'payment_type': 'cash',
                'queue': 'another_queue',
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'ticket_subject': 'some summary',
                'support_email': 'test@support',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
                'user_type': 'general',
                'user_phone': 'some_user_phone',
                'user_phone_pd_id': 'phone_pd_id_7',
                'user_platform': 'android',
                'app_version': '2.0',
                'city': 'moscow',
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'driver_phone': 'some_driver_phone',
                'driver_phone_pd_id': 'phone_pd_id_8',
                'coupon': 'some_promocode',
                'coupon_used': 'False',
                'tariff': 'econom',
            },
            False,
        ),
        (
            {'ticket': 'another_queue-10', 'keep_task_status': True},
            'closed',
            ['email_task'],
            {
                'OrderId': 'some_order_id',
                'paymentType': 'cash',
                'userType': 'general',
                'userEmail': 'some_client@email',
                'userPhone': 'some_user_phone',
                'userPlatform': 'android',
                'appVersion': '2.0',
                'city': 'Moscow',
                'driverLicense': 'some_driver_license',
                'driverPhone': 'some_driver_phone',
                'coupon': 'some_promocode',
                'couponUsed': 'False',
                'tariff': 'econom',
                'webhookStatus': 'pending',
                'mlSuggestions': '[]',
                'csatValue': 1,
            },
            'mail',
            'archived',
            ['more', 'tags', 'email_task'],
            {
                'order_id': 'some_order_id',
                'payment_type': 'cash',
                'queue': 'another_queue',
                'copy_to_emails': [
                    'toert@yandex-team',
                    'clinically@insane.me',
                ],
                'ticket_subject': 'some summary',
                'support_email': 'test@support',
                'user_email': 'some_client@email',
                'user_email_pd_id': 'email_pd_id_1',
                'user_type': 'general',
                'user_phone': 'some_user_phone',
                'user_phone_pd_id': 'phone_pd_id_7',
                'user_platform': 'android',
                'app_version': '2.0',
                'city': 'moscow',
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'driver_phone': 'some_driver_phone',
                'driver_phone_pd_id': 'phone_pd_id_8',
                'coupon': 'some_promocode',
                'coupon_used': 'False',
                'tariff': 'econom',
                'csat_value': 'horrible',
            },
            False,
        ),
    ],
)
async def test_startrack_task(
        cbox,
        db,
        mock_st_get_ticket_with_status,
        mock_st_get_all_attachments,
        mock_st_update_ticket,
        mock_st_get_comments,
        mock_personal,
        data,
        ticket_status,
        tags,
        custom_fields,
        expected_line,
        expected_status,
        expected_tags,
        expected_meta,
        delete_emails,
):
    if delete_emails:
        data_constructor = conftest.construct_ticket_without_emails
    else:
        data_constructor = conftest.construct_ticket_with_cc
    mocked_get_ticket = mock_st_get_ticket_with_status(
        status=ticket_status,
        tags=tags,
        custom_fields=custom_fields,
        data_constructor=data_constructor,
    )
    update_mock = mock_st_update_ticket(ticket_status)
    mock_st_get_comments([])
    mock_st_get_all_attachments(empty=True)
    await cbox.post(
        '/v1/webhooks/startrack_task',
        data=data,
        headers={'X-ChatterBox-API-Key': conftest.CHATTERBOX_API_KEY_TAXI},
    )
    assert cbox.status == 200
    task = await db.support_chatterbox.find_one(
        {'external_id': data['ticket']},
    )
    assert task
    assert task['chat_type'] == 'startrack'
    assert task['line'] == expected_line
    assert task['status'] == expected_status
    assert task['tags'] == expected_tags
    expected_meta.update({'webhook_calls': 1})
    assert task['meta_info'] == expected_meta

    get_ticket_call = mocked_get_ticket.calls[0]
    assert get_ticket_call['ticket'] == data['ticket']

    update_ticket_call = update_mock.calls[0]
    assert update_ticket_call['ticket'] == data['ticket']
    assert update_ticket_call['kwargs'] == {
        'custom_fields': {
            'chatterboxId': str(task['_id']),
            'webhookStatus': 'finished',
        },
    }


@pytest.mark.parametrize(
    'ticket, status, comments, expected_source',
    [
        (
            'some_queue-1',
            'open',
            [],
            {
                'id': 'some_queue-1',
                'type': 'startrack',
                'metadata': {
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': CLIENT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': CLIENT_ID},
                    'summary': 'some summary',
                    'description': 'some description',
                    'key': 'some_queue-1',
                    'queue': {'key': 'some_queue'},
                    'status': {'key': 'open'},
                    'last_message_from_user': True,
                    'ask_csat': False,
                    'emailFrom': 'some_client@email',
                    'emailTo': ['test@support'],
                    'emailCreatedBy': 'test@support',
                    'reopen_external': True,
                },
                'participants': [
                    {'id': CLIENT_ID, 'role': 'client'},
                    {'id': SUPPORT_ID, 'role': 'support'},
                ],
                'status': {'is_open': True, 'is_visible': True},
            },
        ),
        (
            'another_queue-2',
            'closed',
            [
                {
                    'id': 'some_comment_id',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some reply',
                    'email': {'some': 'email'},
                },
            ],
            {
                'id': 'another_queue-2',
                'type': 'startrack',
                'metadata': {
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': CLIENT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': CLIENT_ID},
                    'summary': 'some summary',
                    'description': 'some description',
                    'key': 'another_queue-2',
                    'queue': {'key': 'another_queue'},
                    'status': {'key': 'closed'},
                    'last_message_from_user': False,
                    'ask_csat': False,
                    'emailFrom': 'some_client@email',
                    'emailTo': ['test@support'],
                    'emailCreatedBy': 'test@support',
                    'reopen_external': True,
                },
                'participants': [
                    {'id': CLIENT_ID, 'role': 'client'},
                    {'id': SUPPORT_ID, 'role': 'support'},
                ],
                'status': {'is_open': False, 'is_visible': False},
            },
        ),
        (
            'another_queue-3',
            'open',
            [
                {
                    'id': 'some_comment_id',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some reply',
                    'email': {
                        'some': 'email',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                },
                {
                    'id': 'some_comment_id',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': CLIENT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': CLIENT_ID},
                    'text': 'reopen comment',
                    'email': {
                        'some': 'email',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                },
            ],
            {
                'id': 'another_queue-3',
                'type': 'startrack',
                'metadata': {
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': CLIENT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': CLIENT_ID},
                    'summary': 'some summary',
                    'description': 'some description',
                    'key': 'another_queue-3',
                    'queue': {'key': 'another_queue'},
                    'status': {'key': 'open'},
                    'last_message_from_user': True,
                    'ask_csat': False,
                    'emailFrom': 'some_client@email',
                    'emailTo': ['test@support'],
                    'emailCreatedBy': 'test@support',
                    'reopen_external': True,
                },
                'participants': [
                    {'id': CLIENT_ID, 'role': 'client'},
                    {'id': SUPPORT_ID, 'role': 'support'},
                ],
                'status': {'is_open': True, 'is_visible': True},
            },
        ),
    ],
)
async def test_get_source(
        cbox,
        mock_st_get_ticket_with_status,
        mock_st_get_comments,
        ticket,
        status,
        comments,
        expected_source,
):
    mocked_get_comments = mock_st_get_comments(comments)
    mock_st_get_ticket_with_status(status)
    source = await cbox.app.task_source_manager.get_related_source(
        task_type='startrack', external_id=ticket,
    )
    assert source == expected_source
    get_comments_call = mocked_get_comments.calls[0]
    assert get_comments_call['kwargs']['per_page'] == 2000


@pytest.mark.parametrize(
    'comments, task_history, expected_messages, attachments_response',
    [
        (
            [],
            [],
            {
                'messages': [
                    {
                        'id': '0',
                        'sender': {'id': CLIENT_ID, 'role': 'client'},
                        'text': 'some description',
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'ticket_subject': 'some summary',
                            'attachments': [
                                {
                                    'created_at': (
                                        '2018-12-12T14:11:15.643+0000'
                                    ),
                                    'id': '12',
                                    'link': (
                                        'https://tracker.yandex.ru/'
                                        'some_queue-1/attachments/12?orgid=1'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': (
                                        'Screen Shot 2018-10-26 '
                                        'at 12.54.39.png'
                                    ),
                                    'size': 35188,
                                },
                            ],
                        },
                    },
                ],
                'total': 1,
                'hidden_comments': [],
                'newest_message_id': '0',
            },
            [
                {
                    'id': '12',
                    'size': 35188,
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Screen Shot 2018-10-26 at 12.54.39.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
            ],
        ),
        (
            [
                {
                    'id': 'some_comment_id',
                    'longId': 'long_comment_id_1',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some_login написал письмо',
                    'email': {
                        'text': 'some reply',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                    'type': 'outgoing',
                    'transport': 'email',
                },
                {
                    'id': 'some_inner_comment_id',
                    'longId': 'long_comment_id_2',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID, 'display': 'Support name'},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some inner comment',
                },
                {
                    'id': 'some_comment_id',
                    'longId': 'long_comment_id_3',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': CLIENT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': CLIENT_ID},
                    'text': 'some new message',
                },
            ],
            [],
            {
                'messages': [
                    {
                        'id': '0',
                        'sender': {'id': CLIENT_ID, 'role': 'client'},
                        'text': 'some description',
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'ticket_subject': 'some summary',
                        },
                    },
                    {
                        'id': 'some_comment_id',
                        'sender': {'id': SUPPORT_ID, 'role': 'support'},
                        'text': (
                            'От: chatterbox@yandex.ru\r\n'
                            'Кому: client@gmail.com\r\n'
                            'Тема: Subject\r\n\n'
                            'some reply'
                        ),
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'attachments': [
                                {
                                    'created_at': (
                                        '2018-12-12T14:11:15.643+0000'
                                    ),
                                    'id': '12',
                                    'link': (
                                        'https://tracker.yandex.ru/'
                                        'some_queue-1/attachments/12?orgid=1'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': (
                                        'Screen Shot 2018-10-26 '
                                        'at 12.54.39.png'
                                    ),
                                    'size': 35188,
                                },
                            ],
                        },
                    },
                    {
                        'id': 'some_comment_id',
                        'sender': {'id': CLIENT_ID, 'role': 'client'},
                        'text': 'some new message',
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                        },
                    },
                ],
                'total': 3,
                'hidden_comments': [
                    {
                        'comment': 'some inner comment',
                        'created': dates.parse_timestring(
                            '2018-01-02T03:45:00.000Z',
                        ),
                        'external_comment_id': 'some_inner_comment_id',
                        'login': 'Support name',
                    },
                ],
                'newest_message_id': 'some_comment_id',
            },
            [
                {
                    'id': '12',
                    'size': 35188,
                    'commentId': 'long_comment_id_1',
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Screen Shot 2018-10-26 at 12.54.39.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
            ],
        ),
        (
            [
                {
                    'id': 'some_defer_id',
                    'longId': 'long_some_defer_id',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some_login написал письмо',
                    'email': {
                        'text': 'some defer',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                    'type': 'outgoing',
                    'transport': 'email',
                },
                {
                    'id': 'some_comment_id',
                    'longId': 'long_some_comment_id_1',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some_login написал письмо',
                    'email': {
                        'text': 'some comment',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                    'type': 'outgoing',
                    'transport': 'email',
                },
                {
                    'id': 'some_comment_id',
                    'longId': 'long_some_comment_id_2',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': CLIENT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': CLIENT_ID},
                    'text': (
                        'some new message '
                        'with card number 11 11  22 2 - 2333- - 3444  4'
                    ),
                },
                {
                    'id': 'some_close_id',
                    'longId': 'long_some_close_id',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some_login написал письмо',
                    'email': {
                        'text': 'some close',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                    'type': 'outgoing',
                    'transport': 'email',
                },
            ],
            [
                {
                    'action': 'defer',
                    'comment': 'some defer',
                    'login': 'support1',
                },
                {
                    'action': 'comment',
                    'comment': 'some comment',
                    'login': 'support2',
                },
                {
                    'action': 'close',
                    'comment': 'some close',
                    'login': 'support3',
                },
            ],
            {
                'messages': [
                    {
                        'id': '0',
                        'sender': {'id': CLIENT_ID, 'role': 'client'},
                        'text': 'some description',
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'ticket_subject': 'some summary',
                            'attachments': [
                                {
                                    'created_at': (
                                        '2018-12-12T14:11:15.643+0000'
                                    ),
                                    'id': '0',
                                    'link': (
                                        'https://tracker.yandex.ru/'
                                        'some_queue-1/attachments/0?orgid=1'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'Base.png',
                                    'size': 35188,
                                },
                            ],
                        },
                    },
                    {
                        'id': 'some_defer_id',
                        'sender': {'id': 'support1', 'role': 'support'},
                        'text': (
                            'От: chatterbox@yandex.ru\r\n'
                            'Кому: client@gmail.com\r\n'
                            'Тема: Subject\r\n\n'
                            'some defer'
                        ),
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'attachments': [
                                {
                                    'created_at': (
                                        '2018-12-12T14:11:15.643+0000'
                                    ),
                                    'id': '12',
                                    'link': (
                                        'https://tracker.yandex.ru/'
                                        'some_queue-1/attachments/12?orgid=1'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': (
                                        'Screen Shot 2018-10-26 '
                                        'at 12.54.39.png'
                                    ),
                                    'size': 35188,
                                },
                            ],
                        },
                    },
                    {
                        'id': 'some_comment_id',
                        'sender': {'id': 'support2', 'role': 'support'},
                        'text': (
                            'От: chatterbox@yandex.ru\r\n'
                            'Кому: client@gmail.com\r\n'
                            'Тема: Subject\r\n\n'
                            'some comment'
                        ),
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'attachments': [
                                {
                                    'created_at': (
                                        '2018-12-12T14:11:15.643+0000'
                                    ),
                                    'id': '13',
                                    'link': (
                                        'https://tracker.yandex.ru/'
                                        'some_queue-1/attachments/13?orgid=1'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'Answer.png',
                                    'size': 35188,
                                },
                                {
                                    'created_at': (
                                        '2018-12-12T14:11:15.643+0000'
                                    ),
                                    'id': '14',
                                    'link': (
                                        'https://tracker.yandex.ru/'
                                        'some_queue-1/attachments/14?orgid=1'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'Answer2.png',
                                    'size': 35188,
                                },
                            ],
                        },
                    },
                    {
                        'id': 'some_comment_id',
                        'sender': {'id': CLIENT_ID, 'role': 'client'},
                        'text': (
                            'some new message '
                            'with card number 111122******4444'
                        ),
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                        },
                    },
                    {
                        'id': 'some_close_id',
                        'sender': {'id': 'support3', 'role': 'support'},
                        'text': (
                            'От: chatterbox@yandex.ru\r\n'
                            'Кому: client@gmail.com\r\n'
                            'Тема: Subject\r\n\n'
                            'some close'
                        ),
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                        },
                    },
                ],
                'total': 5,
                'hidden_comments': [],
                'newest_message_id': 'some_close_id',
            },
            [
                {
                    'id': '12',
                    'commentId': 'long_some_defer_id',
                    'size': 35188,
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Screen Shot 2018-10-26 at 12.54.39.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
                {
                    'id': '13',
                    'commentId': 'long_some_comment_id_1',
                    'size': 35188,
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Answer.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
                {
                    'id': '0',
                    'size': 35188,
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Base.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
                {
                    'id': '14',
                    'commentId': 'long_some_comment_id_1',
                    'size': 35188,
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Answer2.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
            ],
        ),
        (
            [
                {
                    # this id will be in history
                    'id': 1,
                    'longId': 'long_1',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some_login написал письмо',
                    'email': {
                        'text': 'some defer',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                    'type': 'outgoing',
                    'transport': 'email',
                },
                {
                    # this id won't be in history
                    'id': 2,
                    'longId': 'long_2',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some_login написал письмо',
                    'email': {
                        'text': 'some comment',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                    'type': 'outgoing',
                    'transport': 'email',
                },
                {
                    # this id will be in history
                    'id': 3,
                    'longId': 'long_3',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': (
                        'some new message '
                        'with card number 11 11  22 2 - 2333- - 3444  4'
                    ),
                    'email': {
                        'text': 'some comment',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                    'type': 'outgoing',
                    'transport': 'email',
                },
                {
                    'id': 4,
                    'longId': 'long_4',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some_login написал письмо',
                    'email': {
                        'text': 'some external_comment',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                    'type': 'outgoing',
                    'transport': 'email',
                },
            ],
            [
                # swapped first and third comments
                {
                    'action': 'close',
                    'comment': 'some close',
                    'login': 'support3',
                    'external_id': '3',
                },
                {
                    'action': 'comment',
                    'comment': 'some comment',
                    'login': 'support2',
                },
                {
                    'action': 'defer',
                    'comment': 'some defer',
                    'login': 'support1',
                    'external_id': '1',
                },
                {
                    'action': 'external_comment',
                    'comment': 'some external_comment',
                    'login': 'support4',
                    'external_id': '4',
                },
            ],
            {
                'messages': [
                    {
                        'id': '0',
                        'sender': {'id': CLIENT_ID, 'role': 'client'},
                        'text': 'some description',
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'ticket_subject': 'some summary',
                        },
                    },
                    {
                        'id': '1',
                        'sender': {'id': 'support1', 'role': 'support'},
                        'text': (
                            'От: chatterbox@yandex.ru\r\n'
                            'Кому: client@gmail.com\r\n'
                            'Тема: Subject\r\n\n'
                            'some defer'
                        ),
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'attachments': [
                                {
                                    'created_at': (
                                        '2018-12-12T14:11:15.643+0000'
                                    ),
                                    'id': '12',
                                    'link': (
                                        'https://tracker.yandex.ru/'
                                        'some_queue-1/attachments/12?orgid=1'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': (
                                        'Screen Shot 2018-10-26 '
                                        'at 12.54.39.png'
                                    ),
                                    'size': 35188,
                                },
                            ],
                        },
                    },
                    {
                        'id': '2',
                        'sender': {'id': 'support2', 'role': 'support'},
                        'text': (
                            'От: chatterbox@yandex.ru\r\n'
                            'Кому: client@gmail.com\r\n'
                            'Тема: Subject\r\n\n'
                            'some comment'
                        ),
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                        },
                    },
                    {
                        'id': '3',
                        'sender': {'id': 'support3', 'role': 'support'},
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                        },
                        'text': (
                            'От: chatterbox@yandex.ru\r\n'
                            'Кому: client@gmail.com\r\n'
                            'Тема: Subject\r\n\n'
                            'some comment'
                        ),
                    },
                    {
                        'id': '4',
                        'sender': {'id': 'support4', 'role': 'support'},
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                        },
                        'text': (
                            'От: chatterbox@yandex.ru\r\n'
                            'Кому: client@gmail.com\r\n'
                            'Тема: Subject\r\n\n'
                            'some external_comment'
                        ),
                    },
                ],
                'total': 5,
                'hidden_comments': [],
                'newest_message_id': '4',
            },
            [
                {
                    'id': '12',
                    'commentId': 'long_1',
                    'size': 35188,
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Screen Shot 2018-10-26 at 12.54.39.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
            ],
        ),
        (
            [
                {
                    'id': 'some_comment_id',
                    'longId': 'long_some_comment_id',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {
                        'id': SUPPORT_ID,
                        'display': 'Саппорт из тестинга',
                    },
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some_login написал письмо',
                    'email': {
                        'text': 'some reply',
                        'info': {
                            'from': 'chatterbox@yandex.ru',
                            'to': ['client@gmail.com'],
                        },
                        'subject': 'Subject',
                    },
                    'type': 'outgoing',
                    'transport': 'email',
                },
                {
                    'id': 'some_new_comment_id',
                    'longId': 'long_some_new_comment_id',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': CLIENT_ID},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': CLIENT_ID},
                    'text': 'some new message',
                },
                {
                    'id': 'some_hidden_comment',
                    'longId': 'long_hidden_comment',
                    'createdAt': '2018-01-02T03:45:00.000Z',
                    'createdBy': {'id': SUPPORT_ID, 'display': 'hidden_supp'},
                    'updatedAt': '2018-01-02T03:45:00.000Z',
                    'updatedBy': {'id': SUPPORT_ID},
                    'text': 'some new message',
                },
            ],
            [
                {
                    'action': 'comment',
                    'comment': 'some new message',
                    'external_id': 'some_new_comment_id',
                    'reply_to': ['0', 'some_comment_id'],
                },
            ],
            {
                'messages': [
                    {
                        'id': '0',
                        'sender': {'id': CLIENT_ID, 'role': 'client'},
                        'text': 'some description',
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'ticket_subject': 'some summary',
                            'attachments': [
                                {
                                    'created_at': (
                                        '2018-12-12T14:11:15.643+0000'
                                    ),
                                    'id': '13',
                                    'link': (
                                        'https://tracker.yandex.ru/'
                                        'some_queue-1/attachments/13?orgid=1'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': (
                                        'Screen Shot 2018-10-26 '
                                        'at 12.54.39.png'
                                    ),
                                    'size': 3518,
                                },
                            ],
                        },
                    },
                    {
                        'id': 'some_comment_id',
                        'sender': {'id': SUPPORT_ID, 'role': 'support'},
                        'text': (
                            'От: chatterbox@yandex.ru\r\n'
                            'Кому: client@gmail.com\r\n'
                            'Тема: Subject\r\n\n'
                            'some reply'
                        ),
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'attachments': [
                                {
                                    'created_at': (
                                        '2018-12-12T14:11:15.643+0000'
                                    ),
                                    'id': '12',
                                    'link': (
                                        'https://tracker.yandex.ru/'
                                        'some_queue-1/attachments/12?orgid=1'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': (
                                        'Screen Shot 2018-10-26 '
                                        'at 12.54.39.png'
                                    ),
                                    'size': 35188,
                                },
                            ],
                        },
                    },
                    {
                        'id': 'some_new_comment_id',
                        'sender': {'id': CLIENT_ID, 'role': 'client'},
                        'text': 'some new message',
                        'metadata': {
                            'created': '2018-01-02T03:45:00.000Z',
                            'updated': '2018-01-02T03:45:00.000Z',
                            'reply_to': ['0', 'some_comment_id'],
                        },
                    },
                ],
                'total': 3,
                'hidden_comments': [
                    {
                        'comment': 'some new message',
                        'created': dates.parse_timestring(
                            '2018-01-02T03:45:00.000Z',
                        ),
                        'external_comment_id': 'some_hidden_comment',
                        'login': 'hidden_supp',
                    },
                ],
                'newest_message_id': 'some_new_comment_id',
            },
            [
                {
                    'id': '12',
                    'commentId': 'long_some_comment_id',
                    'size': 35188,
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Screen Shot 2018-10-26 at 12.54.39.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
                {
                    'id': '13',
                    'commentId': 'long_hidden_comment',
                    'size': 3518,
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Screen Shot 2018-10-26 at 12.54.39.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
            ],
        ),
    ],
)
@pytest.mark.parametrize('profile', [None, 'support-taxi'])
async def test_get_comments(
        cbox,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        comments,
        task_history,
        expected_messages,
        attachments_response,
        profile,
):
    mock_st_get_all_attachments(response=attachments_response)
    mocked_get_comments = mock_st_get_comments(comments)
    task = {
        '_id': 1,
        'type': 'startrack',
        'external_id': 'some_queue-1',
        'meta_info': {'user_email': 'client@gmail.com'},
    }
    if task_history:
        task['history'] = task_history
    messages = await cbox.app.task_source_manager.get_messages(task)
    assert messages == expected_messages
    get_comments_call = mocked_get_comments.calls[0]
    assert get_comments_call['kwargs']['per_page'] == 2000


async def test_get_comments_empty_ticket(
        cbox, monkeypatch, mock_st_get_comments, mock_st_get_all_attachments,
):
    async def _dummy_get_ticket(self, ticket, profile=None):
        queue, _ = ticket.split('-')
        return {
            'key': ticket,
            'queue': {'key': queue},
            'status': {'key': 'open'},
            'createdAt': '2018-01-02T03:45:00.000Z',
            'createdBy': {'id': CLIENT_ID},
            'updatedAt': '2018-01-02T03:45:00.000Z',
            'updatedBy': {'id': SUPPORT_ID},
            'summary': 'some summary',
            'emailFrom': 'some_client@email',
            'emailTo': ['test@support'],
            'emailCreatedBy': 'test@support',
        }

    monkeypatch.setattr(
        startrack.StartrackAPIClient, 'get_ticket', _dummy_get_ticket,
    )

    mock_st_get_all_attachments()
    mock_st_get_comments([])
    task = {'_id': 1, 'type': 'startrack', 'external_id': 'some_queue-1'}
    messages = await cbox.app.task_source_manager.get_messages(task)
    assert messages == {
        'messages': [
            {
                'id': '0',
                'sender': {'id': CLIENT_ID, 'role': 'client'},
                'text': 'some summary',
                'metadata': {
                    'created': '2018-01-02T03:45:00.000Z',
                    'updated': '2018-01-02T03:45:00.000Z',
                    'ticket_subject': 'some summary',
                },
            },
        ],
        'total': 1,
        'hidden_comments': [],
        'newest_message_id': '0',
    }


@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'user_email': 'emails'},
    },
)
@pytest.mark.parametrize(
    'ticket, text, tags',
    [
        ('some_queue-1', 'some text', []),
        ('another_queue-2', 'other text', ['tag1', 'tag2']),
    ],
)
async def test_put_message(
        cbox,
        mock_st_create_comment,
        mock_st_update_ticket,
        mock_personal,
        ticket,
        text,
        tags,
):
    st_update_ticket_request = mock_st_update_ticket('open')
    task = {
        'type': 'startrack',
        'external_id': ticket,
        'meta_info': {
            'user_email_pd_id': 'email_pd_id_1',
            'support_email': 'some@support',
            'ticket_subject': 'Some ticket subject',
        },
        'tags': [],
    }
    await cbox.app.task_source_manager.put_message(
        task, tags, 'some_login', text, {}, 'pending',
    )
    create_comment_call = mock_st_create_comment.calls[0]
    assert create_comment_call['args'] == (ticket,)
    create_comment_call['kwargs'].pop('log_extra')
    assert create_comment_call['kwargs'] == {
        'text': 'some_login написал письмо',
        'email_from': 'some@support',
        'email_to': 'some_client@email',
        'email_cc': [],
        'email_subject': 'Re: Some ticket subject',
        'email_text': text,
        'signature_selection': True,
        'attachment_ids': None,
    }
    st_update_ticket_call = st_update_ticket_request.calls[0]
    assert st_update_ticket_call['kwargs']['tags'] == tags


@pytest.mark.parametrize(
    'ticket, text',
    [
        ('some_queue-1', 'some text'),
        ('another_queue-2', 'other text'),
        ('closed-3', 'new text'),
    ],
)
async def test_close(
        cbox,
        mock_st_create_comment,
        mock_st_transition,
        mock_st_get_ticket_with_status,
        mock_st_update_ticket,
        ticket,
        text,
):
    mock_st_get_ticket_with_status('closed')
    mock_st_update_ticket('closed')
    task = {
        'meta_info': {
            'user_email': 'some_client@email',
            'support_email': 'some@support',
            'ticket_subject': 'Some ticket subject',
        },
        'type': 'startrack',
        'external_id': ticket,
        'tags': [],
    }
    await cbox.app.task_source_manager.close(
        task, login='some_login', comment=text, ticket_status='closed',
    )

    create_comment_call = mock_st_create_comment.calls[0]
    assert create_comment_call['args'] == (ticket,)
    create_comment_call['kwargs'].pop('log_extra')
    assert create_comment_call['kwargs'] == {
        'text': 'some_login написал письмо',
        'email_from': 'some@support',
        'email_to': 'some_client@email',
        'email_cc': [],
        'email_subject': 'Re: Some ticket subject',
        'email_text': text,
        'signature_selection': True,
        'attachment_ids': None,
    }

    execute_transition_call = mock_st_transition.calls[0]
    assert execute_transition_call['ticket'] == ticket
    assert execute_transition_call['kwargs'] == {
        'transition': 'close',
        'data': {'resolution': 'fixed'},
    }


async def test_race(
        cbox,
        db,
        monkeypatch,
        mock_st_get_ticket_with_status,
        mock_st_get_all_attachments,
        mock_st_update_ticket,
        mock_st_get_comments,
):
    async def _dummy_create(task_type, chat_type, external_id, login, profile):
        raise pymongo.errors.DuplicateKeyError('Oh shi~')

    class DummyFindByExternalId:
        old_func = cbox.app.tasks_manager._find_by_external_id
        already_called = False

        async def __call__(self, external_id, log_extra=None):
            if self.already_called:
                return await self.old_func(external_id, log_extra=log_extra)
            self.already_called = True
            return None

    monkeypatch.setattr(
        cbox.app.tasks_manager,
        '_find_by_external_id',
        DummyFindByExternalId(),
    )
    monkeypatch.setattr(cbox.app.tasks_manager, 'create', _dummy_create)

    mock_st_get_ticket_with_status(
        status='open',
        tags=[],
        custom_fields={},
        data_constructor=conftest.construct_ticket_with_cc,
    )
    mock_st_update_ticket('open')
    mock_st_get_comments([])
    mock_st_get_all_attachments(empty=True)
    await cbox.post(
        '/v1/webhooks/startrack_task',
        data={'ticket': 'another_queue-2'},
        headers={'X-ChatterBox-API-Key': conftest.CHATTERBOX_API_KEY_TAXI},
    )
    assert cbox.status == 200
    task = await db.support_chatterbox.find_one(
        {'external_id': 'another_queue-2'},
    )
    assert task
    assert task['chat_type'] == 'startrack'


@pytest.mark.parametrize(
    'data, api_key, external_id, expected_line',
    [
        (
            {'ticket': 'some_queue-1'},
            conftest.CHATTERBOX_API_KEY_TAXI,
            'some_queue-1',
            'mail',
        ),
        (
            {'ticket': 'some_queue-1'},
            conftest.CHATTERBOX_API_KEY_ZEN,
            'support-zen_some_queue-1',
            'support-zen_mail',
        ),
        (
            {'ticket': 'another_queue-1'},
            conftest.CHATTERBOX_API_KEY_ZEN,
            'support-zen_another_queue-1',
            'support-zen_mail',
        ),
    ],
)
async def test_startrack_task_profile(
        cbox,
        db,
        mock_st_get_ticket_with_status,
        mock_st_get_all_attachments,
        mock_st_update_ticket,
        mock_st_get_comments,
        data,
        api_key,
        external_id,
        expected_line,
):
    mock_st_get_ticket_with_status('closed')
    mock_st_update_ticket('closed')
    mock_st_get_comments([])
    mock_st_get_all_attachments(empty=True)
    await cbox.post(
        '/v1/webhooks/startrack_task',
        data=data,
        headers={'X-ChatterBox-API-Key': api_key},
    )
    assert cbox.status == 200
    task = await db.support_chatterbox.find_one({'external_id': external_id})
    assert task
    assert task['chat_type'] == 'startrack'
    assert task['line'] == expected_line


@pytest.mark.parametrize(
    ('data', 'api_key', 'external_id', 'expected_line', 'expected_status'),
    [
        (
            {'ticket': 'another_queue-11'},
            conftest.CHATTERBOX_API_KEY_TAXI,
            'another_queue-11',
            'mail',
            'archive_in_progress',
        ),
    ],
)
async def test_startrack_task_error(
        cbox,
        db,
        mock_st_get_ticket_with_status,
        mock_st_get_all_attachments,
        mock_st_update_ticket,
        mock_st_get_comments,
        data,
        api_key,
        external_id,
        expected_line,
        expected_status,
):
    mock_st_get_ticket_with_status('open')
    mock_st_update_ticket('open')
    mock_st_get_comments([])
    mock_st_get_all_attachments(empty=True)
    await cbox.post(
        '/v1/webhooks/startrack_task',
        data=data,
        headers={'X-ChatterBox-API-Key': api_key},
    )
    assert cbox.status == 409
    task = await db.support_chatterbox.find_one({'external_id': external_id})
    assert task
    assert task['chat_type'] == 'startrack'
    assert task['line'] == expected_line
    assert task['status'] == expected_status


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('chatterbox_id', ['5c3cbe6dc2683b986925d3b2'])
async def test_email_task(cbox, db, mock_chat_add_update, chatterbox_id):
    await cbox.post(
        '/v1/webhooks/email_task',
        data={'chatterbox_id': chatterbox_id},
        headers={'X-ChatterBox-API-Key': conftest.CHATTERBOX_API_KEY_TAXI},
    )
    task = await db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(chatterbox_id)},
    )
    assert task['status'] == 'reopened'
    assert task['history'][-1] == {
        'action': 'reopen',
        'created': NOW,
        'line': 'first',
        'login': 'superuser',
        'source': 'startrack',
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'chatterbox_id, profile, issue_id',
    [
        ('d535ac1da56e7e401e6dc800', 'yandex-team', 'APPREQUESTS-4212'),
        ('d535ac1da56e7e401e6dc801', 'yandex-team', 'CLAIMFF-1234'),
        ('d535ac1da56e7e401e6dc802', 'support-taxi', 'MARKETRETURNS-1234'),
    ],
)
async def test_tracker_link_webhook(
        cbox, db, api_keys, chatterbox_id, profile, issue_id,
):
    await cbox.post(
        '/v1/webhooks/tracker_link',
        data={'chatterbox_id': chatterbox_id, 'tracker_id': issue_id},
        headers={'X-ChatterBox-API-Key': api_keys[profile]},
    )
    task = await db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(chatterbox_id)},
    )
    gui_url = conftest.STARTRACK_EXTRA_TICKET_PROFILES[profile]['gui_url']
    issue_url = f'{gui_url}/{issue_id}'

    assert task['history'][-1] == {
        'action': 'tracker_link',
        'profile': profile,
        'issue_id': issue_id,
        'issue_url': issue_url,
        'line': 'reclaim',
        'created': NOW,
        'login': 'superuser',
        'hidden_comment': f'Issue linked: (({issue_url} {issue_id}))',
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'chatterbox_id, issue_id, status, expected_status',
    [
        (
            'd535ac1da56e7e401e6dc800',
            'APPREQUESTS-4212',
            'deferred',
            'reopened',
        ),
        ('d535ac1da56e7e401e6dc801', 'CLAIMFF-1234', 'closed', 'closed'),
    ],
)
async def test_tracker_update_webhook(
        cbox, db, chatterbox_id, issue_id, status, expected_status,
):
    task = await db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(chatterbox_id)},
    )
    assert task['status'] == status

    await cbox.post(
        '/v1/webhooks/tracker_update',
        data={'chatterbox_id': chatterbox_id, 'tracker_id': issue_id},
        headers={'X-ChatterBox-API-Key': conftest.CHATTERBOX_API_KEY_STARTREK},
    )
    task = await db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(chatterbox_id)},
    )
    assert task['status'] == expected_status

    profile = 'yandex-team'
    gui_url = conftest.STARTRACK_EXTRA_TICKET_PROFILES[profile]['gui_url']
    issue_url = f'{gui_url}/{issue_id}'
    assert task['history'][-1] == {
        'action': 'tracker_update',
        'profile': profile,
        'issue_id': issue_id,
        'issue_url': issue_url,
        'line': 'reclaim',
        'created': NOW,
        'login': 'superuser',
        'hidden_comment': f'Issue updated: (({issue_url} {issue_id}))',
    }


@pytest.mark.parametrize(
    'chatterbox_id, expected_code',
    [
        ('d535ac1da56e7e401e6dc800', 200),
        ('', 400),
        ('1234567', 400),
        ('invalid string', 400),
    ],
)
async def test_tracker_webhooks(cbox, chatterbox_id, expected_code):
    await cbox.post(
        '/v1/webhooks/tracker_update',
        data={'chatterbox_id': chatterbox_id, 'tracker_id': 'TEST-1'},
        headers={'X-ChatterBox-API-Key': conftest.CHATTERBOX_API_KEY_STARTREK},
    )
    assert cbox.status == expected_code

    await cbox.post(
        '/v1/webhooks/tracker_link',
        data={'chatterbox_id': chatterbox_id, 'tracker_id': 'TEST-2'},
        headers={'X-ChatterBox-API-Key': conftest.CHATTERBOX_API_KEY_STARTREK},
    )
    assert cbox.status == expected_code
