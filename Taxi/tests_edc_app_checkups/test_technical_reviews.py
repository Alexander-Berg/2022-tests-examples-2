import pytest

CHECKUP_ID_2 = '5e000000-5c37-4ef8-a9d5-cf5fef3e4959'
NOT_EXISTS_CHECKUP_ID = '0e000000-5c37-4ef8-a9d5-cf5fef3e4959'
NOT_EXISTS_TECHNICAL_REVIEW_ID = 'd0ea000b-f122-426d-ac36-91d0c88341be'
EXIST_TECHNICAL_REVIEW_ID = 'd7ea193b-f122-426d-ac36-91d0c88341be'
TECHNICIAN_PASSPORT_UID_1 = '123456788'

TECHNICAL_REVIEW_WITH_CHECKUP = {
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
    'id': 'd7ea193b-f122-426d-ac36-91d0c88341be',
    'park_id': '11111111cccd4f13acabf24d11c3b6c3',
    'passed_at': '2020-04-09T08:35:57.279901+00:00',
    'resolution': {
        'fields': [
            {
                'checked': True,
                'code': 'brakes',
                'comment': 'LOL',
                'name': 'Тормоза',
            },
            {'checked': True, 'code': 'locks', 'name': 'Замки'},
        ],
        'is_passed': True,
        'odometer_value': 1,
    },
    'technician': {
        'diploma': '1111',
        'display_name': 'Механиков Механик Механикович',
        'id': 'fb67a583c14a4db78669f7e0af1fdd26',
    },
}

NEW_TECHNICAL_REVIEW_1 = {
    'id': '01010101-f122-426d-ac36-91d0c88341be',
    'checkup_id': CHECKUP_ID_2,
    'park_id': '11111111cccd4f13acabf24d11c3b6c3',
    'passed_at': '2020-04-09 08:26:18.926246',
    'resolution': {
        'fields': [
            {'checked': True, 'code': 'brakes', 'name': 'Тормоза'},
            {'checked': True, 'code': 'locks', 'name': 'Замки'},
        ],
        'is_passed': True,
        'odometer_value': 9666,
    },
    'resolution_is_passed': True,
    'technician_id': 'fb67a583c14a4db78669f7e0af1fdd26',
    'technician': {
        'diploma': '',
        'display_name': 'Механиков Механик Механикович',
        'id': 'fb67a583c14a4db78669f7e0af1fdd26',
    },
}


TECHNICAL_REVIEW_FIELDS = [
    'id',
    'checkup_id',
    'technician_id',
    'technician',
    'park_id',
    'resolution_is_passed',
    'resolution',
    'passed_at',
]


def _select_technical_review(technical_review_id, pgsql):
    cursor = pgsql['edc_app_checkups'].cursor()
    cursor.execute(
        f"""
        SELECT {", ".join(TECHNICAL_REVIEW_FIELDS)}
        from edc_app_checkups.technical_reviews
        WHERE id='{technical_review_id}';""",
    )
    row = cursor.fetchone()
    technical_review = {}
    if row:
        assert len(row) == len(TECHNICAL_REVIEW_FIELDS)
        for i, field in enumerate(TECHNICAL_REVIEW_FIELDS):
            if row[i]:
                technical_review[field] = row[i]
        technical_review['passed_at'] = str(technical_review['passed_at'])
    return technical_review


def _select_checkup_updated_fields(checkup_id, pgsql):
    cursor = pgsql['edc_app_checkups'].cursor()
    cursor.execute(
        f"""
        SELECT technical_review_id, status, passed_at
        from edc_app_checkups.checkups
        WHERE id='{checkup_id}';""",
    )
    row = cursor.fetchone()
    updated_fields = {}
    if row:
        updated_fields['technical_review_id'] = row[0]
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
                    'id': NEW_TECHNICAL_REVIEW_1['technician']['id'],
                    'park_id': NEW_TECHNICAL_REVIEW_1['park_id'],
                    'display_name': 'Механиков Механик Механикович',
                    'passport_uid': TECHNICIAN_PASSPORT_UID_1,
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
    'fields': [
        {'checked': True, 'code': 'brakes', 'name': 'Тормоза'},
        {'checked': True, 'code': 'locks', 'name': 'Замки'},
    ],
    'is_passed': True,
    'odometer_value': 9666,
}


