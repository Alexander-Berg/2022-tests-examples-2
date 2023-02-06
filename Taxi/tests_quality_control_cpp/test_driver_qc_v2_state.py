from unittest import mock

import pytest

AUTH_HEADERS = {
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_uuid',
    'X-YaTaxi-Park-Id': 'park_id',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'Accept-language': 'ru',
}


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    'mock_pass, mock_state, expected_response',
    [
        (
            'api_v1_pass_rqc_new.json',
            'api_v1_state_rqc_need_pass.json',
            'need_pass.json',
        ),
        (
            'api_v1_pass_rqc_new.json',
            'api_v1_state_rqc_need_pass_reject.json',
            'need_pass_reject.json',
        ),
        (
            'api_v1_pass_rqc_new.json',
            'api_v1_state_rqc_next_pass.json',
            'next_pass.json',
        ),
        ('api_v1_pass_rqc_new.json', 'api_v1_state_rqc_ok.json', 'ok.json'),
        ('api_v1_pass_rqc_new.json', '', 'not_found.json'),
        (
            'api_v1_pass_rqc_new.json',
            'api_v1_state_rqc_pending.json',
            'pending.json',
        ),
        (
            'api_v1_pass_rqc_new.json',
            'api_v1_state_rqc_blocked.json',
            'blocked.json',
        ),
        (
            'api_v1_pass_rqc_new.json',
            'api_v1_state_rqc_can_pass.json',
            'can_pass.json',
        ),
        (
            'api_v1_pass_rqc_pending.json',
            'api_v1_state_rqc_need_pass.json',
            'ok_pass_pending.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='qc_cpp_exam_settings_rqc.json')
@pytest.mark.experiments3()
@pytest.mark.now('2020-10-10T00:00:00+00:00')
async def test_driver_qc_v2_state(
        taxi_quality_control_cpp,
        driver_authorizer,
        quality_control,
        parks,
        tags_mocks,
        load_json,
        mock_pass,
        mock_state,
        expected_response,
):
    driver_authorizer.set_session('park_id', 'driver_session', 'driver_uuid')
    if mock_state:
        quality_control.set_state(
            'driver',
            'park_id_driver_uuid',
            'rqc',
            'mock_responses/' + mock_state,
        )
    quality_control.set_pass(
        '5d485be9e0eda8c4aafc4e96', 'mock_responses/' + mock_pass,
    )
    quality_control.set_confirmed_data(
        'driver',
        'park_id_driver_uuid',
        'mock_responses/api_v1_pass_confirmed_rqc.json',
    )
    parks.set_driver_profiles_list(
        'park_id',
        'driver_uuid',
        'mock_responses/driver_profile_list_rus.json',
    )

    response = await taxi_quality_control_cpp.post(
        '/driver/v1/qc/v2/state',
        headers=AUTH_HEADERS,
        json={
            'position': {'lon': 37.590533, 'lat': 55.733863},
            'exam_code': 'rqc',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('responses/' + expected_response)


@pytest.mark.parametrize(
    'json, mock_state, mock_pass, update_request, mock_parks, expected_code, '
    'expected_response',
    [
        (
            {'exam_code': 'identity'},
            'api_v1_state_identity.json',
            'api_v1_pass_identity_new.json',
            {
                'media': ['front', 'back'],
                'data': ['identity_confirmation', 'identity_id'],
            },
            'driver_profile_list_rus.json',
            200,
            'identity_default.json',
        ),
        (
            {'exam_code': 'identity', 'selectors': {'country_id': 'blr'}},
            'api_v1_state_identity.json',
            'api_v1_pass_identity_new.json',
            {
                'media': ['front', 'back'],
                'data': ['identity_confirmation', 'identity_id'],
            },
            'driver_profile_list_rus.json',
            200,
            'identity_non_default_country.json',
        ),
        (
            {
                'exam_code': 'identity',
                'selectors': {
                    'country_id': 'rus',
                    'identity_id': 'sailor_rus',
                },
            },
            'api_v1_state_identity.json',
            'api_v1_pass_identity_new.json',
            {
                'media': ['front', 'back', 'selfie'],
                'data': ['identity_confirmation', 'identity_id'],
            },
            'driver_profile_list_rus.json',
            200,
            'identity_non_default_document.json',
        ),
        (
            {
                'exam_code': 'identity',
                'selectors': {
                    'country_id': 'blr',
                    'identity_id': 'sailor_rus',
                },
            },
            'api_v1_state_identity.json',
            'api_v1_pass_identity_new.json',
            {'media': ['front', 'back'], 'data': ['identity_id']},
            'driver_profile_list_blr.json',
            200,
            'identity_incorrect_document.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='qc_cpp_exam_settings_identity.json')
@pytest.mark.experiments3()
async def test_driver_qc_v2_state_identity(
        taxi_quality_control_cpp,
        driver_authorizer,
        quality_control,
        parks,
        tags_mocks,
        load_json,
        json,
        mock_state,
        mock_pass,
        update_request,
        mock_parks,
        expected_code,
        expected_response,
):
    driver_authorizer.set_session('park_id', 'driver_session', 'driver_uuid')
    quality_control.set_state(
        'driver',
        'park_id_driver_uuid',
        'identity',
        'mock_responses/' + mock_state,
    )
    quality_control.set_pass(
        '5d485be9e0eda8c4aafc4e96', 'mock_responses/' + mock_pass,
    )
    quality_control.set_pass_update(
        '5d485be9e0eda8c4aafc4e96',
        update_request,
        'mock_responses/api_v1_pass_update_identity.json',
    )
    quality_control.set_confirmed_data(
        'driver',
        'park_id_driver_uuid',
        'mock_responses/api_v1_pass_confirmed_empty.json',
    )
    parks.set_driver_profiles_list(
        'park_id', 'driver_uuid', 'mock_responses/' + mock_parks,
    )
    json['position'] = {'lon': 37.590533, 'lat': 55.733863}
    response = await taxi_quality_control_cpp.post(
        '/driver/v1/qc/v2/state', headers=AUTH_HEADERS, json=json,
    )
    assert response.status_code == 200
    assert response.json() == load_json('responses/' + expected_response)


@pytest.mark.parametrize(
    'json, mock_state, mock_pass, mock_pass_update, update_request, '
    'mock_parks, expected_code, expected_response',
    [
        (
            {
                'position': {'lon': 37.590533, 'lat': 55.733863},
                'exam_code': 'vaccination',
            },
            'api_v1_state_vaccination.json',
            'api_v1_pass_vaccination_new.json',
            'api_v1_pass_update_vaccination_data.json',
            {'data': ['scan_result_id']},
            'driver_profile_list_rus.json',
            200,
            'vac_no_switchers.json',
        ),
        (
            {
                'position': {'lon': 37.590533, 'lat': 55.733863},
                'exam_code': 'vaccination',
                'switchers': {
                    'type': 'vaccination',
                    'verification_type': 'certificate_photo',
                },
            },
            'api_v1_state_vaccination.json',
            'api_v1_pass_vaccination_new.json',
            'api_v1_pass_update_vaccination_media.json',
            {'media': ['front']},
            'driver_profile_list_rus.json',
            200,
            'vac_one_page_certificate.json',
        ),
        (
            {
                'position': {'lon': 37.590533, 'lat': 55.733863},
                'exam_code': 'vaccination',
                'switchers': {
                    'type': 'vaccination',
                    'verification_type': 'certificate_photo',
                    'certificate_type': 'two_page_certificate',
                },
            },
            'api_v1_state_vaccination.json',
            'api_v1_pass_vaccination_new.json',
            'api_v1_pass_update_vaccination_media2.json',
            {'media': ['front', 'back']},
            'driver_profile_list_rus.json',
            200,
            'vac_two_page_certificate.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='qc_cpp_exam_settings_vaccination.json')
@pytest.mark.experiments3(filename='qc_cpp_vaccination_settings.json')
@pytest.mark.experiments3()
async def test_driver_qc_v2_state_vaccination(
        taxi_quality_control_cpp,
        driver_authorizer,
        quality_control,
        parks,
        tags_mocks,
        load_json,
        json,
        mock_state,
        mock_pass,
        mock_pass_update,
        update_request,
        mock_parks,
        expected_code,
        expected_response,
):
    driver_authorizer.set_session('park_id', 'driver_session', 'driver_uuid')
    quality_control.set_state(
        'driver',
        'park_id_driver_uuid',
        'vaccination',
        'mock_responses/' + mock_state,
    )
    quality_control.set_pass(
        '5d485be9e0eda8c4aafc4e92', 'mock_responses/' + mock_pass,
    )
    quality_control.set_pass_update(
        '5d485be9e0eda8c4aafc4e92',
        update_request,
        'mock_responses/' + mock_pass_update,
    )
    quality_control.set_confirmed_data(
        'driver',
        'park_id_driver_uuid',
        'mock_responses/api_v1_pass_confirmed_empty.json',
    )
    parks.set_driver_profiles_list(
        'park_id', 'driver_uuid', 'mock_responses/' + mock_parks,
    )

    response = await taxi_quality_control_cpp.post(
        '/driver/v1/qc/v2/state', headers=AUTH_HEADERS, json=json,
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == load_json('responses/' + expected_response)


@pytest.mark.parametrize(
    'json, mock_state, mock_pass, mock_pass_update, '
    'mock_data_confirmed, update_request, mock_parks, '
    'expected_response, park_id, pass_id, exam_code',
    [
        (
            {'exam_code': 'identity'},
            'api_v1_state_identity.json',
            'api_v1_pass_identity_new.json',
            'api_v1_pass_update_identity.json',
            'api_v1_pass_confirmed_empty.json',
            {
                'media': ['front', 'back'],
                'data': ['identity_confirmation', 'identity_id'],
            },
            'driver_profile_list_rus.json',
            'identity_default.json',
            'park_id',
            '5d485be9e0eda8c4aafc4e96',
            'identity',
        ),
        (
            {'exam_code': 'identity'},
            'api_v1_state_identity.json',
            'api_v1_pass_identity_new.json',
            'api_v1_pass_update_identity.json',
            'api_v1_pass_confirmed_empty.json',
            {'media': ['front', 'back'], 'data': ['identity_id']},
            'driver_profile_list_rus.json',
            'identity_confirmation_not_required.json',
            'park_id_required_false',
            '5d485be9e0eda8c4aafc4e96',
            'identity',
        ),
        (
            {'exam_code': 'vaccination'},
            'api_v1_state_vaccination.json',
            'api_v1_pass_vaccination_new.json',
            'api_v1_pass_update_vaccination_data.json',
            'api_v1_pass_confirmed_empty.json',
            {'data': ['vaccination_confirmation', 'scan_result_id']},
            'driver_profile_list_rus.json',
            'vac_no_switchers_required_true.json',
            'park_id',
            '5d485be9e0eda8c4aafc4e92',
            'vaccination',
        ),
        (
            {'exam_code': 'vaccination'},
            'api_v1_state_vaccination.json',
            'api_v1_pass_vaccination_new.json',
            'api_v1_pass_update_vaccination_data.json',
            'api_v1_pass_confirmed_empty.json',
            {'data': ['scan_result_id']},
            'driver_profile_list_rus.json',
            'vac_no_switchers.json',
            'park_id_required_false',
            '5d485be9e0eda8c4aafc4e92',
            'vaccination',
        ),
        (
            {'exam_code': 'vaccination'},
            'api_v1_state_vaccination.json',
            'api_v1_pass_vaccination_new.json',
            'api_v1_pass_update_vaccination_data.json',
            'api_v1_pass_confirmed_empty.json',
            {'data': ['vaccination_confirmation', 'scan_result_id']},
            'driver_profile_list_rus.json',
            'vac_no_switchers_required_true.json',
            'park_id_frequency_one_time',
            '5d485be9e0eda8c4aafc4e92',
            'vaccination',
        ),
        pytest.param(
            {'exam_code': 'vaccination'},
            'api_v1_state_vaccination.json',
            'api_v1_pass_vaccination_new.json',
            'api_v1_pass_update_vaccination_data.json',
            'api_v1_pass_confirmed_empty.json',
            {'data': ['scan_result_id']},
            'driver_profile_list_rus.json',
            'vac_no_switchers_no_confirmation.json',
            'park_id_frequency_one_time',
            '5d485be9e0eda8c4aafc4e92',
            'vaccination',
            marks=pytest.mark.filldb(confirmations='vaccination'),
        ),
        pytest.param(
            {'exam_code': 'vaccination'},
            'api_v1_state_vaccination.json',
            'api_v1_pass_vaccination_new.json',
            'api_v1_pass_update_vaccination_data.json',
            'api_v1_pass_confirmed_empty.json',
            {
                'data': [
                    'vaccination_confirmation_unconfirmed',
                    'scan_result_id',
                ],
            },
            'driver_profile_list_rus.json',
            'vac_many_confirmations.json',
            'park_id_many_confirmations',
            '5d485be9e0eda8c4aafc4e92',
            'vaccination',
            marks=pytest.mark.filldb(confirmations='many'),
        ),
    ],
)
@pytest.mark.experiments3(filename='qc_cpp_exp3_confirmation_configs.json')
@pytest.mark.experiments3(filename='qc_cpp_exam_settings_identity.json')
@pytest.mark.experiments3(filename='qc_cpp_vaccination_settings.json')
@pytest.mark.experiments3(filename='qc_cpp_exam_settings_vaccination.json')
@pytest.mark.experiments3()
async def test_driver_qc_v2_state_confirmation(
        taxi_quality_control_cpp,
        driver_authorizer,
        quality_control,
        parks,
        tags_mocks,
        load_json,
        json,
        mock_state,
        mock_pass,
        mock_pass_update,
        mock_data_confirmed,
        update_request,
        mock_parks,
        expected_response,
        park_id,
        pass_id,
        exam_code,
):
    driver_authorizer.set_session(park_id, 'driver_session', 'driver_uuid')
    quality_control.set_state(
        'driver',
        f'{park_id}_driver_uuid',
        exam_code,
        'mock_responses/' + mock_state,
    )
    quality_control.set_pass(pass_id, 'mock_responses/' + mock_pass)
    quality_control.set_pass_update(
        pass_id, update_request, 'mock_responses/' + mock_pass_update,
    )
    quality_control.set_confirmed_data(
        'driver',
        f'{park_id}_driver_uuid',
        'mock_responses/' + mock_data_confirmed,
    )
    parks.set_driver_profiles_list(
        park_id, 'driver_uuid', 'mock_responses/' + mock_parks,
    )
    json['position'] = {'lon': 37.590533, 'lat': 55.733863}

    with mock.patch.dict(AUTH_HEADERS, {'X-YaTaxi-Park-Id': park_id}):
        response = await taxi_quality_control_cpp.post(
            '/driver/v1/qc/v2/state', headers=AUTH_HEADERS, json=json,
        )
    assert response.status_code == 200
    assert response.json() == load_json('responses/' + expected_response)


@pytest.mark.parametrize(
    'tags, update_request, expected_response',
    [
        (
            ['tag1'],
            {
                'media': ['front', 'back'],
                'data': ['identity_confirmation', 'identity_id'],
            },
            'identity_default.json',
        ),
        (
            ['tag1', 'tag2'],
            {'media': ['front', 'back'], 'data': ['identity_id']},
            'identity_confirmation_not_required.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='qc_cpp_exp3_confirmation_configs.json')
@pytest.mark.experiments3(filename='qc_cpp_exam_settings_identity.json')
@pytest.mark.experiments3(filename='qc_cpp_vaccination_settings.json')
@pytest.mark.experiments3(filename='qc_cpp_exam_settings_vaccination.json')
@pytest.mark.experiments3()
async def test_driver_qc_v2_state_tags(
        taxi_quality_control_cpp,
        driver_authorizer,
        quality_control,
        parks,
        tags_mocks,
        load_json,
        tags,
        update_request,
        expected_response,
):
    driver_authorizer.set_session('park_id', 'driver_session', 'driver_uuid')
    quality_control.set_state(
        'driver',
        'park_id_driver_uuid',
        'identity',
        'mock_responses/api_v1_state_identity.json',
    )
    quality_control.set_pass(
        '5d485be9e0eda8c4aafc4e96',
        'mock_responses/api_v1_pass_identity_new.json',
    )

    quality_control.set_pass_update(
        '5d485be9e0eda8c4aafc4e96',
        update_request,
        'mock_responses/api_v1_pass_update_identity.json',
    )

    quality_control.set_confirmed_data(
        'driver',
        'park_id_driver_uuid',
        'mock_responses/api_v1_pass_confirmed_empty.json',
    )
    parks.set_driver_profiles_list(
        'park_id',
        'driver_uuid',
        'mock_responses/driver_profile_list_rus.json',
    )

    tags_mocks.set_tags(tags)

    json = {
        'exam_code': 'identity',
        'position': {'lon': 37.590533, 'lat': 55.733863},
    }

    with mock.patch.dict(AUTH_HEADERS, {'X-YaTaxi-Park-Id': 'park_id'}):
        response = await taxi_quality_control_cpp.post(
            '/driver/v1/qc/v2/state', headers=AUTH_HEADERS, json=json,
        )
    assert response.status_code == 200
    assert response.json() == load_json('responses/' + expected_response)
