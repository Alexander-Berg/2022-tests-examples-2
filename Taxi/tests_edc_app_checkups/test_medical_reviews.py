import pytest

CHECKUP_ID_2 = '5e000000-5c37-4ef8-a9d5-cf5fef3e4959'
NOT_EXISTS_CHECKUP_ID = '0e000000-5c37-4ef8-a9d5-cf5fef3e4959'
NOT_EXISTS_MEDICAL_REVIEW_ID = '000e70f6-3fd3-46d0-b953-167ef884c004'
EXIST_MEDICAL_REVIEW_ID = '678e70f6-3fd3-46d0-b953-167ef884c004'
PHYSICIAN_PASSPORT_UID_1 = '123456787'

MEDICAL_REVIEW_WITH_CHECKUP = {
    'checkup': {
        'created_at': '2020-04-09T08:25:18.926246+00:00',
        'creator': {
            'display_name': 'Петров Семен Семенович',
            'id': '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
        },
        'driver': {
            'birth_date': '1990-01-07',
            'first_name': 'Семен',
            'id': '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
            'last_name': 'Петров',
            'license': '1234567890',
            'middle_name': 'Семенович',
            'sex': 'male',
        },
        'id': '4e991007-5c37-4ef8-a9d5-cf5fef3e4959',
        'number': '00000000000005721518',
        'park': {
            'address': 'ул. Арбат, 15',
            'city_id': '02677bb0-e4b6-45a1-a468-2c35c5916422',
            'id': '2d3d692a-cccd-4f13-acab-f24d11c3b6c3',
            'name': 'Acme Ltd',
            'phone': '+74852200000',
            'primary_state_registration_number': '1037727038315',
        },
        'status': 'in_progress',
        'vehicle': {
            'id': '7a9b5d6f-c0e5-4304-8487-d3981c5852ef',
            'license_plate': 'А001АА',
            'model': 'Logan',
            'type': 'car',
            'year': '2005',
        },
    },
    'id': '678e70f6-3fd3-46d0-b953-167ef884c004',
    'park_id': '22222222cccd4f13acabf24d11c3b6c3',
    'passed_at': '2020-04-09T08:49:33.378941+00:00',
    'resolution_is_passed': True,
    'resolution': {
        'temperature': {'value': 36.6},
        'heart_rate': 75,
        'mucous_membranes_are_ok': True,
        'blood_pressure': {'systolic': 120, 'diastolic': 80},
        'is_passed': True,
    },
    'physician': {
        'job_position': 'фельдшер',
        'display_name': 'Врачев Врач Врачевич',
        'id': '3b35047d1d4d4abc903544ffbba00d46',
    },
}

MEDICAL_REVIEW_WITH_CHECKUP_EXTERNAL = {
    'checkup': {
        'created_at': '2020-04-09T08:25:18.926246+00:00',
        'creator': {
            'display_name': 'Петров Семен Семенович',
            'id': '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
        },
        'driver': {
            'birth_date': '1990-01-07',
            'first_name': 'Семен',
            'id': '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
            'last_name': 'Петров',
            'license': '1234567890',
            'middle_name': 'Семенович',
            'sex': 'male',
        },
        'id': '4e991007-5c37-4ef8-a9d5-cf5fef3e4988',
        'number': '00000000000005721528',
        'park': {
            'address': 'ул. Арбат, 15',
            'city_id': '02677bb0-e4b6-45a1-a468-2c35c5916422',
            'id': '2d3d692a-cccd-4f13-acab-f24d11c3b6c3',
            'name': 'Acme Ltd',
            'phone': '+74852200000',
            'primary_state_registration_number': '1037727038315',
        },
        'status': 'in_progress',
        'vehicle': {
            'id': '7a9b5d6f-c0e5-4304-8487-d3981c5852ef',
            'license_plate': 'А001АА',
            'model': 'Logan',
            'type': 'car',
            'year': '2005',
        },
    },
    'id': '678e70f6-3fd3-46d0-b953-167ef884c022',
    'park_id': '22222222cccd4f13acabf24d11c3b6c3',
    'passed_at': '2020-04-08T08:49:33.378941+00:00',
    'resolution_is_passed': True,
    'physician': {
        'job_position': 'фельдшер',
        'display_name': 'Врачев Врач Врачевич',
        'id': '3b35047d1d4d4abc903544ffbba00d46',
    },
}


