import pytest


@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
async def test_bad_request(taxi_ucommunications):
    text = {'key': 'key1', 'params': {'cost': 100}}

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': text,
            'locale': 'ru',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
        'money': {'ru': 'P%(count)s', 'en': '$%(count)'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
@pytest.mark.parametrize(
    'text,payload',
    [
        ('Строка!', 'Строка!'),
        (
            {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}},
            '100 руб.',
        ),
        (
            {
                'key': 'key1',
                'keyset': 'notify',
                'params': {
                    'cost': {
                        'key': 'money',
                        'keyset': 'notify',
                        'params': {'count': 100},
                    },
                },
            },
            'P100 руб.',
        ),
    ],
)
async def test_send_ok(taxi_ucommunications, mockserver, text, payload):
    @mockserver.json_handler('/yasms/sendsms', raw_request=True)
    async def _mock_yasms(request):
        post = await request.post()

        assert post['phone'] == '+70001112233'
        assert post['text'] == payload
        assert post['utf8'] == '1'

        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'adadadadad', 'value': '+70001112233'}

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': text,
            'locale': 'ru',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': payload,
        'status': 'sent',
    }


@pytest.mark.translations(
    notify={
        'key1': {
            'ru': ['%(cost)s рубль', '%(cost)s рубля', '%(cost)s рублей'],
            'en': '%(cost)s dollars.',
        },
        'money': {'ru': 'P%(count)s', 'en': '$%(count)'},
    },
)
@pytest.mark.parametrize(
    'text,payload',
    [
        (
            {
                'key': 'key1',
                'keyset': 'notify',
                'params': {'cost': {'value': '100', 'count': 100}},
            },
            '100 рублей',
        ),
        (
            {
                'key': 'key1',
                'keyset': 'notify',
                'params': {'cost': {'value': 101, 'count': 101}},
            },
            '101 рубль',
        ),
        (
            {
                'key': 'key1',
                'keyset': 'notify',
                'params': {'cost': {'value': '1', 'count': 1}},
            },
            '1 рубль',
        ),
        (
            {
                'key': 'key1',
                'keyset': 'notify',
                'params': {'cost': {'value': '2', 'count': 2}},
            },
            '2 рубля',
        ),
        (
            {
                'key': 'key1',
                'keyset': 'notify',
                'params': {
                    'cost': {
                        'value': {
                            'key': 'money',
                            'keyset': 'notify',
                            'params': {'count': {'value': '2'}},
                        },
                        'count': 2,
                    },
                },
            },
            'P2 рубля',
        ),
        (
            {
                'key': 'key1',
                'keyset': 'notify',
                'params': {
                    'cost': {
                        'value': {
                            'key': 'money',
                            'keyset': 'notify',
                            'params': {'count': {'value': '0'}},
                        },
                        'count': 0,
                    },
                },
            },
            'P0 рублей',
        ),
    ],
)
async def test_send_ok_plural(taxi_ucommunications, mockserver, text, payload):
    @mockserver.json_handler('/yasms/sendsms', raw_request=True)
    async def _mock_yasms(request):
        post = await request.post()

        assert post['phone'] == '+70001112233'
        assert post['text'] == payload
        assert post['utf8'] == '1'

        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'adadadadad', 'value': '+70001112233'}

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': text,
            'locale': 'ru',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': payload,
        'status': 'sent',
    }


@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(cost)s руб.',
            'en': '%(cost)s dollars.',
            'kk': '%(cost)s kzt.',
        },
        'key2': {'en': 'fixed'},
    },
)
@pytest.mark.parametrize(
    'phone,text,payload',
    [
        (
            '+40001112233',
            {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}},
            '100 dollars.',
        ),
        (
            '+375001112233',
            {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}},
            '100 руб.',
        ),
        (
            '+79001112233',
            {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}},
            '100 руб.',
        ),
        (
            '+77001112233',
            {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}},
            '100 kzt.',
        ),
    ],
)
async def test_request_no_locale(
        taxi_ucommunications, mockserver, phone, text, payload,
):
    @mockserver.json_handler('/yasms/sendsms', raw_request=True)
    async def _mock_yasms(request):
        post = await request.post()

        assert post['phone'] == phone
        assert post['text'] == payload
        assert post['utf8'] == '1'

        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'adadadadad', 'value': phone}

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={'phone': phone, 'text': text, 'intent': 'greeting'},
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': payload,
        'status': 'sent',
    }


@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
async def test_argument_not_found(taxi_ucommunications, mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'adadadadad', 'value': '+792611505656'}

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': {'key': 'key1', 'keyset': 'notify', 'params': {}},
            'locale': 'ru',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 400
    response_data = response.json()
    response_data.pop('message_id')
    assert response_data == {
        'code': '400',
        'message': (
            'Substitute localization error: Translation [notify][key1] '
            'failed: No substitution for key cost when formatting '
            'template {cost} руб.'
        ),
        'status': 'error',
    }
