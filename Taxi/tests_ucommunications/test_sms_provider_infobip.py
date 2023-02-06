import json

import pytest


def _make_infobip_response(group_name, group_id, status_name, status_id):
    return json.dumps(
        {
            'bulkId': 'BULK-ID-123-xyz',
            'trackingProcessKey': '9243E3F4BEDC719D83C2A38A483E6CB3',
            'messages': [
                {
                    'to': '+70001112233',
                    'status': {
                        'groupId': group_id,
                        'groupName': group_name,
                        'id': status_id,
                        'name': status_name,
                        'description': 'Message sent to next instance',
                    },
                    'messageId': 'MESSAGE-ID-123-xyz',
                },
            ],
        },
    )


@pytest.mark.parametrize(
    'group_name,group_id,status_name,status_id',
    [
        ('OK', 0, 'NO_ERROR', 0),
        ('PENDING', 1, 'PENDING_ACCEPTED', 26),
        ('DELIVERED', 3, 'DELIVERED_TO_OPERATOR', 2),
    ],
)
@pytest.mark.parametrize(
    'intent_cache,intent_config',
    [
        (True, {}),
        (
            False,
            {
                'test': {
                    'provider': 'infobip',
                    'provider_settings': {
                        'sender': 'Yandex.Taxi',
                        'ttl': '33',
                        'account': 'taxi',
                    },
                },
            },
        ),
    ],
)
async def test_ok(
        taxi_ucommunications,
        mockserver,
        mock_personal,
        group_name,
        group_id,
        status_name,
        status_id,
        taxi_config,
        load_json,
        intent_cache,
        intent_config,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    taxi_config.set_values(
        dict(
            COMMUNICATIONS_SMS_GET_INTENTS_FROM_SMS_INTENTS_ADMIN=intent_cache,
            COMMUNICATIONS_SMS_INTENTS_MAP=intent_config,
        ),
    )
    await taxi_ucommunications.invalidate_caches()

    @mockserver.json_handler('/taxi_infobip/sms/2/text/advanced')
    def _mock_infobip(request):
        assert request.headers['Authorization'] == 'App taxi_apikey'
        assert 'application/json' in request.headers['Content-Type']
        assert 'application/json' in request.headers['Accept']

        assert request.json == {
            'messages': [
                {
                    'from': 'Yandex.Taxi',
                    'text': 'Добрый день!',
                    'destinations': [{'to': '+70001112233'}],
                    'validityPeriod': 33,
                },
            ],
        }
        return mockserver.make_response(
            _make_infobip_response(
                group_name, group_id, status_name, status_id,
            ),
            200,
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'test',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


@pytest.mark.parametrize('account', ['taxi', 'eda'])
@pytest.mark.parametrize(
    'intent_cache,intent_config',
    [
        (True, {}),
        (
            False,
            {
                'taxi_infobip': {
                    'provider': 'infobip',
                    'provider_settings': {
                        'sender': 'Yandex.Taxi',
                        'ttl': '33',
                        'account': 'taxi',
                    },
                },
                'eda_infobip': {
                    'provider': 'infobip',
                    'provider_settings': {
                        'sender': 'Yandex.Eda',
                        'ttl': '66',
                        'account': 'eda',
                    },
                },
            },
        ),
    ],
)
async def test_multiaccount(
        taxi_ucommunications,
        mockserver,
        account,
        mock_personal,
        load_json,
        taxi_config,
        intent_cache,
        intent_config,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    taxi_config.set_values(
        dict(
            COMMUNICATIONS_SMS_GET_INTENTS_FROM_SMS_INTENTS_ADMIN=intent_cache,
            COMMUNICATIONS_SMS_INTENTS_MAP=intent_config,
        ),
    )
    await taxi_ucommunications.invalidate_caches()

    # Note that mockserver URL is parametrized too
    @mockserver.json_handler(f'/{account}_infobip/sms/2/text/advanced')
    def _mock_infobip(request):
        assert request.headers['Authorization'] == f'App {account}_apikey'
        return mockserver.make_response(
            _make_infobip_response('OK', 0, 'NO_ERROR', 0), 200,
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': f'{account}_infobip',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


@pytest.mark.config(
    COMMUNICATIONS_SMS_PROVIDER_SETTINGS={
        'yasms': {'sender_to_route': {}},
        'infobip': {
            'sender_to_alpha_name': {'taxi': 'Yandex.Taxi', 'yango': 'Yango'},
        },
    },
)
@pytest.mark.parametrize(
    'sender,alphaname', [('taxi', 'Yandex.Taxi'), ('yango', 'Yango')],
)
@pytest.mark.parametrize(
    'intent_cache,intent_config',
    [
        (True, {}),
        (
            False,
            {
                'infobip': {
                    'provider': 'infobip',
                    'provider_settings': {
                        'sender': 'Yandex.Taxi',
                        'ttl': '33',
                        'account': 'taxi',
                    },
                },
            },
        ),
    ],
)
async def test_send_with_sender(
        taxi_ucommunications,
        mock_personal,
        mockserver,
        sender,
        alphaname,
        load_json,
        taxi_config,
        intent_cache,
        intent_config,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    taxi_config.set_values(
        dict(
            COMMUNICATIONS_SMS_GET_INTENTS_FROM_SMS_INTENTS_ADMIN=intent_cache,
            COMMUNICATIONS_SMS_INTENTS_MAP=intent_config,
        ),
    )
    await taxi_ucommunications.invalidate_caches()

    @mockserver.json_handler('/taxi_infobip/sms/2/text/advanced')
    def _mock_infobip(request):
        assert request.json['messages'][0]['from'] == alphaname
        return mockserver.make_response(
            _make_infobip_response('OK', 0, 'NO_ERROR', 0), 200,
        )

    response = await taxi_ucommunications.post(
        'general/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'sender': sender,
            'intent': 'infobip',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }
