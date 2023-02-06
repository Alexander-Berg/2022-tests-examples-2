# pylint: disable=protected-access
import copy
import json

import asynctest
import pytest

from client_order_core import helper as order_core_helper

from taxi_safety_center import const
from taxi_safety_center import models
from taxi_safety_center.generated.service.swagger.models import api
from taxi_safety_center.generated.web import web_context
from taxi_safety_center.logic.share.action import getter

SHARE_URL = '/4.0/safety_center/v1/share'
USER_ID = 'id1'
HEADER = {
    'X-Yandex-UID': '9876',
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': 'a' * 24,  # it must be a 24-character hex string
    'Accept-Language': 'ru-RU',
}

DUMMY = 'dummy'


def _mock_share_action_for_share(notification_type):
    recipients = models.Phones(
        [
            models.Phone(
                name='Name', personal_phone_id='id', number='+79999999999',
            ),
        ],
    )
    strategy = getter.get_strategy(
        notification_type=notification_type,
        user_id=DUMMY,
        yandex_uid=DUMMY,
        phone_id=DUMMY,
        phones=recipients,
        locale='ru',
        request=api.ShareRequest(
            'idempotency_key', notification_type, ['recipients'],
        ),
        context=web_context.Context(),
        log_extra={},
    )
    # avoid database hit
    strategy._user_phone = models.Phone(
        number='+71234567890', personal_phone_id='+71234567890_id',
    )
    return strategy


def _verify_sharing_row(row, request_body, user_id, yandex_uid, user_locale):
    keys_and_values = list(request_body.items())
    keys_and_values.extend(
        [
            ('user_id', user_id),
            ('yandex_uid', yandex_uid),
            ('user_locale', user_locale),
        ],
    )
    for key, value in keys_and_values:
        if key == 'coordinates':
            value = str(tuple(value)).replace(' ', '')
        if key == 'recipients':
            value = [recipient + '_id' for recipient in value]
        assert row[key] == value


async def verify_sharing_inserted(
        request_body, user_id, yandex_uid, user_locale, pgsql,
):
    query = (
        'SELECT * FROM safety_center.sharing'
        ' WHERE idempotency_key=\'{}\'::TEXT'
    ).format(request_body['idempotency_key'])
    cursor = pgsql['safety_center'].cursor()
    cursor.execute(query)
    assert cursor.rowcount == 1
    table_keys = (
        'sharing_id',
        'idempotency_key',
        'user_id',
        'yandex_uid',
        'user_locale',
        'notification_type',
        'recipients',
        'order_id',
        'coordinates',
        'accuracy',
        'created_at',
    )
    result = [dict(zip(table_keys, row)) for row in cursor]
    _verify_sharing_row(
        result[0], request_body, user_id, yandex_uid, user_locale,
    )


async def test_send_sms(mockserver):
    notification_type = 'emergency'
    emerg = _mock_share_action_for_share(notification_type)
    stq_called = False

    @mockserver.json_handler('/stq-agent/queues/api/add/send_sms')
    def _(request):
        nonlocal stq_called
        stq_called = True
        assert request.method == 'POST'
        request.json['kwargs'].pop('log_extra')
        assert request.json == {
            'task_id': f'{emerg.request.idempotency_key}_id',
            'args': [
                '+79999999999',
                f'safety_center.{notification_type}',
                None,
                'ru',
            ],
            'kwargs': {'sender_phone': emerg._user_phone.number},
            'eta': '1970-01-01T00:00:00.000000Z',
        }

    await emerg._send_sms_to_contacts()
    assert stq_called


async def test_notify_support(mockserver):
    notification_type = 'emergency'
    emerg = _mock_share_action_for_share(notification_type)
    stq_called = False

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/safety_center_create_support_ticket',
    )
    def _(request):
        nonlocal stq_called
        stq_called = True
        assert request.method == 'POST'
        request.json['kwargs'].pop('log_extra')
        assert request.json == {
            'task_id': 'idempotency_key_safety_center',
            'args': [],
            'kwargs': {
                'phone': emerg._user_phone.number,
                'locale': emerg.locale,
                'idempotency_key': emerg.request.idempotency_key,
                'source': emerg.support_source_key,
            },
            'eta': '1970-01-01T00:00:00.000000Z',
        }

    await emerg._notify_support()
    assert stq_called


