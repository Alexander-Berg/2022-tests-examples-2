import hashlib

import pytest


HEADERS = {
    'X-Remote-IP': '1.1.1.1',
    'Accept-Language': 'ru_RU',
    'User-Agent': 'Taximeter 9.22 (2222)',
}


def _hash_string(s):  # pylint: disable=invalid-name
    return hashlib.sha256(
        f'{s}DRIVER_LOGIN_SECRET'.encode('utf-8'),
    ).hexdigest()


def _token_key_by_driver(key):
    return f'Driver:AuthToken:{_hash_string(key)}'


def _token_key(key):
    return _token_key_by_driver(key)


@pytest.mark.experiments3(filename='experiment_selfemployed_phone.json')
@pytest.mark.now('2019-04-18T13:10:00.786Z')
@pytest.mark.parametrize('step', ['sms_code', 'phone_code', 'phone'])
async def test_selfemployed_phone_right_steps(
        taxi_driver_login,
        redis_store,
        mockserver,
        mock_driver_order_misc,
        mock_driver_authorizer,
        mock_client_notify,
        yagr_position_store,
        step,
):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def _confirm_commit(request):
        return {'status': 'ok'}

    @mockserver.json_handler('/passport-internal/1/track/')
    def _pi_track(request):
        return {'id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def _pi_confirm_submit(request):
        return {'track_id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/parks-certifications/v1/parks/certifications/list',
    )
    def _parks_certifications(request):
        return {'certifications': []}

    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-phone-pd-id/v1',
    )
    def _find_drafts(request):
        request_json = request.json
        assert 'status' in request_json
        assert request_json['status'] == 'draft'
        return {
            'profiles': [
                {
                    'park_id': 'park_id1',
                    'driver_id': 'driver_id1',
                    'profession': 'scooter',
                    'status': 'draft',
                    'city': 'Москва',
                },
                {
                    'park_id': 'park_id2',
                    'driver_id': 'driver_id1',
                    'profession': 'scooter',
                    'status': 'draft',
                    'city': 'Москва',
                },
            ],
        }

    phone = '+79991112233'
    redis_store.set(f'Driver:SMS:TrackId:{phone}', 'sms_track_id')
    redis_store.set(_token_key(phone), _hash_string('token'))

    headers = dict(HEADERS)
    headers['X-Remote-IP'] = '77.72.243.13'  # random Novosibirsk IP

    response = await taxi_driver_login.post(
        'v1/driver/login',
        params={'token': 'token'},
        headers=headers,
        data={'phone': phone, 'step': step, 'sms_code': '0000'},
    )
    assert response.status_code == 200

    content = response.json()
    assert content.pop('token')

    assert content == {
        'step': 'selfemployed',
        'selfemployed_info': {
            'park_id': 'park_id1',
            'driver_id': 'driver_id1',
            'profession': 'scooter',
        },
    }


@pytest.mark.config(
    DRIVER_LOGIN_DRIVER_STATUS_CLIENT_FAILURE_SETTINGS={
        'strategy': 'force_busy',
    },
)
@pytest.mark.experiments3(filename='experiment_selfemployed_phone.json')
@pytest.mark.translations(
    taximeter_backend_api_controllers={
        'Login_Error_InternalServerError': {'ru': 'Internal Error'},
    },
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
@pytest.mark.parametrize(
    'step, expected_step',
    [
        pytest.param('send_sms', 'sms_code', id='selfemployed_phone_send_sms'),
        pytest.param('select_db', 'login', id='selfemployed_phone_select_db'),
    ],
)
async def test_selfemployed_phone_other_step(
        taxi_driver_login,
        redis_store,
        mockserver,
        mock_fleet_parks_list,
        fleet_vehicles,
        driver_protocol,
        driver_modes,
        driver_support,
        driver_profiles_info,
        unique_drivers,
        yagr_position_store,
        mock_driver_order_misc,
        mock_driver_authorizer,
        mock_client_notify,
        step,
        expected_step,
):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def _confirm_commit(request):
        return {'status': 'ok'}

    @mockserver.json_handler(
        '/parks-certifications/v1/parks/certifications/list',
    )
    def _parks_certifications(request):
        return {'certifications': []}

    @mockserver.json_handler('/passport-internal/1/track/')
    def _pi_track(request):
        return {'id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def _pi_confirm_submit(request):
        return {'track_id': 'track_id', 'status': 'ok'}

    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-phone-pd-id/v1',
    )
    def _find_drafts(request):
        return {'profiles': []}

    mock_driver_order_misc.set_on_order(
        [
            {
                'park_id': 'dbid_by_phone',
                'driver_profile_id': 'uuid_by_phone',
                'on_order': False,
            },
        ],
    )

    phone = '+79991112233'
    redis_store.set(f'Driver:SMS:TrackId:{phone}', 'sms_track_id')
    redis_store.set(_token_key(phone), _hash_string('token'))

    headers = dict(HEADERS)
    headers['X-Remote-IP'] = '77.72.243.13'  # random Novosibirsk IP

    response = await taxi_driver_login.post(
        'v1/driver/login',
        params={'token': 'token'},
        headers=headers,
        data={
            'phone': phone,
            'step': step,
            'db': 'dbid',
            'token': 'token',
            'deviceId': '00001111',
            'uuid': 'metrica_uuid',
            'metricaDeviceId': '9c19ad8723c6a7e3f4f5709e8179d58b',
        },
    )
    assert response.status_code == 200
    assert response.json()['step'] == expected_step

    assert _find_drafts.times_called == 0
