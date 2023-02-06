import pytest


async def test_bad_request(
        taxi_ucommunications, mock_personal, mock_parks, mockserver, load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone.json')

    response = await taxi_ucommunications.post(
        'driver/sms/send', json={'phone': '+70001112233'},
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'driver/sms/send', json={'text': 'Добрый день!'},
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'notexisting',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'phone': '+70001112233',
            'phone_id': 'anljl12',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'driver_id': 'DRIVER_ID',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'park_id': 'DRIVER_ID',
            'phone_id': 'anljl12',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'park_id': 'PARK_ID',
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
        personal_response_code,
        expected_code,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal(request):
        return mockserver.make_response(
            status=personal_response_code,
            json={'code': 'not-found', 'message': 'error'},
        )

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'phone_id': '557f191e810c19729de860ea',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == expected_code


async def test_send_empty_driver_profiles(
        taxi_ucommunications, mock_yasms, mock_personal, mockserver, load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone_empty.json')

    response = await taxi_ucommunications.post(
        'driver/sms/send',
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


async def test_send_driver_not_found(
        taxi_ucommunications, mock_yasms, mock_personal, mockserver, load_json,
):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def _get_driver_phone_id(request):
        return {'profiles': []}

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone_empty.json')

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'park_id': 'PARK_ID',
            'driver_id': 'DRIVER_ID',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 404


async def test_send_phone_id_not_found(
        taxi_ucommunications, mock_yasms, mock_personal, mockserver, load_json,
):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def _get_driver_phone_id(request):
        return {
            'profiles': [
                {
                    'driver': {'phone_pd_ids': [], 'locale': 'en'},
                    'park': {'locale': 'kk'},
                },
            ],
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone_empty.json')

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'park_id': 'PARK_ID',
            'driver_id': 'DRIVER_ID',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 404
    response_data = response.json()
    assert response_data == {
        'code': '404',
        'message': 'phone_id not found for driver_id',
    }


async def test_send_by_phone_id(
        taxi_ucommunications, mock_yasms, mock_personal, mockserver, load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone.json')

    response = await taxi_ucommunications.post(
        'driver/sms/send',
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


@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(cost)s руб.',
            'en': '%(cost)s dollars.',
            'kk': '%(cost)s kzt.',
        },
    },
)
async def test_send_locale_by_phone_id(
        taxi_ucommunications, mock_yasms, mock_personal, mockserver, load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone.json')

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'phone_id': '557f191e810c19729de860ea',
            'text': {
                'key': 'key1',
                'keyset': 'notify',
                'params': {'cost': 100},
            },
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop('message_id')
    assert response_data == {
        'code': '200',
        'message': 'OK',
        'content': '100 dollars.',
        'status': 'sent',
    }


async def test_send_by_phone(
        taxi_ucommunications, mock_yasms, mock_personal, mockserver, load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone.json')

    response = await taxi_ucommunications.post(
        'driver/sms/send',
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


async def test_mask_text(
        taxi_ucommunications, mock_yasms, mock_personal, mock_parks,
):
    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'park_id': 'PARK_ID',
            'driver_id': 'DRIVER_ID',
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


async def test_send_by_driver_id(
        taxi_ucommunications, mock_yasms, mock_personal, mock_parks,
):
    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'park_id': 'PARK_ID',
            'driver_id': 'DRIVER_ID',
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


@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(cost)srub',
            'en': '%(cost)sdol',
            'kk': '%(cost)skzt',
        },
    },
)
@pytest.mark.parametrize(
    'driver_locale,park_locale,sms_text',
    [('en', 'kk', '100dol'), (None, 'kk', '100kzt'), (None, '', '100rub')],
)
async def test_autodetect_locale(
        taxi_ucommunications,
        mock_yasms,
        mock_parks,
        mock_personal,
        mockserver,
        load_json,
        driver_locale,
        park_locale,
        sms_text,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_driver_app_profiles_retrieve(request):
        return {
            'profiles': [
                {
                    'data': {'locale': driver_locale},
                    'park_driver_profile_id': 'PARK_ID_DRIVER_ID',
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks_v1_parks_list(request):
        response = load_json('fleet_parks_list_default_response.json')
        response['parks'][0]['locale'] = park_locale
        return response

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'park_id': 'PARK_ID',
            'driver_id': 'DRIVER_ID',
            'text': {
                'key': 'key1',
                'keyset': 'notify',
                'params': {'cost': 100},
            },
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop('message_id')
    assert response_data == {
        'code': '200',
        'message': 'OK',
        'content': sms_text,
        'status': 'sent',
    }


@pytest.mark.parametrize('personal_response_code', [500, 404])
async def test_bad_response_personal_find(
        taxi_ucommunications,
        mock_yasms,
        mock_personal,
        mockserver,
        personal_response_code,
        load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone.json')

    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return mockserver.make_response('', personal_response_code)

    response = await taxi_ucommunications.post(
        'driver/sms/send',
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


@pytest.mark.config(COMMUNICATIONS_SMS_CHECK_REMOVED_DRIVER_PROFILES=True)
async def test_driver_removed_by_request(
        taxi_ucommunications, mock_personal, mock_parks, mockserver, load_json,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone_removed_by_request.json')

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'park_id': 'PARK_ID',
            'driver_id': 'DRIVER_ID',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'driver profile removed'
    assert response.json()['status'] == 'error'
    assert response.json()['code'] == '200'


@pytest.mark.config(COMMUNICATIONS_SMS_CHECK_REMOVED_DRIVER_PROFILES=True)
async def test_driver_removed_by_request_personal_id(
        taxi_ucommunications, mock_parks, mockserver, load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json(
            'driver_profiles_by_phone_removed_by_request_personal_id.json',
        )

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'driver profile removed'
    assert response.json()['status'] == 'error'
    assert response.json()['code'] == '200'


@pytest.mark.config(COMMUNICATIONS_SMS_CHECK_REMOVED_DRIVER_PROFILES=True)
async def test_driver_removed_by_request_is_false(
        taxi_ucommunications, mock_parks, mockserver, mock_yasms, load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json(
            'driver_profiles_by_phone_removed_by_request_is_false.json',
        )

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'sent'
    assert response.json()['code'] == '200'
