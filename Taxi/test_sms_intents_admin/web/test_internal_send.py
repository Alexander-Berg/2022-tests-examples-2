from aiohttp import web
import pytest


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+79111111111'])
@pytest.mark.pgsql('sms_intents_admin', files=['test_send.sql'])
async def test_raw_text(web_app_client, mock_ucommunications):
    @mock_ucommunications('/user/sms/send')
    async def handler_send(request):
        assert request.json['text'] == 'raw_text'
        return web.json_response({'code': 'code', 'message': 'message'})

    response = await web_app_client.post(
        '/v1/internal/send',
        json={
            'intent': 'test_raw_text',
            'recipients_type': 'user',
            'phone': '+79111111111',
            'text': 'raw_text',
        },
    )
    assert response.status == 200
    assert handler_send.times_called == 1


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+79111111111'])
@pytest.mark.pgsql('sms_intents_admin', files=['test_send.sql'])
async def test_tanker_key_with_params(web_app_client, mock_ucommunications):
    @mock_ucommunications('/user/sms/send')
    async def handler_send(request):
        assert request.json['text'] == {
            'key': 'my_key',
            'keyset': 'tanker',
            'params': {'foo': 'bar'},
        }
        assert request.json['locale'] == 'ru'
        return web.json_response({'code': 'code', 'message': 'message'})

    response = await web_app_client.post(
        '/v1/internal/send',
        json={
            'intent': 'test_user',
            'recipients_type': 'user',
            'phone': '+79111111111',
            'text': {
                'key': 'my_key',
                'keyset': 'tanker',
                'params': {'foo': 'bar'},
                'locale': 'ru',
            },
        },
    )
    assert response.status == 200
    assert handler_send.times_called == 1


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+79111111111'])
@pytest.mark.pgsql('sms_intents_admin', files=['test_send.sql'])
async def test_driver_recipients_type(web_app_client, mock_ucommunications):
    @mock_ucommunications('/driver/sms/send')
    async def handler_send(request):
        return web.json_response({'code': 'code', 'message': 'message'})

    response = await web_app_client.post(
        '/v1/internal/send',
        json={
            'intent': 'test_user',
            'recipients_type': 'driver',
            'phone': '+79111111111',
            'text': {'key': 'my_key', 'keyset': 'tanker'},
        },
    )
    assert response.status == 200
    assert handler_send.times_called == 1


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+79111111111'])
@pytest.mark.pgsql('sms_intents_admin', files=['test_send.sql'])
async def test_general_recipients_type(web_app_client, mock_ucommunications):
    @mock_ucommunications('/general/sms/send')
    async def handler_send(request):
        return web.json_response({'code': 'code', 'message': 'message'})

    response = await web_app_client.post(
        '/v1/internal/send',
        json={
            'intent': 'test_user',
            'recipients_type': 'general',
            'phone': '+79111111111',
            'text': {'key': 'my_key', 'keyset': 'tanker'},
        },
    )
    assert response.status == 200
    assert handler_send.times_called == 1


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+79222222222'])
@pytest.mark.pgsql('sms_intents_admin', files=['test_send.sql'])
async def test_unknown_phone_number(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/send',
        json={
            'intent': 'test_user',
            'recipients_type': 'user',
            'phone': '+79111111111',
            'text': {'key': 'my_key', 'keyset': 'tanker'},
        },
    )
    assert response.status == 400


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+79111111111'])
@pytest.mark.pgsql('sms_intents_admin', files=['test_send.sql'])
async def test_unknown_intent(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/send',
        json={
            'intent': 'unknown_intent',
            'recipients_type': 'user',
            'phone': '+79111111111',
            'text': {'key': 'my_key', 'keyset': 'tanker'},
        },
    )
    assert response.status == 404


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+79111111111'])
@pytest.mark.pgsql('sms_intents_admin', files=['test_send.sql'])
async def test_raw_text_to_tanker_only_intent(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/send',
        json={
            'intent': 'test_user',
            'recipients_type': 'user',
            'phone': '+79111111111',
            'text': 'raw_text',
        },
    )
    assert response.status == 400


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+79111111111'])
@pytest.mark.pgsql('sms_intents_admin', files=['test_send.sql'])
async def test_incorrect_key_to_tanker_only_intent(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/send',
        json={
            'intent': 'test_user',
            'recipients_type': 'user',
            'phone': '+79111111111',
            'text': {'key': 'unknown_key', 'keyset': 'tanker'},
        },
    )
    assert response.status == 400