NEW_MEDICAL_REVIEW_1 = {
    'id': '10101010-f122-426d-ac36-91d0c88341be',
    'checkup_id': CHECKUP_ID_2,
    'park_id': '11111111cccd4f13acabf24d11c3b6c3',
    'passed_at': '2020-04-09 08:33:18.926246',
    'resolution': {
        'temperature': {'value': 36.4},
        'blood_pressure': {'systolic': 125, 'diastolic': 85},
        'heart_rate': 75,
        'mucous_membranes_are_ok': True,
        'is_passed': True,
    },
    'resolution_is_passed': True,
    'physician_id': '3b35047d1d4d4abc903544ffbba00d46',
    'physician': {
        'job_position': '',
        'display_name': 'Врачев Врач Врачевич',
        'id': '3b35047d1d4d4abc903544ffbba00d46',
    },
}


MEDICAL_REVIEW_FIELDS = [
    'id',
    'checkup_id',
    'physician_id',
    'physician',
    'park_id',
    'resolution_is_passed',
    'resolution',
    'passed_at',
]


def _select_medical_review(medical_review_id, pgsql):
    cursor = pgsql['edc_app_checkups'].cursor()
    cursor.execute(
        f"""
        SELECT {", ".join(MEDICAL_REVIEW_FIELDS)}
        from edc_app_checkups.medical_reviews
        WHERE id='{medical_review_id}';""",
    )
    row = cursor.fetchone()
    medical_review = {}
    if row:
        assert len(row) == len(MEDICAL_REVIEW_FIELDS)
        for i, field in enumerate(MEDICAL_REVIEW_FIELDS):
            if row[i]:
                medical_review[field] = row[i]
        medical_review['passed_at'] = str(medical_review['passed_at'])
    return medical_review


def _select_checkup_updated_fields(checkup_id, pgsql):
    cursor = pgsql['edc_app_checkups'].cursor()
    cursor.execute(
        f"""
        SELECT medical_review_id, status, passed_at
        from edc_app_checkups.checkups
        WHERE id='{checkup_id}';""",
    )
    row = cursor.fetchone()
    updated_fields = {}
    if row:
        updated_fields['medical_review_id'] = row[0]
        updated_fields['status'] = row[1]
        updated_fields['passed_at'] = row[2]
    return updated_fields


