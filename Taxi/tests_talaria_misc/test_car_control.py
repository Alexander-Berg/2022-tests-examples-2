import jwt
import pytest


@pytest.mark.parametrize(
    [
        'personal_response_file',
        'wind_info_ride_id_response_file',
        'wind_user_response_file',
        'wind_helmet_unlock_response_file',
        'wind_beep_and_flash_response_file',
        'expected_response_file',
        'unlock_gprs_mock_call_times',
        'beep_and_flash_mock_call_times',
        'action',
        'response_status_code',
    ],
    [
        (
            'personal_v1_phone_find_primary.json',
            'wind_riding_id_response.json',
            'wind_get_user_no_ride_response.json',
            'success_helmet_unlock_gprs_response.json',
            'wind_beep_and_flash_success_response.json',
            'succes_helmet_response.json',
            1,
            0,
            'open-helmet',
            200,
        ),
        (
            'personal_v1_phone_find_primary.json',
            'wind_riding_id_response.json',
            'wind_get_user_no_ride_response.json',
            'success_helmet_unlock_gprs_response.json',
            'wind_beep_and_flash_success_response.json',
            'succes_helmet_response.json',
            1,
            0,
            'unlock-helmet',
            200,
        ),
        (
            'personal_v1_phone_find_primary.json',
            'wind_riding_id_response.json',
            'wind_get_user_no_ride_response.json',
            'success_helmet_unlock_gprs_response.json',
            'wind_beep_and_flash_success_response.json',
            'succes_helmet_response.json',
            0,
            1,
            'blink-n-horn',
            200,
        ),
        (
            'personal_v1_phone_find_primary.json',
            'wind_fail_info_ride_id_response.json',
            'wind_get_user_no_ride_response.json',
            'fail_helmet_unlock_gprs_response.json',
            'wind_beep_and_flash_fail_response.json',
            'fail_helmet_response.json',
            0,
            0,
            'open-helmet',
            500,
        ),
        (
            'personal_v1_phone_find_primary.json',
            'wind_fail_info_ride_id_response.json',
            'wind_get_user_no_ride_response.json',
            'fail_helmet_unlock_gprs_response.json',
            'wind_beep_and_flash_fail_response.json',
            'fail_helmet_response.json',
            0,
            0,
            'blink-n-horn',
            500,
        ),
    ],
)
@pytest.mark.servicetest
async def test_success_response_helmet_unlock(
        personal_response_file,
        wind_helmet_unlock_response_file,
        wind_info_ride_id_response_file,
        expected_response_file,
        wind_user_response_file,
        wind_beep_and_flash_response_file,
        unlock_gprs_mock_call_times,
        beep_and_flash_mock_call_times,
        action,
        response_status_code,
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        jwt_secret,
        jwt_iss,
        jwt_aud,
        jwt_scope,
        wind_api_key,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler('/google-oauth/token')
    def _mock_google_oauth(request):
        decoded = jwt.decode(
            request.json['assertion'],
            jwt_secret,
            algorithms=['RS256'],
            audience='https://oauth2.googleapis.com/token',
            options={'verify_signature': False},
        )
        assert decoded.get('iss') == jwt_iss
        assert decoded.get('aud') == jwt_aud
        assert decoded.get('scope') == jwt_scope
        return load_json('google_oauth_response.json')

    @mockserver.json_handler('/firebase-api/v1/projects/123/accounts:lookup')
    def _mock_firebase_lookup_response(request):
        phone_number = request.json['phoneNumber'][0]
        users = load_json('firebase_response.json')
        for user in users:
            if user['users'][0].get('phoneNumber') == phone_number:
                return user
        return {'kind': 'test'}

    @mockserver.json_handler('/firebase-api/v1/projects/123/accounts')
    def _mock_firebase_create_user_response(request):
        return load_json('firebase_create_new_user_response.json')

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _mock_firebase_response(request):
        return load_json(personal_response_file)

    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        return load_json(wind_user_response_file)

    @mockserver.json_handler('/wind/pf/v1/boardRides/cbca7e8d5b83')
    def _mock_wind_get_info_ride_id_response(request):
        return load_json(wind_info_ride_id_response_file)

    @mockserver.json_handler('/wind/pf/v1/boards/A0000111/beep')
    def _mock_wind_beep_response(request):
        assert request.headers.get('x-lat') == x_latitude
        assert request.headers.get('x-long') == x_longitude
        return load_json(wind_beep_and_flash_response_file)

    @mockserver.json_handler('/wind/pf/v1/boards/A0000111/unlockHelmetByGprs')
    def _mock_wind_helmet_unlock_grps_response(request):
        return load_json(wind_helmet_unlock_response_file)

    @mockserver.json_handler('/wind-pd/pf/v1/user')
    def _mock_wind_get_user(request):
        assert request.headers.get('x-api-key') == wind_api_key
        firebase_uid = request.json['firebaseUid']
        users = load_json('wind_pf_v1_user_response.json')
        for user in users:
            if user['user']['firebaseUid'] == firebase_uid:
                return user
        return users[0]

    response = await taxi_talaria_misc.post(
        '/scooters/api/yandex/car/control',
        json={'action': action, 'car_id': 'cbca7e8d5b83'},
        headers={
            'lon': x_longitude,
            'lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )

    assert response.json() == load_json(expected_response_file)
    assert response.status_code == response_status_code
    assert _mock_wind_get_user.times_called == 1
    assert _mock_firebase_create_user_response.times_called == 1
    assert _mock_firebase_lookup_response.times_called == 1
    assert _mock_google_oauth.times_called == 1
    assert _mock_wind_get_info_ride_id_response.times_called == 1
    assert (
        _mock_wind_helmet_unlock_grps_response.times_called
        == unlock_gprs_mock_call_times
    )
    assert (
        _mock_wind_beep_response.times_called == beep_and_flash_mock_call_times
    )


async def test_401_response_helmet_unlock(
        taxi_talaria_misc, x_latitude, x_longitude,
):
    response = await taxi_talaria_misc.post(
        '/scooters/api/yandex/car/control',
        headers={
            'lon': x_longitude,
            'lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
        },
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}
