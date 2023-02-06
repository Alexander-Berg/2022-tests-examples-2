import pytest


async def _send_user_sms_by_phone(taxi_ucommunications):
    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    return response


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+70001112233'])
async def test_ok(taxi_ucommunications, mock_personal, mock_yasms):
    response = await _send_user_sms_by_phone(taxi_ucommunications)
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=[])
async def test_not_in_whitelist(
        taxi_ucommunications, mock_personal, mockserver,
):
    @pytest.fixture(name='mock_yasms')
    def _mock_yasms(mockserver):
        @mockserver.aiohttp_json_handler('/yasms/sendsms')
        async def _mock_yasms(request):
            assert False

    response = await _send_user_sms_by_phone(taxi_ucommunications)
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'Declined by COMMUNICATIONS_SMS_PHONES_WHITELIST',
        'status': 'error',
        'content': 'Добрый день!',
    }


async def test_in_excluded(
        taxi_ucommunications, mock_personal, mock_yasms, mockserver, load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents_whitelist_disabled.json')

    response = await _send_user_sms_by_phone(taxi_ucommunications)
    assert response.status_code == 200


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=[])
async def test_send_by_phone_id_400(
        taxi_ucommunications, mock_personal, mockserver, load_json,
):
    @pytest.fixture(name='mock_yasms')
    def _mock_yasms(mockserver):
        @mockserver.aiohttp_json_handler('/yasms/sendsms')
        async def _mock_yasms(request):
            assert False

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=['+70001112233'])
async def test_send_by_phone_id_ok(
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
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=[])
async def test_general(taxi_ucommunications, mockserver, mock_personal):
    @pytest.fixture(name='mock_yasms')
    def _mock_yasms(mockserver):
        @mockserver.aiohttp_json_handler('/yasms/sendsms')
        async def _mock_yasms(request):
            assert False

    response = await taxi_ucommunications.post(
        'general/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200


@pytest.mark.config(COMMUNICATIONS_SMS_PHONES_WHITELIST=[])
async def test_driver(
        taxi_ucommunications, mockserver, mock_personal, load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone.json')

    @pytest.fixture(name='mock_yasms')
    def _mock_yasms(mockserver):
        @mockserver.aiohttp_json_handler('/yasms/sendsms')
        async def _mock_yasms(request):
            assert False

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'phone_id': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
