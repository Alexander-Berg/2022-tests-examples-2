from aiohttp import web
import pytest

from generated import clients
from generated import models

PUSH_BODY = {
    'repack': {
        'wns': {'toast': {'text1': 'Винни-Пух и все-все-все'}},
        'apns': {
            'aps': {
                'content-available': 1,
                'alert': 'Винни-Пух и все-все-все',
                'repack_payload': ['id', 'msg', 'deeplink', 'extra'],
            },
        },
        'fcm': {
            'notification': {'title': 'Винни-Пух и все-все-все'},
            'repack_payload': ['id', 'msg', 'deeplink', 'extra'],
        },
        'hms': {
            'notification_title': 'Винни-Пух и все-все-все',
            'repack_payload': ['id', 'msg', 'deeplink', 'extra'],
        },
        'mpns': {'toast': {'text1': 'Винни-Пух и все-все-все'}},
    },
    'payload': {
        'id': 'yt_table:3874747',
        'msg': 'Если б мишки были пчелами',
        'deeplink': 'yandextaxi://addpromocode?code=MISHKI',
        'extra': {'save_promocode': True, 'promocode': 'MISHKI'},
    },
}


@pytest.fixture(name='client')
def communications_fixture(web_context):
    return web_context.clients.ucommunications


async def test_user_sms_send_localizable(client, mockserver):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    async def handler(request):
        assert request.json == {
            'phone_id': 'ff00ff00ff00ff00',
            'text': {
                'keyset': 'notify',
                'key': 'apns.on_assigned',
                'params': {
                    'estimate': '4',
                    'car_info': 'car-info',
                    'driver_phone': '+799999',
                },
            },
            'locale': 'en',
            'intent': 'greeting',
        }
        return web.json_response({'code': 'code', 'message': 'message'})

    response = await client.user_sms_send_post(
        body=clients.ucommunications.UserSmsSendPostBody(
            phone_id='ff00ff00ff00ff00',
            text=models.ucommunications.Localizable(
                keyset='notify',
                key='apns.on_assigned',
                params={
                    'estimate': '4',
                    'car_info': 'car-info',
                    'driver_phone': '+799999',
                },
            ),
            locale='en',
            intent='greeting',
        ),
    )

    assert response.status == 200
    assert response.body.code == 'code'
    assert response.body.message == 'message'
    assert handler.times_called == 1


async def test_user_sms_send_text(client, mockserver):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    async def handler(request):
        assert request.json == {
            'phone_id': 'ff00ff00ff00ff00',
            'text': 'just text',
            'locale': 'en',
            'intent': 'greeting',
        }
        return web.json_response({'code': 'code', 'message': 'message'})

    response = await client.user_sms_send_post(
        body=clients.ucommunications.UserSmsSendPostBody(
            phone_id='ff00ff00ff00ff00',
            text='just text',
            locale='en',
            intent='greeting',
        ),
    )

    assert response.status == 200
    assert response.body.code == 'code'
    assert response.body.message == 'message'
    assert handler.times_called == 1


async def test_user_notification_push(client, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def handler(request):
        assert request.json == {
            'user': 'd6d13ca5b64e1bade2829fed08a28a88',
            'intent': 'none',
            'confirm': True,
            'locale': 'ru',
            'ttl': 600,
            'data': PUSH_BODY,
        }
        return web.json_response({})

    response = await client.user_notification_push_post(
        body=clients.ucommunications.UserNotificationPushPostBody(
            user='d6d13ca5b64e1bade2829fed08a28a88',
            data=PUSH_BODY,
            locale='ru',
            intent='none',
            confirm=True,
            ttl=600,
        ),
    )

    assert response.status == 200
    assert response.body.payload is None
    assert handler.times_called == 1
