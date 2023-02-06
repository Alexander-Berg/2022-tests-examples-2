import pytest


async def test_bad_request(taxi_ucommunications, mock_personal):
    response = await taxi_ucommunications.post(
        'general/sms/send', json={'phone': '+70001112233'},
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'general/sms/send', json={'text': 'Добрый день!'},
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'general/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'notexisting',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'general/sms/send',
        json={
            'phone_id': 'bdkb1dk1',
            'phone': '+70001112233',
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
        'general/sms/send',
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
        'general/sms/send',
        json={
            'phone_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'greeting',
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


async def test_send_by_phone(taxi_ucommunications, mock_yasms, mock_personal):
    response = await taxi_ucommunications.post(
        'general/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
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
        'general/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
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


async def test_mask_text(taxi_ucommunications, mock_yasms, mock_personal):
    response = await taxi_ucommunications.post(
        'general/sms/send',
        json={
            'phone_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'mask_text',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Д...',
        'status': 'sent',
    }
