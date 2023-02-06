import pytest


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    'exam_code, entity_type, mock_state, mock_pass, mock_data_confirmed,'
    'expected_code, expected_response',
    [
        (
            'rqc',
            'driver',
            'api_v1_state_rqc.json',
            'api_v1_pass_rqc_new.json',
            'api_v1_pass_confirmed_rqc.json',
            200,
            'expected_response1.json',
        ),
        (
            'rqc',
            'driver',
            'api_v1_state_rqc.json',
            'api_v1_pass_rqc_pending.json',
            'api_v1_pass_confirmed_rqc.json',
            200,
            'expected_response2.json',
        ),
        (
            'rqc',
            'driver',
            'api_v1_state_rqc.json',
            'api_v1_pass_rqc_new.json',
            'api_v1_pass_confirmed_empty.json',
            200,
            'expected_response3.json',
        ),
        (
            'dkvu',
            'driver',
            'api_v1_state_dkvu.json',
            'api_v1_pass_dkvu_new.json',
            'api_v1_pass_confirmed_empty.json',
            200,
            'expected_response4.json',
        ),
        (
            'sts',
            'car',
            'api_v1_state_sts.json',
            'api_v1_pass_sts_new.json',
            'api_v1_pass_confirmed_empty.json',
            200,
            'expected_response5.json',
        ),
        (
            'vaccination',
            'driver',
            'api_v1_state_vaccination.json',
            'api_v1_pass_vaccination_new.json',
            'api_v1_pass_confirmed_empty.json',
            200,
            'expected_response10.json',
        ),
    ],
)
@pytest.mark.experiments3()
@pytest.mark.now('2020-10-10T00:00:00+00:00')
async def test_driver_qc_v1_state(
        taxi_quality_control_cpp,
        driver_authorizer,
        quality_control,
        parks,
        tags_mocks,
        load_json,
        exam_code,
        entity_type,
        mock_state,
        mock_pass,
        mock_data_confirmed,
        expected_code,
        expected_response,
):
    driver_authorizer.set_session('park_id', 'driver_session', 'driver_uuid')
    entity_id = 'park_id_' + (
        'car_id' if entity_type == 'car' else 'driver_uuid'
    )
    if mock_state:
        quality_control.set_state(
            entity_type, entity_id, exam_code, 'mock_responses/' + mock_state,
        )
    quality_control.set_pass(
        '5d485be9e0eda8c4aafc4e96', 'mock_responses/' + mock_pass,
    )
    quality_control.set_confirmed_data(
        entity_type, entity_id, 'mock_responses/' + mock_data_confirmed,
    )
    parks.set_driver_profiles_list(
        'park_id',
        'driver_uuid',
        'mock_responses/driver_profile_list_rus.json',
    )

    response = await taxi_quality_control_cpp.post(
        '/driver/qc/v1/state',
        params={'park_id': 'park_id'},
        json={'exam_code': exam_code},
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Driver-Session': 'driver_session',
        },
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
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
            'expected_response6.json',
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
            'expected_response7.json',
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
            'expected_response8.json',
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
            'expected_response9.json',
        ),
    ],
)
@pytest.mark.experiments3()
async def test_driver_qc_v1_state_identity(
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

    response = await taxi_quality_control_cpp.post(
        '/driver/qc/v1/state',
        params={'park_id': 'park_id'},
        json=json,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Driver-Session': 'driver_session',
        },
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == load_json('responses/' + expected_response)


@pytest.mark.parametrize(
    'json, mock_state, mock_pass, mock_pass_update, '
    'mock_data_confirmed, update_request, mock_parks, '
    'expected_code, expected_response, park_id, exam_id',
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
            200,
            'expected_response6.json',
            'park_id',
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
            200,
            'expected_response6_required_false.json',
            'park_id_required_false',
            'identity',
        ),
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
            200,
            'expected_response6.json',
            'park_id_frequency_one_time',
            'identity',
        ),
        pytest.param(
            {'exam_code': 'identity'},
            'api_v1_state_identity.json',
            'api_v1_pass_identity_new.json',
            'api_v1_pass_update_identity.json',
            'api_v1_pass_confirmed_empty.json',
            {'media': ['front', 'back'], 'data': ['identity_id']},
            'driver_profile_list_rus.json',
            200,
            'expected_response6_no_confirmation.json',
            'park_id_frequency_one_time',
            'identity',
            marks=pytest.mark.filldb(confirmations='identity'),
        ),
        (
            {'exam_code': 'identity'},
            'api_v1_state_identity.json',
            'api_v1_pass_identity_new.json',
            'api_v1_pass_update_identity.json',
            'api_v1_pass_confirmed_empty.json',
            {'media': ['front', 'back'], 'data': ['identity_id']},
            'driver_profile_list_rus.json',
            200,
            'expected_response6_required_false.json',
            'park_id_frequency_one_time_required_false',
            'identity',
        ),
        pytest.param(
            {'exam_code': 'identity'},
            'api_v1_state_identity.json',
            'api_v1_pass_identity_new.json',
            'api_v1_pass_update_identity.json',
            'api_v1_pass_confirmed_empty.json',
            {'media': ['front', 'back'], 'data': ['identity_id']},
            'driver_profile_list_rus.json',
            200,
            'expected_response6_no_confirmation.json',
            'park_id_frequency_one_time_required_false',
            'identity',
            marks=pytest.mark.filldb(
                confirmations='identity_park_id_required_false',
            ),
        ),
        (
            {'exam_code': 'dkvu'},
            'api_v1_state_dkvu.json',
            'api_v1_pass_dkvu_new.json',
            'api_v1_pass_update_dkvu.json',
            'api_v1_pass_confirmed_empty.json',
            {'data': ['dkvu_confirmation']},
            'driver_profile_list_rus.json',
            200,
            'expected_response4_required_true.json',
            'park_id',
            'dkvu',
        ),
        (
            {'exam_code': 'dkvu'},
            'api_v1_state_dkvu.json',
            'api_v1_pass_dkvu_new.json',
            'api_v1_pass_update_dkvu.json',
            'api_v1_pass_confirmed_empty.json',
            {},
            'driver_profile_list_rus.json',
            200,
            'expected_response4.json',
            'park_id_required_false',
            'dkvu',
        ),
        (
            {'exam_code': 'dkvu'},
            'api_v1_state_dkvu.json',
            'api_v1_pass_dkvu_new.json',
            'api_v1_pass_update_dkvu.json',
            'api_v1_pass_confirmed_empty.json',
            {'data': ['dkvu_confirmation']},
            'driver_profile_list_rus.json',
            200,
            'expected_response4_required_true.json',
            'park_id_frequency_one_time',
            'dkvu',
        ),
        pytest.param(
            {'exam_code': 'dkvu'},
            'api_v1_state_dkvu.json',
            'api_v1_pass_dkvu_new.json',
            'api_v1_pass_update_dkvu.json',
            'api_v1_pass_confirmed_empty.json',
            {},
            'driver_profile_list_rus.json',
            200,
            'expected_response4_no_confirmation.json',
            'park_id_frequency_one_time',
            'dkvu',
            marks=pytest.mark.filldb(confirmations='dkvu'),
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3.json')
async def test_driver_qc_v1_state_confirmation(
        taxi_quality_control_cpp,
        driver_authorizer,
        quality_control,
        parks,
        load_json,
        json,
        tags_mocks,
        mock_state,
        mock_pass,
        mock_pass_update,
        mock_data_confirmed,
        update_request,
        mock_parks,
        expected_code,
        expected_response,
        park_id,
        exam_id,
):
    driver_authorizer.set_session(park_id, 'driver_session', 'driver_uuid')
    quality_control.set_state(
        'driver',
        f'{park_id}_driver_uuid',
        exam_id,
        'mock_responses/' + mock_state,
    )
    quality_control.set_pass(
        '5d485be9e0eda8c4aafc4e96', 'mock_responses/' + mock_pass,
    )

    if mock_pass_update:
        quality_control.set_pass_update(
            '5d485be9e0eda8c4aafc4e96',
            update_request,
            'mock_responses/' + mock_pass_update,
        )

    quality_control.set_confirmed_data(
        'driver',
        f'{park_id}_driver_uuid',
        'mock_responses/' + mock_data_confirmed,
    )
    parks.set_driver_profiles_list(
        park_id, 'driver_uuid', 'mock_responses/' + mock_parks,
    )

    response = await taxi_quality_control_cpp.post(
        '/driver/qc/v1/state',
        params={'park_id': park_id},
        json=json,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Driver-Session': 'driver_session',
        },
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == load_json('responses/' + expected_response)