@pytest.mark.config(SAFETY_CENTER_SHARE_ENABLED=True)
@pytest.mark.parametrize(
    'request_type', ['emergency', 'contact_request', 'share_location'],
)
@pytest.mark.parametrize(
    'request_body,expected_status,expected_response',
    [
        (
            {
                'idempotency_key': 'uuid',
                'recipients': ['+79999999999'],
                'coordinates': [37.617633, 55.755786],
                'accuracy': 10,
            },
            200,
            {},
        ),
    ],
)
async def test_share(
        web_app_client,
        request_body,
        expected_status,
        expected_response,
        mockserver,
        mock_personal_response,
        mock_personal_single_response,
        mock_archive_response,
        mock_user_api_response,
        request_type,
):
    mock_personal_response(request_body['recipients'])
    mock_personal_single_response(DUMMY)
    mock_archive_response({'user_id': HEADER['X-YaTaxi-UserId']})
    mock_user_api_response('user_api_phone_id')
    request_body['notification_type'] = request_type

    @mockserver.json_handler('/stq-agent/queues/api/add/', prefix=True)
    async def _(request):
        pass

    response = await web_app_client.put(
        SHARE_URL, data=json.dumps(request_body), headers=HEADER,
    )
    assert (response.status, await response.json()) == (
        expected_status,
        expected_response,
    )


@pytest.mark.config(SAFETY_CENTER_SHARE_ENABLED=True)
@pytest.mark.client_experiments3(
    consumer=const.EXP3_SHARE_CONSUMER,
    experiment_name=const.EXP3_CREATE_SUPPORT_TICKET,
    args=[{'name': 'user_id', 'type': 'string', 'value': USER_ID}],
    value={
        'create_support_ticket': [
            'crash_detection',
            'emergency',
            'instruction',
        ],
    },
)
@pytest.mark.parametrize(
    ['notification_type', 'should_send_sms', 'should_notify_support'],
    [
        ('contact_request', True, False),
        ('crash_detection', True, True),
        ('emergency', True, True),
        ('instruction', True, True),
        ('share_location', True, False),
    ],
)
@pytest.mark.pgsql('safety_center')
async def test_sharing_strategies(
        web_app_client,
        mock_archive_response,
        mock_personal_response,
        pgsql,
        notification_type,
        should_send_sms,
        should_notify_support,
):
    mock_archive_response({'user_id': USER_ID})
    sa_refpath = 'taxi_safety_center.logic.share.action.base.ShareAction'
    ss_patch = asynctest.patch(sa_refpath + '._send_sms_to_contacts')
    ns_patch = asynctest.patch(sa_refpath + '._notify_support')
    with ss_patch as send_sms_mock, ns_patch as notify_support_mock:
        recipients = ['+79999999999']
        mock_personal_response(recipients)
        request_body = {
            'idempotency_key': 'uuid',
            'recipients': recipients,
            'coordinates': [37.617633, 55.755786],
            'notification_type': notification_type,
            'accuracy': 10,
        }
        response = await web_app_client.put(
            SHARE_URL, json=request_body, headers=HEADER,
        )
        assert response.status == 200
        assert (await response.json()) == {}
        send_sms_mock.assert_awaited_once()
        await verify_sharing_inserted(
            request_body,
            user_id=HEADER['X-YaTaxi-UserId'],
            yandex_uid=HEADER['X-Yandex-UID'],
            user_locale=HEADER['Accept-Language'][:2],
            pgsql=pgsql,
        )
        if should_notify_support:
            notify_support_mock.assert_awaited_once()
        else:
            notify_support_mock.assert_not_awaited()
        # test idempotency
        updated_body = request_body.copy()
        updated_body['coordinates'] = [1.02, 2.03]
        response = await web_app_client.put(
            SHARE_URL, json=updated_body, headers=HEADER,
        )
        assert response.status == 200
        assert (await response.json()) == {}
        send_sms_mock.assert_awaited_once()
        if should_notify_support:
            notify_support_mock.assert_awaited_once()
        # verify that previous result is stored in db
        await verify_sharing_inserted(
            request_body,
            user_id=HEADER['X-YaTaxi-UserId'],
            yandex_uid=HEADER['X-Yandex-UID'],
            user_locale=HEADER['Accept-Language'][:2],
            pgsql=pgsql,
        )


