import pytest


@pytest.mark.config(
    TALARIA_MISC_AU10TIX_SETTINGS={
        'default_country': 'USA',
        'mobile_success_redirect_url': 'https://mobile.example.com/success',
        'mobile_error_redirect_url': 'https://mobile.example.com/error',
        'mobile_redirect_behavior': 'always',
        'processingflow': 'idv',
        'shorturl': True,
    },
)
async def test_create_session(
        mockserver,
        load_json,
        default_pa_headers,
        taxi_talaria_misc,
        wind_user_auth_mock,
):
    @mockserver.json_handler(
        '/wind-pd/pf/v1/driverLicense/au10tix/secureMeSession',
    )
    def _mock_wind_driver_license_verification(request):
        assert request.json == load_json(
            'wind_driver_license_init_secureme_session_request.json',
        )
        return load_json(
            'wind_driver_license_init_secureme_session_response.json',
        )

    response = await taxi_talaria_misc.post(
        '/4.0/talaria/v1/driver-license/create-au10tix-secureme-session',
        json={},
        headers={'x-request-id': 'request_id', **default_pa_headers()},
    )
    assert response.status_code == 200
    assert response.json() == {'link': {'url': 'au10tix_webview_url'}}
    assert _mock_wind_driver_license_verification.times_called == 1


@pytest.mark.config(
    TALARIA_MISC_DRIVER_LICENSE_VERIFICATION_NOTIFICATION={
        'verified': {'deeplink': 'verified_deeplink'},
        'rejected': {'deeplink': 'rejected_deeplink'},
    },
)
@pytest.mark.translations(
    client_messages={
        'talaria.driver_license_verification.notification.verified.title': {
            'en': 'verified_title',
        },
        'talaria.driver_license_verification.notification.verified.subtitle': {
            'en': 'verified_subtitle',
        },
        'talaria.driver_license_verification.notification.rejected.title': {
            'en': 'rejected_title',
        },
        'talaria.driver_license_verification.notification.rejected.subtitle': {
            'en': 'rejected_subtitle',
        },
    },
)
@pytest.mark.parametrize(
    [
        'wind_result',
        'primary_processing_result',
        'processing_result_remarks',
        'face_comparison_status',
        'expected_status',
    ],
    [
        (2, 0, [0], 0, 'verified'),
        (3, 0, [0], 0, 'rejected'),
        (None, 0, [0], 0, 'verified'),
        (None, 0, [0], None, 'rejected'),
        (None, 20, [0], 0, 'rejected'),
        (None, 0, [0, 100], 0, 'rejected'),
        (None, 0, [0], 20, 'rejected'),
    ],
)
async def test_au10tix_callback(
        mockserver,
        load_json,
        taxi_talaria_misc,
        wind_result,
        primary_processing_result,
        processing_result_remarks,
        face_comparison_status,
        expected_status,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _mock_ucommunications(request):
        assert request.json == {
            'data': {
                'payload': {
                    'deeplink': f'{expected_status}_deeplink',
                    'driver_license_check_result': expected_status,
                    'notification': {
                        'subtitle': f'{expected_status}_subtitle',
                        'title': f'{expected_status}_title',
                    },
                    'type': 'scooters-driver-license',
                },
            },
            'intent': 'talaria.driver_license_verification',
            'user': 'yandex_user_id',
        }
        return {}

    request = load_json('au10tix_calback_request.json')
    if wind_result is not None:
        request['wind_result'] = dict(driver_license_status=wind_result)

    result_data = request['au10tix_parameters']['resultData']
    doc_status_report = result_data['DocumentStatusReport2']
    doc_status_report['PrimaryProcessingResult'] = primary_processing_result
    doc_status_report['ProcessingResultRemarks'] = processing_result_remarks
    if face_comparison_status is not None:
        face_comp_report = result_data['FaceComparisonReport']
        face_comp_report['CompletionStatus'] = face_comparison_status
    else:
        result_data.pop('FaceComparisonReport')
    response = await taxi_talaria_misc.post(
        '/talaria/v1/driver-license/au10tix-callback', json=request,
    )

    assert response.status_code == 200
    assert _mock_ucommunications.times_called == 1
