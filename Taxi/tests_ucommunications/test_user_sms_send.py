import pytest


@pytest.fixture(name='mock_user_api')
def _mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/user_phones/by-natural-id')
    def _phones_retrieve(request):
        return {
            'id': '557f191e810c19729de860ea',
            'phone': '+70001112233',
            'personal_phone_id': '775f191e810c19729de860ea',
            'stat': {
                'big_first_discounts': 10,
                'complete': 200,
                'complete_card': 180,
                'complete_apple': 2,
                'complete_google': 14,
                'fake': 0,
                'total': 222,
            },
            'is_loyal': True,
            'is_yandex_staff': True,
            'is_taxi_staff': True,
            'type': 'yandex',
        }

    @mockserver.json_handler('/user-api/users/search')
    def _users_search(request):
        return {
            'items': [
                {
                    'id': 'my_user_id',
                    'application': 'android',
                    'created': '2019-08-23T13:00:00+0000',
                    'updated': '2019-08-23T13:00:00+0000',
                },
            ],
        }

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve_bulk')
    def _phones_retrieve_bulk(request):
        return {
            'items': [
                {
                    'id': '5d544e9091272f03f6cc5132',
                    'phone': '+79261154433',
                    'type': 'uber',
                    'personal_phone_id': '42bd5677d3534dd1bab8e6b5cda6122b',
                    'phone_hash': (
                        'af02ee9f1a5602cfebd0b632e437fe04d9d703079e2'
                    ),
                    'phone_salt': (
                        'Kau6XnkPII2rTFmMI8gNgs7s21CPIxtRJfLl8Mpr3PY'
                    ),
                },
                {
                    'id': '5892e9287d81ea8c3797bbf4',
                    'phone': '+79261154433',
                    'type': 'yandex',
                    'personal_phone_id': '42bd5677d3534dd1bab8e6b5cda6122b',
                    'phone_hash': (
                        '0303e53d0e164865510883b10ba27eb5fbc4f8f39d4'
                    ),
                    'phone_salt': (
                        'SxQp/43Q91l9Rv99SNWSk4KL3WqWuBVTsWXQEi5ds9M'
                    ),
                },
            ],
        }


async def test_bad_request(taxi_ucommunications, mock_personal):
    response = await taxi_ucommunications.post(
        'user/sms/send', json={'phone': '+70001112233'},
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'user/sms/send', json={'text': 'Добрый день!'},
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'notexisting',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone_id': 'bdkb1dk1',
            'user_id': 'anlnwqmp12',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'user_id': 'anlnwqmp12',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.parametrize(
    'personal_response_code,expected_code', [(500, 502), (404, 404)],
)
async def test_personal_errors(
        taxi_ucommunications,
        mockserver,
        expected_code,
        personal_response_code,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal(request):
        return mockserver.make_response(
            status=personal_response_code,
            json={'code': 'not-found', 'message': 'error'},
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone_id': '557f191e810c19729de860ea',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == expected_code


async def test_send_by_phone_id(
        taxi_ucommunications, mock_yasms, mock_personal,
):
    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop('message_id')
    assert response_data == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


async def test_send_by_phone(taxi_ucommunications, mock_yasms, mock_personal):
    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop('message_id')
    assert response_data == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


async def test_send_by_user_id(
        taxi_ucommunications, mock_yasms, mock_personal, mock_user_api,
):
    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop('message_id')
    assert response_data == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


async def test_send_bad_user_api_response(
        taxi_ucommunications, mock_yasms, mockserver,
):
    @mockserver.json_handler('/user-api/user_phones/by-natural-id')
    def _phones_retrieve(request):
        return mockserver.make_response('{"code": "404", "message":""}', 404)

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 404


@pytest.mark.parametrize('personal_response_code', [500, 404])
async def test_bad_response_personal_find(
        taxi_ucommunications,
        mock_yasms,
        mock_personal,
        mockserver,
        personal_response_code,
):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return mockserver.make_response('', personal_response_code)

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop('message_id')
    assert response_data == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


async def test_empty_phone(taxi_ucommunications, mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return {'id': '557f191e810c19729de860ea', 'value': ''}

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone_id': '557f191e810c19729de860ea',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 404
    assert response.json()['message'] == 'Empty phone number'


async def test_passport_headers(
        taxi_ucommunications, mockserver, mock_personal, mock_user_api,
):
    @mockserver.json_handler('/yasms/sendsms')
    def _sendsms(request):
        assert (
            request.headers['Ya-Consumer-Client-Ip']
            == '2a02:6b8:c18:319d:0:43cb:947d:0'
        )
        assert (
            request.headers['Ya-Client-User-Agent']
            == 'ru.yandex.taxi.develop/999.9.9.9 (iPhone)'
        )
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
        headers={
            'X-Remote-IP': '2a02:6b8:c18:319d:0:43cb:947d:0',
            'X-Real-User-Agent': 'ru.yandex.taxi.develop/999.9.9.9 (iPhone)',
        },
    )
    assert response.status_code == 200


async def test_passport_headers_config(
        taxi_ucommunications,
        mockserver,
        mock_personal,
        mock_user_api,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents_header.json')

    @mockserver.json_handler('/yasms/sendsms')
    def _sendsms(request):
        assert request.headers['Ya-Client-User-Agent'] == 'ua'
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'user_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
        headers={'User-Agent': 'ua', 'X-Real-User-Agent': 'real_ua'},
    )
    assert response.status_code == 200


async def test_mask_text(taxi_ucommunications, mock_yasms, mock_personal):
    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'mask_text',
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop('message_id')
    assert response_data == {
        'code': '200',
        'message': 'OK',
        'content': 'Д...',
        'status': 'sent',
    }


@pytest.mark.parametrize('order_id', [None, 0])
async def test_meta_order_id(
        taxi_ucommunications, mock_yasms, mock_personal, order_id,
):
    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'mask_text',
            'meta': {'order_id': order_id},
        },
    )
    assert response.status_code == 200