@pytest.fixture(name='dispatcher_access_control')
def _dispatcher_access_control(mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock_dispatcher_access_control(request):
        return {
            'users': [
                {
                    'id': NEW_MEDICAL_REVIEW_1['physician']['id'],
                    'park_id': NEW_MEDICAL_REVIEW_1['park_id'],
                    'display_name': 'Врачев Врач Врачевич',
                    'passport_uid': PHYSICIAN_PASSPORT_UID_1,
                    'is_enabled': True,
                    'is_confirmed': True,
                    'is_superuser': True,
                    'is_usage_consent_accepted': True,
                },
            ],
            'limit': 1,
            'offset': 0,
        }


RESOLUTION = {
    'temperature': {'value': 36.4},
    'blood_pressure': {'systolic': 125, 'diastolic': 85},
    'heart_rate': 75,
    'mucous_membranes_are_ok': True,
    'is_passed': True,
}
RESOLUTION_2 = {
    'temperature': {'value': 36.4},
    'blood_pressure': {'systolic': 185, 'diastolic': 85},
    'heart_rate': 75,
    'mucous_membranes_are_ok': False,
    'alcohol_concentration_in_ppm': 4.5,
    'health_complaints': (
        'При наступлении полнолуния пациент превращается в оборотня.'
    ),
    'is_passed': False,
}


@pytest.mark.parametrize(
    'headers,params,request_body,expected_status_code,expected_response_body',
    [
        pytest.param(
            {
                'X-Park-Id': NEW_MEDICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': PHYSICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': NEW_MEDICAL_REVIEW_1['checkup_id']},
            {'id': NEW_MEDICAL_REVIEW_1['id'], 'resolution': RESOLUTION},
            200,
            {},
            marks=[
                pytest.mark.now('2020-04-09T08:33:18.926246+00:00'),
                pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql']),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_MEDICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': PHYSICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': NOT_EXISTS_CHECKUP_ID},
            {'id': NEW_MEDICAL_REVIEW_1['id'], 'resolution': RESOLUTION},
            404,
            {'code': 'checkup_not_exists', 'message': 'Checkup not exists'},
            marks=[
                pytest.mark.now('2020-04-09T08:33:18.926246+00:00'),
                pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql']),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_MEDICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': PHYSICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': NEW_MEDICAL_REVIEW_1['checkup_id']},
            {'id': EXIST_MEDICAL_REVIEW_ID, 'resolution': RESOLUTION},
            400,
            {
                'code': 'could_not_post',
                'message': (
                    'id (678e70f6-3fd3-46d0-b953-167ef884c004) '
                    'violates unique constraint'
                ),
            },
            marks=[
                pytest.mark.now('2020-04-09T08:33:18.926246+00:00'),
                pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql']),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_MEDICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': PHYSICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': '4e991007-5c37-4ef8-a9d5-cf5fef3e4950'},
            {'id': NEW_MEDICAL_REVIEW_1['id'], 'resolution': RESOLUTION},
            400,
            {
                'code': 'medical_review_is_passed',
                'message': 'Medical review already is passed',
            },
            marks=[
                pytest.mark.now('2020-04-09T08:51:18.926246+00:00'),
                pytest.mark.pgsql(
                    'edc_app_checkups', files=['checkups_for_limits.sql'],
                ),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_MEDICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': PHYSICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': '4e991007-5c37-4ef8-a9d5-cf5fef3e4951'},
            {'id': NEW_MEDICAL_REVIEW_1['id'], 'resolution': RESOLUTION_2},
            400,
            {
                'code': 'medical_reviews_limit_exceeded',
                'message': 'Medical reviews limit is exceeded',
            },
            marks=[
                pytest.mark.now('2020-04-09T08:51:18.926246+00:00'),
                pytest.mark.pgsql(
                    'edc_app_checkups', files=['checkups_for_limits.sql'],
                ),
            ],
        ),
    ],
)
async def test_medical_reviews_post(
        taxi_edc_app_checkups,
        dispatcher_access_control,
        pgsql,
        headers,
        params,
        request_body,
        expected_status_code,
        expected_response_body,
):
    response = await taxi_edc_app_checkups.post(
        '/fleet/edc-api/v1/medical-reviews',
        headers=headers,
        params=params,
        json=request_body,
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        db_technical_review = _select_medical_review(request_body['id'], pgsql)
        assert NEW_MEDICAL_REVIEW_1 == db_technical_review

        checkup_updated_fields = _select_checkup_updated_fields(
            CHECKUP_ID_2, pgsql,
        )
        assert (
            checkup_updated_fields['medical_review_id'] == request_body['id']
        )
        assert checkup_updated_fields['status'] == 'in_progress'
        assert checkup_updated_fields['passed_at'] is None
    else:
        assert response.json() == expected_response_body


@pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql'])
@pytest.mark.parametrize(
    'params, expected_status_code, expected_respose_body',
    [
        (
            {'id': MEDICAL_REVIEW_WITH_CHECKUP['id']},
            200,
            MEDICAL_REVIEW_WITH_CHECKUP,
        ),
        (
            {'id': MEDICAL_REVIEW_WITH_CHECKUP_EXTERNAL['id']},
            200,
            MEDICAL_REVIEW_WITH_CHECKUP_EXTERNAL,
        ),
        (
            {'id': NOT_EXISTS_MEDICAL_REVIEW_ID},
            404,
            {
                'code': 'medical_review_not_found',
                'message': 'Medical review not found',
            },
        ),
    ],
)
async def test_medical_reviews_get(
        taxi_edc_app_checkups,
        pgsql,
        params,
        expected_status_code,
        expected_respose_body,
):
    response = await taxi_edc_app_checkups.get(
        '/fleet/edc-api/v1/medical-reviews/item', params=params,
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_respose_body


CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTIxMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)
CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_2 = (
    'eyJvZmZzZXQiOjIsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTIxMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_EMPTY_DRIVER_PARK_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjEsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTExMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)
CURSOR_LIMIT_2_EMPTY_DRIVER_PARK_PAGE_2 = (
    'eyJvZmZzZXQiOjIsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjEsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTExMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_WITH_DRIVER_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjEsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTExMSIsInVzZXJfaWQiOiIzMTExMTExMTExMTExMTExMT'
    'ExMTExMTExMTExMTExMSIsInJlc29sdXRpb25faXNfcGFzc2VkIjpudWxsLCJmcm9tIjpudWx'
    'sLCJ1bnRpbCI6bnVsbH0'
)
CURSOR_LIMIT_2_WITH_DRIVER_PAGE_2 = (
    'eyJvZmZzZXQiOjIsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjEsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTExMSIsInVzZXJfaWQiOiIzMTExMTExMTExMTExMTExMT'
    'ExMTExMTExMTExMTExMSIsInJlc29sdXRpb25faXNfcGFzc2VkIjpudWxsLCJmcm9tIjpudWx'
    'sLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_WITH_PHYSICIAN_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTIxMSIsInVzZXJfaWQiOiIyMTExMTExMTExMTExMTExMT'
    'ExMTExMTExMTExMTIxMSIsInJlc29sdXRpb25faXNfcGFzc2VkIjpudWxsLCJmcm9tIjpudWx'
    'sLCJ1bnRpbCI6bnVsbH0'
)
CURSOR_LIMIT_2_WITH_PHYSICIAN_PAGE_2 = (
    'eyJvZmZzZXQiOjIsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTIxMSIsInVzZXJfaWQiOiIyMTExMTExMTExMTExMTExMT'
    'ExMTExMTExMTExMTIxMSIsInJlc29sdXRpb25faXNfcGFzc2VkIjpudWxsLCJmcm9tIjpudWx'
    'sLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_WITH_NOT_EXISTS_DRIVER_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjEsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTIxMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_IS_PASSED_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTIxMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjp0cnVlLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_FROM_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTIxMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjoiMjAyMC0wNC0wOVQwODo1Mzo1Ny4yNzk5MDErMDA6MDA'
    'iLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_UNTIL_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTIxMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6IjIwMjAtMDQtMDlUMDg6NTc6NTc'
    'uMjc5OTAxKzAwOjAwIn0'
)

INVALID_CURSOR = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjozLAZAZAJrX2lkI'
    'jpudWxsLCJkcml2ZXJfaWQiOm51bGx9'
)


@pytest.mark.parametrize(
    'headers, request_body, response_body',
    [
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'limit': 2, 'query': {'user': {'type': 'physician'}}},
            {'cursor': CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'limit': 2, 'query': {'user': {'type': 'driver'}}},
            {'cursor': CURSOR_LIMIT_2_EMPTY_DRIVER_PARK_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {
                'limit': 2,
                'query': {
                    'user': {
                        'type': 'driver',
                        'id': '31111111111111111111111111111111',
                    },
                },
            },
            {'cursor': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {
                'limit': 2,
                'query': {
                    'user': {
                        'type': 'physician',
                        'id': '21111111111111111111111111111211',
                    },
                },
            },
            {'cursor': CURSOR_LIMIT_2_WITH_PHYSICIAN_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {
                'limit': 2,
                'query': {
                    'user': {
                        'type': 'driver',
                        'driver_profile_id': (
                            '31111111111111111111111111111120'
                        ),
                    },
                },
            },
            {'cursor': CURSOR_LIMIT_2_WITH_NOT_EXISTS_DRIVER_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {
                'limit': 2,
                'query': {
                    'user': {'type': 'physician'},
                    'resolution_is_passed': True,
                },
            },
            {'cursor': CURSOR_LIMIT_2_IS_PASSED_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {
                'limit': 2,
                'query': {
                    'user': {'type': 'physician'},
                    'from': '2020-04-09T08:53:57.279901+00:00',
                },
            },
            {'cursor': CURSOR_LIMIT_2_FROM_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {
                'limit': 2,
                'query': {
                    'user': {'type': 'physician'},
                    'until': '2020-04-09T08:57:57.279901+00:00',
                },
            },
            {'cursor': CURSOR_LIMIT_2_UNTIL_PAGE_1},
        ),
    ],
)
async def test_medical_reviews_search_post(
        taxi_edc_app_checkups, headers, request_body, response_body,
):
    response = await taxi_edc_app_checkups.post(
        '/fleet/edc-api/v1/medical-reviews/search',
        headers=headers,
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == response_body


@pytest.mark.pgsql('edc_app_checkups', files=['checkups_for_search.sql'])
@pytest.mark.parametrize(
    'headers,params,expected_status_code,expected_response_body,names_list',
    [
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'cursor': CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_2,
            },
            [('MED_REVIEW_2', 'CHECKUP_2'), ('MED_REVIEW_4', 'CHECKUP_4')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'cursor': CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_2},
            200,
            {
                'cursor_prev': CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_1,
                'cursor': CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_2,
            },
            [('MED_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_EMPTY_DRIVER_PARK_PAGE_1},
            200,
            {
                'cursor_next': CURSOR_LIMIT_2_EMPTY_DRIVER_PARK_PAGE_2,
                'cursor': CURSOR_LIMIT_2_EMPTY_DRIVER_PARK_PAGE_1,
            },
            [('MED_REVIEW_2', 'CHECKUP_2'), ('MED_REVIEW_4', 'CHECKUP_4')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_EMPTY_DRIVER_PARK_PAGE_2},
            200,
            {
                'cursor_prev': CURSOR_LIMIT_2_EMPTY_DRIVER_PARK_PAGE_1,
                'cursor': CURSOR_LIMIT_2_EMPTY_DRIVER_PARK_PAGE_2,
            },
            [('MED_REVIEW_3', 'CHECKUP_3'), ('MED_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_2,
            },
            [('MED_REVIEW_2', 'CHECKUP_2'), ('MED_REVIEW_3', 'CHECKUP_3')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_2},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_2,
                'cursor_prev': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_1,
            },
            [('MED_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'cursor': CURSOR_LIMIT_2_WITH_PHYSICIAN_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_PHYSICIAN_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_WITH_PHYSICIAN_PAGE_2,
            },
            [('MED_REVIEW_2', 'CHECKUP_2'), ('MED_REVIEW_4', 'CHECKUP_4')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'cursor': CURSOR_LIMIT_2_WITH_PHYSICIAN_PAGE_2},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_PHYSICIAN_PAGE_2,
                'cursor_prev': CURSOR_LIMIT_2_WITH_PHYSICIAN_PAGE_1,
            },
            [('MED_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'cursor': CURSOR_LIMIT_2_WITH_NOT_EXISTS_DRIVER_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_WITH_NOT_EXISTS_DRIVER_PAGE_1},
            [],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'cursor': CURSOR_LIMIT_2_IS_PASSED_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_IS_PASSED_PAGE_1},
            [('MED_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'cursor': CURSOR_LIMIT_2_FROM_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_FROM_PAGE_1},
            [('MED_REVIEW_2', 'CHECKUP_2'), ('MED_REVIEW_4', 'CHECKUP_4')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'cursor': CURSOR_LIMIT_2_UNTIL_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_UNTIL_PAGE_1},
            [('MED_REVIEW_4', 'CHECKUP_4'), ('MED_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111211'},
            {'cursor': INVALID_CURSOR},
            400,
            {'code': 'invalid_cursor', 'message': 'Invalid cursor'},
            None,
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111311'},
            {'cursor': CURSOR_LIMIT_2_EMPTY_PHYSICIAN_PARK_PAGE_1},
            400,
            {'code': 'invalid_cursor', 'message': 'Invalid cursor'},
            None,
        ),
    ],
)
async def test_medical_reviews_search_get(
        taxi_edc_app_checkups,
        load_json,
        headers,
        params,
        expected_status_code,
        expected_response_body,
        names_list,
):
    response = await taxi_edc_app_checkups.get(
        '/fleet/edc-api/v1/medical-reviews/search',
        headers=headers,
        params=params,
    )

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        checkups = load_json('checkups_for_search.json')
        expected_response_body['items'] = []
        for names in names_list:
            item = checkups[names[0]]
            item['checkup'] = checkups[names[1]]
            item['checkup'].pop('status_updated_at', None)
            expected_response_body['items'].append(item)
    assert response.json() == expected_response_body