@pytest.mark.config(SAFETY_CENTER_SHARE_ENABLED=False)
@pytest.mark.parametrize(
    'request_body,expected_status,' 'expected_response_template',
    [
        (
            {
                'idempotency_key': 'uuid',
                'recipients': ['+79999999999'],
                'accuracy': 10,
                'coordinates': [37.617633, 55.755786],
            },
            200,
            {
                'message': {
                    'recipients': ['+79999999999'],
                    # updating template with status to check that text is right
                    'text': 'Позвоните мне, пожалуйста {}',
                },
                'need_send_as_message': True,
            },
        ),
        (
            {
                'idempotency_key': 'uuid',
                'recipients': ['+79999999999'],
                'accuracy': 10,
                'order_id': '8bc1b8648a4d4b2a85d869156c5efb5f',
                'coordinates': [37.617633, 55.755786],
            },
            200,
            {
                'message': {
                    'recipients': ['+79999999999'],
                    # updating template with status to check that text is right
                    'text': (
                        'Я сейчас здесь: https://taxi.yandex.ru/route'
                        '/-0AZikHShmO6Z_1YdToKq1eZKrZImeLTmyDdT6oJbkk= {}'
                    ),
                },
                'need_send_as_message': True,
            },
        ),
        (
            {
                'idempotency_key': 'uuid',
                'recipients': ['+79999999999'],
                'accuracy': 10,
                'order_id': 'unauthorized_order',
                'coordinates': [37.617633, 55.755786],
            },
            403,  # unauthorized_user
            {'code': 'unauthorized_order_access'},
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'safety_center.share.emergency.fallback_response_with_order': {
            'ru': 'Я сейчас здесь: {sharing_url} emergency',
        },
        'safety_center.share.share_location.fallback_response_with_order': {
            'ru': 'Я сейчас здесь: {sharing_url} share_location',
        },
        'safety_center.share.contact_request.fallback_response_with_order': {
            'ru': 'Я сейчас здесь: {sharing_url} contact_request',
        },
        'safety_center.share.emergency.fallback_response': {
            'ru': 'Позвоните мне, пожалуйста emergency',
        },
        'safety_center.share.share_location.fallback_response': {
            'ru': 'Позвоните мне, пожалуйста share_location',
        },
        'safety_center.share.contact_request.fallback_response': {
            'ru': 'Позвоните мне, пожалуйста contact_request',
        },
    },
)
@pytest.mark.parametrize(
    'request_type', ['emergency', 'contact_request', 'share_location'],
)
@order_core_helper.ORDER_CORE_ENABLED
async def test_share_fallback(
        web_app_client,
        request_body,
        expected_status,
        expected_response_template,
        request_type,
        mockserver,
        mock_personal_response,
        mock_archive_response,
        order_core_mock,
):
    header = {
        'X-Yandex-UID': '9876',
        'X-YaTaxi-UserId': '123',
        'X-YaTaxi-PhoneId': '456',
        'Accept-Language': 'ru',
    }
    if request_body.get('order_id', '') != 'unauthorized_order':
        mock_archive_response({'user_id': header['X-YaTaxi-UserId']})
    else:
        mock_archive_response({'user_id': 'unauthorized_user'})
    mock_personal_response(request_body['recipients'])

    request_body['notification_type'] = request_type

    expected_response = copy.deepcopy(expected_response_template)

    if 'message' in expected_response:
        text = expected_response['message']['text']
        expected_response['message']['text'] = text.format(request_type)

    response = await web_app_client.put(
        SHARE_URL, data=json.dumps(request_body), headers=header,
    )
    assert (response.status, await response.json()) == (
        expected_status,
        expected_response,
    )


@pytest.mark.config(
    SAFETY_CENTER_SHARING_ROUTE_URL_TEMPLATE_BY_BRAND={
        '__default__': 'https://taxi.yandex.ru/route/{sharing_key}',
        'yango': 'https://yango.yandex.com/route/{sharing_key}',
    },
)
@pytest.mark.parametrize(
    ['order_id', 'expected_message_text'],
    [
        pytest.param(
            'yango_order',
            'Я сейчас здесь: ' 'https://yango.yandex.com/route/yango_key',
            id='order_from_yango',
        ),
        pytest.param(
            'other_order',
            'Я сейчас здесь: ' 'https://taxi.yandex.ru/route/yandex_key',
            id='order_from_another_brand',
        ),
        pytest.param(
            'unknown_order',
            'Я сейчас здесь: ' 'https://taxi.yandex.ru/route/unknown_key',
            id='brand_unknown',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'safety_center.share.share_location.fallback_response_with_order': {
            'ru': 'Я сейчас здесь: {sharing_url}',
        },
    },
)
@order_core_helper.ORDER_CORE_ENABLED
async def test_sharing_url_template(
        web_app_client,
        order_id,
        expected_message_text,
        mockserver,
        mock_personal_response,
        mock_archive_response,
        order_core_mock,
):
    request_body = {
        'idempotency_key': 'uuid',
        'order_id': order_id,
        'recipients': ['+79999999999'],
    }
    expected_response = {
        'message': {
            'recipients': ['+79999999999'],
            'text': expected_message_text,
        },
        'need_send_as_message': True,
    }
    header = {
        'X-Yandex-UID': '9876',
        'X-YaTaxi-UserId': '123',
        'X-YaTaxi-PhoneId': '456',
        'Accept-Language': 'ru',
    }
    mock_archive_response({'user_id': header['X-YaTaxi-UserId']})
    mock_personal_response(request_body['recipients'])
    request_body['notification_type'] = 'share_location'

    response = await web_app_client.put(
        SHARE_URL, data=json.dumps(request_body), headers=header,
    )
    assert (await response.json(),) == (expected_response,)
