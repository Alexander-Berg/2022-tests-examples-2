import pytest


@pytest.mark.parametrize(
    'path, params',
    [
        ('user/sms/send', {'user_id': 'user_1'}),
        ('driver/sms/send', {'park_id': 'PARK_ID', 'driver_id': 'DRIVER_ID'}),
        ('general/sms/send', {'phone_id': 'phone_id1'}),
    ],
)
@pytest.mark.config(COMMUNICATIONS_SMS_CHECK_ALLOWED_TRANSLATIONS=False)
@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(cost)s руб.',
            'en': '%(cost)s dollars.',
            'kk': '%(cost)s kzt.',
        },
        'another_key': {
            'ru': '%(cost)s руб.',
            'en': '%(cost)s dollars.',
            'kk': '%(cost)s kzt.',
        },
    },
)
async def test_check_disabled(
        taxi_ucommunications, mockserver, path, params, load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.handler('/yasms/sendsms', raw_request=True)
    async def _send_sms(request):
        post = await request.post()
        assert post['text'] == '100 dollars.'

        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    body = {
        'text': {
            'key': 'another_key',
            'keyset': 'notify',
            'params': {'cost': 100},
        },
        'locale': 'en',
        'intent': 'greeting',
    }
    body.update(params)

    response = await taxi_ucommunications.post(path, json=body)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'path, params',
    [
        ('user/sms/send', {'user_id': 'user_1'}),
        ('driver/sms/send', {'park_id': 'PARK_ID', 'driver_id': 'DRIVER_ID'}),
        ('general/sms/send', {'phone_id': 'phone_id1'}),
    ],
)
@pytest.mark.config(COMMUNICATIONS_SMS_CHECK_ALLOWED_TRANSLATIONS=True)
@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(cost)s руб.',
            'en': '%(cost)s dollars.',
            'kk': '%(cost)s kzt.',
        },
        'another_key': {
            'ru': '%(cost)s руб.',
            'en': '%(cost)s dollars.',
            'kk': '%(cost)s kzt.',
        },
    },
)
async def test_not_allowed_translations(
        taxi_ucommunications, path, params, load_json, mockserver,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    body = {
        'text': {
            'key': 'another_key',
            'keyset': 'notify',
            'params': {'cost': 100},
        },
        'locale': 'en',
        'intent': 'greeting',
    }
    body.update(params)

    response = await taxi_ucommunications.post(path, json=body)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'path, params',
    [
        ('user/sms/send', {'user_id': 'user_1'}),
        ('driver/sms/send', {'park_id': 'PARK_ID', 'driver_id': 'DRIVER_ID'}),
        ('general/sms/send', {'phone_id': 'phone_id1'}),
    ],
)
@pytest.mark.config(COMMUNICATIONS_SMS_CHECK_ALLOWED_TRANSLATIONS=True)
@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(cost)s руб.',
            'en': '%(cost)s dollars.',
            'kk': '%(cost)s kzt.',
        },
    },
)
async def test_allowed_translations(
        taxi_ucommunications, mockserver, path, params, load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.handler('/yasms/sendsms', raw_request=True)
    async def _send_sms(request):
        post = await request.post()
        assert post['text'] == '100 dollars.'

        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    body = {
        'locale': 'en',
        'text': {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}},
        'intent': 'greeting',
    }
    body.update(params)

    response = await taxi_ucommunications.post(path, json=body)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'path, params',
    [
        ('user/sms/send', {'user_id': 'user_1'}),
        ('driver/sms/send', {'park_id': 'PARK_ID', 'driver_id': 'DRIVER_ID'}),
        ('general/sms/send', {'phone_id': 'phone_id1'}),
    ],
)
@pytest.mark.config(COMMUNICATIONS_SMS_CHECK_ALLOWED_TRANSLATIONS=True)
@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(cost)s руб.',
            'en': '%(cost)s dollars.',
            'kk': '%(cost)s kzt.',
        },
    },
)
async def test_not_allowed_translations_for_text_intent_cache(
        taxi_ucommunications, path, params, mockserver, load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    body = {'locale': 'en', 'text': 'not localizable', 'intent': 'greeting'}
    body.update(params)

    response = await taxi_ucommunications.post(path, json=body)
    assert response.status_code == 400