@pytest.mark.parametrize(
    'headers,params,request_body,expected_status_code,expected_response_body',
    [
        pytest.param(
            {
                'X-Park-Id': NEW_TECHNICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': TECHNICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': NEW_TECHNICAL_REVIEW_1['checkup_id']},
            {'id': NEW_TECHNICAL_REVIEW_1['id'], 'resolution': RESOLUTION},
            200,
            {},
            marks=[
                pytest.mark.now('2020-04-09 08:26:18.926246'),
                pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql']),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_TECHNICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': TECHNICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': NOT_EXISTS_CHECKUP_ID},
            {'id': NEW_TECHNICAL_REVIEW_1['id'], 'resolution': RESOLUTION},
            404,
            {'code': 'checkup_not_exists', 'message': 'Checkup not exists'},
            marks=[
                pytest.mark.now('2020-04-09 08:26:18.926246'),
                pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql']),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_TECHNICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': TECHNICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': NEW_TECHNICAL_REVIEW_1['checkup_id']},
            {'id': EXIST_TECHNICAL_REVIEW_ID, 'resolution': RESOLUTION},
            400,
            {
                'code': 'could_not_post',
                'message': (
                    'id (d7ea193b-f122-426d-ac36-91d0c88341be) '
                    'violates unique constraint'
                ),
            },
            marks=[
                pytest.mark.now('2020-04-09 08:26:18.926246'),
                pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql']),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_TECHNICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': TECHNICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': '4e991007-5c37-4ef8-a9d5-cf5fef3e4950'},
            {'id': NEW_TECHNICAL_REVIEW_1['id'], 'resolution': RESOLUTION},
            400,
            {
                'code': 'technical_reviews_limit_exceeded',
                'message': 'Technical reviews limit is exceeded',
            },
            marks=[
                pytest.mark.now('2020-04-09 08:26:18.926246'),
                pytest.mark.pgsql(
                    'edc_app_checkups', files=['checkups_for_limits.sql'],
                ),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_TECHNICAL_REVIEW_1['park_id'],
                'X-Yandex-Uid': TECHNICIAN_PASSPORT_UID_1,
            },
            {'checkup_id': '4e991007-5c37-4ef8-a9d5-cf5fef3e4951'},
            {'id': NEW_TECHNICAL_REVIEW_1['id'], 'resolution': RESOLUTION},
            400,
            {
                'code': 'technical_review_is_passed',
                'message': 'Technical review already is passed',
            },
            marks=[
                pytest.mark.now('2020-04-09 08:26:18.926246'),
                pytest.mark.pgsql(
                    'edc_app_checkups', files=['checkups_for_limits.sql'],
                ),
            ],
        ),
    ],
)
async def test_technical_reviews_post(
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
        '/fleet/edc-api/v1/technical-reviews',
        headers=headers,
        params=params,
        json=request_body,
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        db_technical_review = _select_technical_review(
            request_body['id'], pgsql,
        )
        assert NEW_TECHNICAL_REVIEW_1 == db_technical_review

        checkup_updated_fields = _select_checkup_updated_fields(
            CHECKUP_ID_2, pgsql,
        )
        assert (
            checkup_updated_fields['technical_review_id'] == request_body['id']
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
            {'id': TECHNICAL_REVIEW_WITH_CHECKUP['id']},
            200,
            TECHNICAL_REVIEW_WITH_CHECKUP,
        ),
        (
            {'id': NOT_EXISTS_TECHNICAL_REVIEW_ID},
            404,
            {
                'code': 'technical_review_not_found',
                'message': 'Technical review not found',
            },
        ),
    ],
)
async def test_technical_reviews_get(
        taxi_edc_app_checkups,
        pgsql,
        params,
        expected_status_code,
        expected_respose_body,
):
    response = await taxi_edc_app_checkups.get(
        '/fleet/edc-api/v1/technical-reviews/item', params=params,
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_respose_body


CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTEyMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)
CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_2 = (
    'eyJvZmZzZXQiOjIsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTEyMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_DRIVER_PARK_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjEsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTExMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)
CURSOR_LIMIT_2_DRIVER_PARK_PAGE_2 = (
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

CURSOR_LIMIT_2_WITH_TECHNICIAN_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTEyMSIsInVzZXJfaWQiOiIyMTExMTExMTExMTExMTExMT'
    'ExMTExMTExMTExMTEyMSIsInJlc29sdXRpb25faXNfcGFzc2VkIjpudWxsLCJmcm9tIjpudWx'
    'sLCJ1bnRpbCI6bnVsbH0'
)
CURSOR_LIMIT_2_WITH_TECHNICIAN_PAGE_2 = (
    'eyJvZmZzZXQiOjIsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTEyMSIsInVzZXJfaWQiOiIyMTExMTExMTExMTExMTExMT'
    'ExMTExMTExMTExMTEyMSIsInJlc29sdXRpb25faXNfcGFzc2VkIjpudWxsLCJmcm9tIjpudWx'
    'sLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_WITH_NOT_EXISTS_DRIVER_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjEsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTExMSIsInVzZXJfaWQiOiIzMTExMTExMTExMTExMTExMT'
    'ExMTExMTExMTExMTEyMCIsInJlc29sdXRpb25faXNfcGFzc2VkIjpudWxsLCJmcm9tIjpudWx'
    'sLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_IS_PASSED_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTEyMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjp0cnVlLCJmcm9tIjpudWxsLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_FROM_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTEyMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjoiMjAyMC0wNC0wOVQwODo0Mzo1Ny4yNzk5MDErMDA6MDA'
    'iLCJ1bnRpbCI6bnVsbH0'
)

CURSOR_LIMIT_2_UNTIL_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ1c2VyX3R5cGUiOjAsInBhcmtfaWQiOiI1MTExMTExM'
    'TExMTExMTExMTExMTExMTExMTExMTEyMSIsInVzZXJfaWQiOm51bGwsInJlc29sdXRpb25faX'
    'NfcGFzc2VkIjpudWxsLCJmcm9tIjpudWxsLCJ1bnRpbCI6IjIwMjAtMDQtMDlUMDg6NDU6NTc'
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
            {'X-Park-Id': '51111111111111111111111111111121'},
            {'limit': 2, 'query': {'user': {'type': 'technician'}}},
            {'cursor': CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'limit': 2, 'query': {'user': {'type': 'driver'}}},
            {'cursor': CURSOR_LIMIT_2_DRIVER_PARK_PAGE_1},
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
            {'X-Park-Id': '51111111111111111111111111111121'},
            {
                'limit': 2,
                'query': {
                    'user': {
                        'type': 'technician',
                        'id': '21111111111111111111111111111121',
                    },
                },
            },
            {'cursor': CURSOR_LIMIT_2_WITH_TECHNICIAN_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {
                'limit': 2,
                'query': {
                    'user': {
                        'type': 'driver',
                        'id': '31111111111111111111111111111120',
                    },
                },
            },
            {'cursor': CURSOR_LIMIT_2_WITH_NOT_EXISTS_DRIVER_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {
                'limit': 2,
                'query': {
                    'user': {'type': 'technician'},
                    'resolution_is_passed': True,
                },
            },
            {'cursor': CURSOR_LIMIT_2_IS_PASSED_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {
                'limit': 2,
                'query': {
                    'user': {'type': 'technician'},
                    'from': '2020-04-09T08:43:57.279901+00:00',
                },
            },
            {'cursor': CURSOR_LIMIT_2_FROM_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {
                'limit': 2,
                'query': {
                    'user': {'type': 'technician'},
                    'until': '2020-04-09T08:45:57.279901+00:00',
                },
            },
            {'cursor': CURSOR_LIMIT_2_UNTIL_PAGE_1},
        ),
    ],
)
async def test_technical_reviews_search_post(
        taxi_edc_app_checkups, headers, request_body, response_body,
):
    response = await taxi_edc_app_checkups.post(
        '/fleet/edc-api/v1/technical-reviews/search',
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
            {'X-Park-Id': '51111111111111111111111111111121'},
            {'cursor': CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_2,
            },
            [('TECH_REVIEW_2', 'CHECKUP_2'), ('TECH_REVIEW_5', 'CHECKUP_5')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {'cursor': CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_2},
            200,
            {
                'cursor': CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_2,
                'cursor_prev': CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_1,
            },
            [('TECH_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_DRIVER_PARK_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_DRIVER_PARK_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_DRIVER_PARK_PAGE_2,
            },
            [('TECH_REVIEW_3', 'CHECKUP_3'), ('TECH_REVIEW_2', 'CHECKUP_2')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_DRIVER_PARK_PAGE_2},
            200,
            {
                'cursor': CURSOR_LIMIT_2_DRIVER_PARK_PAGE_2,
                'cursor_prev': CURSOR_LIMIT_2_DRIVER_PARK_PAGE_1,
            },
            [('TECH_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_2,
            },
            [('TECH_REVIEW_3', 'CHECKUP_3'), ('TECH_REVIEW_2', 'CHECKUP_2')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_2},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_2,
                'cursor_prev': CURSOR_LIMIT_2_WITH_DRIVER_PAGE_1,
            },
            [('TECH_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {'cursor': CURSOR_LIMIT_2_WITH_TECHNICIAN_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_TECHNICIAN_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_WITH_TECHNICIAN_PAGE_2,
            },
            [('TECH_REVIEW_2', 'CHECKUP_2'), ('TECH_REVIEW_5', 'CHECKUP_5')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {'cursor': CURSOR_LIMIT_2_WITH_TECHNICIAN_PAGE_2},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_TECHNICIAN_PAGE_2,
                'cursor_prev': CURSOR_LIMIT_2_WITH_TECHNICIAN_PAGE_1,
            },
            [('TECH_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_NOT_EXISTS_DRIVER_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_WITH_NOT_EXISTS_DRIVER_PAGE_1},
            [],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {'cursor': CURSOR_LIMIT_2_IS_PASSED_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_IS_PASSED_PAGE_1},
            [('TECH_REVIEW_2', 'CHECKUP_2'), ('TECH_REVIEW_5', 'CHECKUP_5')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {'cursor': CURSOR_LIMIT_2_FROM_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_FROM_PAGE_1},
            [('TECH_REVIEW_2', 'CHECKUP_2'), ('TECH_REVIEW_5', 'CHECKUP_5')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {'cursor': CURSOR_LIMIT_2_UNTIL_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_UNTIL_PAGE_1},
            [('TECH_REVIEW_5', 'CHECKUP_5'), ('TECH_REVIEW_1', 'CHECKUP_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111121'},
            {'cursor': INVALID_CURSOR},
            400,
            {'code': 'invalid_cursor', 'message': 'Invalid cursor'},
            None,
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111131'},
            {'cursor': CURSOR_LIMIT_2_TECHNICIAN_PARK_PAGE_1},
            400,
            {'code': 'invalid_cursor', 'message': 'Invalid cursor'},
            None,
        ),
    ],
)
async def test_technical_reviews_search_get(
        taxi_edc_app_checkups,
        load_json,
        headers,
        params,
        expected_status_code,
        expected_response_body,
        names_list,
):
    response = await taxi_edc_app_checkups.get(
        '/fleet/edc-api/v1/technical-reviews/search',
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
