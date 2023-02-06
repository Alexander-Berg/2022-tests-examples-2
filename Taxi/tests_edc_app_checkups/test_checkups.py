import pytest

CHECKUP_WITH_REVIEWS_1 = {
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
    'status_updated_at': '1970-01-01T00:00:00+00:00',
    'technical_review': {
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
    },
    'vehicle': {
        'id': '7a9b5d6f-c0e5-4304-8487-d3981c5852ef',
        'license_plate': 'А001АА',
        'model': 'Logan',
        'type': 'car',
        'year': '2005',
    },
    'medical_review': {
        'id': '678e70f6-3fd3-46d0-b953-167ef884c004',
        'park_id': '22222222cccd4f13acabf24d11c3b6c3',
        'passed_at': '2020-04-09T08:49:33.378941+00:00',
        'resolution_is_passed': True,
        'resolution': {
            'temperature': {'value': 36.6},
            'blood_pressure': {'systolic': 120, 'diastolic': 80},
            'heart_rate': 75,
            'mucous_membranes_are_ok': True,
            'is_passed': True,
        },
        'physician': {
            'job_position': 'фельдшер',
            'display_name': 'Врачев Врач Врачевич',
            'id': '3b35047d1d4d4abc903544ffbba00d46',
        },
    },
}


NEW_CHECKUP_1 = {
    'id': 'e1db0e79-a393-458c-82ae-cc59cc2ea7c2',
    'creator_user_id': 'b601049dba914dd6a1297f81bc0b9a5d',
    'creator': {
        'id': 'b601049dba914dd6a1297f81bc0b9a5d',
        'display_name': 'Петров Семен Семенович',
    },
    'driver_id': '5328f5a3cdc2435d9c07672e7dd29fb3',
    'driver': {
        'birth_date': '1990-01-07T06:56:07.000',
        'first_name': 'Семен',
        'id': '5328f5a3cdc2435d9c07672e7dd29fb3',
        'last_name': 'Петров',
        'license': '1234567890',
        'middle_name': 'Семенович',
        'sex': 'male',
    },
    'park_id': '2d3d692acccd4f13acabf24d11c3b6c3',
    'park': {
        'address': 'ул. Арбат, 15',
        'city_id': 'Ярославль',
        'id': '2d3d692acccd4f13acabf24d11c3b6c3',
        'name': 'Acme Ltd',
        'primary_state_registration_number': '',
        'phone': '+74852200000',
    },
    'vehicle_id': '7a9b5d6fc0e543048487d3981c5852ef',
    'vehicle': {
        'id': '7a9b5d6fc0e543048487d3981c5852ef',
        'license_plate': 'А001АА',
        'model': 'Camry',
        'type': '',
        'year': '2019',
    },
    'technical_review_id': None,
    'medical_review_id': None,
    'status': 'in_progress',
    'created_at': '2020-04-10 00:00:00',
    'passed_at': None,
}

NEW_CHECKUP_2 = NEW_CHECKUP_1.copy()
NEW_CHECKUP_2['created_at'] = '2020-04-09 21:00:01'

NEW_CHECKUP_ID_1 = 'e1db0e79-a393-458c-82ae-cc59cc2ea7c2'
NEW_CREATOR_ID_1 = 'b601049dba914dd6a1297f81bc0b9a5d'
NEW_CREATOR_PASSPORT_UID_1 = '123456789'
NEW_DRIVER_PROFILE_ID_1 = '5328f5a3cdc2435d9c07672e7dd29fb3'
NEW_DRIVER_LICENSE_PD_ID_1 = '1b33c20f17a44e1aa814d6df98df39c2'
NEW_PARK_ID_1 = '2d3d692acccd4f13acabf24d11c3b6c3'
NEW_VEHICLE_ID_1 = '7a9b5d6fc0e543048487d3981c5852ef'

NUMBER_1 = '00000000000005721518'
NOT_EXISTING_NUMBER = '00000000000005721517'

NOT_EXISTING_ID = '4e991007-5c37-4ef8-a9d5-cf5fef3e4957'

CHECKUP_FIELDS = [
    'id',
    'number',
    'creator_user_id',
    'creator',
    'driver_id',
    'driver',
    'vehicle_id',
    'vehicle',
    'park_id',
    'park',
    'medical_review_id',
    'technical_review_id',
    'created_at',
    'passed_at',
    'status',
]


def _select_checkup(checkup_id, pgsql):
    cursor = pgsql['edc_app_checkups'].cursor()
    cursor.execute(
        f"""
        SELECT {", ".join(CHECKUP_FIELDS)}
        from edc_app_checkups.checkups
        WHERE id='{checkup_id}';""",
    )
    row = cursor.fetchone()
    checkup = {}
    if row:
        assert len(row) == len(CHECKUP_FIELDS)
        for i, field in enumerate(CHECKUP_FIELDS):
            checkup[field] = row[i]
    if checkup['created_at']:
        checkup['created_at'] = str(checkup['created_at'])
    if checkup['passed_at']:
        checkup['passed_at'] = str(checkup['passed_at'])
    return checkup


@pytest.fixture(name='driver_profiles')
def _driver_profiles(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': (
                        f'{NEW_PARK_ID_1}_{NEW_DRIVER_PROFILE_ID_1}'
                    ),
                    'data': {
                        'full_name': {
                            'last_name': 'Петров',
                            'first_name': 'Семен',
                            'middle_name': 'Семенович',
                        },
                        'license_driver_birth_date': '1990-01-07T06:56:07.000',
                        'license': {'pd_id': NEW_DRIVER_LICENSE_PD_ID_1},
                    },
                },
            ],
        }


@pytest.fixture(name='fleet_vehicles')
def _fleet_vehicles(mockserver):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicle(request):
        return {
            'vehicles': [
                {
                    'data': {
                        'model': 'Camry',
                        'number': 'А001АА',
                        'year': '2019',
                    },
                    'park_id_car_id': f'{NEW_PARK_ID_1}_{NEW_VEHICLE_ID_1}',
                },
            ],
        }


@pytest.fixture(name='fleet_parks')
def _fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    'id': NEW_PARK_ID_1,
                    'login': 'U15293523',
                    'name': 'Acme Ltd',
                    'is_active': True,
                    'city_id': 'Ярославль',
                    'tz_offset': 3,
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'country_id': 'rus',
                    'driver_hiring': {
                        'park_phone': '+74852200000',
                        'park_address': 'ул. Арбат, 15',
                    },
                    'demo_mode': False,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }


@pytest.fixture(name='dispatcher_access_control')
def _dispatcher_access_control(mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock_dispatcher_access_control(request):
        return {
            'users': [
                {
                    'id': 'b601049dba914dd6a1297f81bc0b9a5d',
                    'park_id': '2d3d692acccd4f13acabf24d11c3b6c3',
                    'display_name': 'Петров Семен Семенович',
                    'passport_uid': '123456789',
                    'is_enabled': True,
                    'is_confirmed': True,
                    'is_superuser': True,
                    'is_usage_consent_accepted': True,
                },
            ],
            'limit': 1,
            'offset': 0,
        }


@pytest.fixture(name='personal')
def _personal(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _mock_driver_profiles(request):
        return {'id': NEW_DRIVER_LICENSE_PD_ID_1, 'value': '1234567890'}


@pytest.mark.parametrize(
    'headers,request_body,expected_status_code,expected_response_body,checkup',
    [
        pytest.param(
            {
                'X-Park-Id': NEW_PARK_ID_1,
                'X-Yandex-Uid': NEW_CREATOR_PASSPORT_UID_1,
            },
            {
                'id': NEW_CHECKUP_ID_1,
                'driver_profile_id': NEW_DRIVER_PROFILE_ID_1,
                'vehicle_id': NEW_VEHICLE_ID_1,
            },
            200,
            {},
            NEW_CHECKUP_1,
            marks=[
                pytest.mark.now('2020-04-10T00:00:00+00:00'),
                pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql']),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_PARK_ID_1,
                'X-Yandex-Uid': NEW_CREATOR_PASSPORT_UID_1,
            },
            {
                'id': NEW_CHECKUP_ID_1,
                'driver_profile_id': NEW_DRIVER_PROFILE_ID_1,
                'vehicle_id': NEW_VEHICLE_ID_1,
            },
            400,
            {
                'code': 'checkups_limit_exceeded',
                'message': 'Checkups limit exceeded',
            },
            {},
            marks=[
                pytest.mark.now('2020-04-09T15:00:00+00:00'),
                pytest.mark.pgsql(
                    'edc_app_checkups', files=['checkups_for_limits.sql'],
                ),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_PARK_ID_1,
                'X-Yandex-Uid': NEW_CREATOR_PASSPORT_UID_1,
            },
            {
                'id': NEW_CHECKUP_ID_1,
                'driver_profile_id': NEW_DRIVER_PROFILE_ID_1,
                'vehicle_id': NEW_VEHICLE_ID_1,
            },
            400,
            {
                'code': 'checkups_limit_exceeded',
                'message': 'Checkups limit exceeded',
            },
            {},
            marks=[
                pytest.mark.now('2020-04-09T20:59:59+00:00'),
                pytest.mark.pgsql(
                    'edc_app_checkups', files=['checkups_for_limits.sql'],
                ),
            ],
        ),
        pytest.param(
            {
                'X-Park-Id': NEW_PARK_ID_1,
                'X-Yandex-Uid': NEW_CREATOR_PASSPORT_UID_1,
            },
            {
                'id': NEW_CHECKUP_ID_1,
                'driver_profile_id': NEW_DRIVER_PROFILE_ID_1,
                'vehicle_id': NEW_VEHICLE_ID_1,
            },
            200,
            {},
            NEW_CHECKUP_2,
            marks=[
                pytest.mark.now('2020-04-09T21:00:01+00:00'),
                pytest.mark.pgsql(
                    'edc_app_checkups', files=['checkups_for_limits.sql'],
                ),
            ],
        ),
    ],
)
async def test_checkups_post(
        taxi_edc_app_checkups,
        driver_profiles,
        fleet_parks,
        fleet_vehicles,
        dispatcher_access_control,
        personal,
        pgsql,
        headers,
        request_body,
        expected_status_code,
        expected_response_body,
        checkup,
):
    response = await taxi_edc_app_checkups.post(
        '/fleet/edc-api/v1/checkups', headers=headers, json=request_body,
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        db_checkup = _select_checkup(request_body['id'], pgsql)
        assert response.json().get('number')
        checkup['number'] = response.json().get('number')
        db_checkup['park'].pop('tz_offset', None)
        assert db_checkup == checkup
    else:
        assert response.json() == expected_response_body


@pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql'])
@pytest.mark.parametrize(
    'headers, params, expected_status_code, expected_respose_body',
    [
        (
            {'X-Park-Id': '2d3d692a-cccd-4f13-acab-f24d11c3b6c3'},
            {'id': CHECKUP_WITH_REVIEWS_1['id']},
            200,
            CHECKUP_WITH_REVIEWS_1,
        ),
        (
            {'X-Park-Id': '2d3d692a-cccd-4f13-acab-f24d11c3b6c1'},
            {'id': CHECKUP_WITH_REVIEWS_1['id']},
            404,
            {'code': 'checkup_not_found', 'message': 'Checkup not found'},
        ),
        (
            {'X-Park-Id': '2d3d692a-cccd-4f13-acab-f24d11c3b6c3'},
            {'id': NOT_EXISTING_ID},
            404,
            {'code': 'checkup_not_found', 'message': 'Checkup not found'},
        ),
    ],
)
async def test_checkups_get(
        taxi_edc_app_checkups,
        pgsql,
        headers,
        params,
        expected_status_code,
        expected_respose_body,
):
    response = await taxi_edc_app_checkups.get(
        '/fleet/edc-api/v1/checkups/item', headers=headers, params=params,
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_respose_body


@pytest.mark.parametrize(
    'params, expected_status_code, expected_respose_body',
    [
        pytest.param(
            {'number': NUMBER_1},
            200,
            CHECKUP_WITH_REVIEWS_1,
            marks=[
                pytest.mark.now('2020-04-09T10:00:00+00:00'),
                pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql']),
            ],
        ),
        pytest.param(
            {'number': '00000000000005721518'},
            400,
            {
                'code': 'medical_reviews_limit_exceeded',
                'message': 'Medical reviews limit is exceeded',
            },
            marks=[
                pytest.mark.now('2020-04-09T10:00:00+00:00'),
                pytest.mark.pgsql(
                    'edc_app_checkups', files=['checkups_for_limits.sql'],
                ),
            ],
        ),
        pytest.param(
            {'number': NOT_EXISTING_NUMBER},
            404,
            {'code': 'checkup_not_found', 'message': 'Checkup not found'},
            marks=[
                pytest.mark.now('2020-04-09T10:00:00+00:00'),
                pytest.mark.pgsql('edc_app_checkups', files=['checkups.sql']),
            ],
        ),
    ],
)
async def test_checkups_get_by_number(
        taxi_edc_app_checkups,
        pgsql,
        params,
        expected_status_code,
        expected_respose_body,
):
    response = await taxi_edc_app_checkups.get(
        '/fleet/edc-api/v1/checkups/by-number', params=params,
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_respose_body


CURSOR_LIMIT_2_WITH_PARK_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJwYXJ'
    'rX2lkIjoiNTExMTExMTExMTExMTExMTExMTExMTEx'
    'MTExMTExMTEiLCJkcml2ZXJfaWQiOm51bGx9'
)
CURSOR_LIMIT_2_WITH_PARK_PAGE_2 = (
    'eyJvZmZzZXQiOjIsImxpbWl0IjoyLCJwYXJrX2lkI'
    'joiNTExMTExMTExMTExMTExMTExMTExMTExMTE'
    'xMTExMTEiLCJkcml2ZXJfaWQiOm51bGx9'
)
CURSOR_LIMIT_2_WITH_PARK_DRIVER_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJ'
    'wYXJrX2lkIjoiNTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTE'
    'iLCJkcml2ZXJfaWQiOiIzMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMSJ9'
)
CURSOR_LIMIT_2_WITH_PARK_DRIVER_PAGE_2 = (
    'eyJvZmZzZXQiOjIsImxpbWl0IjoyLCJwYXJ'
    'rX2lkIjoiNTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTEiLCJk'
    'cml2ZXJfaWQiOiIzMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMSJ9'
)
CURSOR_LIMIT_2_WITH_NOT_EXISTS_PARK_DRIVER_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0I'
    'joyLCJwYXJrX2lkIjoiNTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTE'
    'iLCJkcml2ZXJfaWQiOiIzMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMyJ9'
)
INVALID_CURSOR = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjozLAZAZAJrX2lkI'
    'jpudWxsLCJkcml2ZXJfaWQiOm51bGx9'
)


@pytest.mark.parametrize(
    'headers, request_body, response_body',
    [
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'limit': 2, 'query': {}},
            {'cursor': CURSOR_LIMIT_2_WITH_PARK_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {
                'limit': 2,
                'query': {
                    'driver_profile_id': '31111111111111111111111111111111',
                },
            },
            {'cursor': CURSOR_LIMIT_2_WITH_PARK_DRIVER_PAGE_1},
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {
                'limit': 2,
                'query': {
                    'driver_profile_id': '31111111111111111111111111111113',
                },
            },
            {'cursor': CURSOR_LIMIT_2_WITH_NOT_EXISTS_PARK_DRIVER_PAGE_1},
        ),
    ],
)
async def test_checkups_search_post(
        taxi_edc_app_checkups, headers, request_body, response_body,
):
    response = await taxi_edc_app_checkups.post(
        '/fleet/edc-api/v1/checkups/search',
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
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_PARK_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_PARK_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_WITH_PARK_PAGE_2,
            },
            [
                ('CHECKUP_3', 'TECH_REVIEW_3', 'MED_REVIEW_3'),
                ('CHECKUP_2', 'TECH_REVIEW_2', 'MED_REVIEW_2'),
            ],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_PARK_PAGE_2},
            200,
            {
                'cursor_prev': CURSOR_LIMIT_2_WITH_PARK_PAGE_1,
                'cursor': CURSOR_LIMIT_2_WITH_PARK_PAGE_2,
            },
            [
                ('CHECKUP_4', None, 'MED_REVIEW_4'),
                ('CHECKUP_1', 'TECH_REVIEW_1', 'MED_REVIEW_1'),
            ],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_PARK_DRIVER_PAGE_1},
            200,
            {
                'cursor_next': CURSOR_LIMIT_2_WITH_PARK_DRIVER_PAGE_2,
                'cursor': CURSOR_LIMIT_2_WITH_PARK_DRIVER_PAGE_1,
            },
            [
                ('CHECKUP_3', 'TECH_REVIEW_3', 'MED_REVIEW_3'),
                ('CHECKUP_2', 'TECH_REVIEW_2', 'MED_REVIEW_2'),
            ],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_PARK_DRIVER_PAGE_2},
            200,
            {
                'cursor': CURSOR_LIMIT_2_WITH_PARK_DRIVER_PAGE_2,
                'cursor_prev': CURSOR_LIMIT_2_WITH_PARK_DRIVER_PAGE_1,
            },
            [('CHECKUP_1', 'TECH_REVIEW_1', 'MED_REVIEW_1')],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': CURSOR_LIMIT_2_WITH_NOT_EXISTS_PARK_DRIVER_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_WITH_NOT_EXISTS_PARK_DRIVER_PAGE_1},
            [],
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111111'},
            {'cursor': INVALID_CURSOR},
            400,
            {'code': 'invalid_cursor', 'message': 'Invalid cursor'},
            None,
        ),
        (
            {'X-Park-Id': '51111111111111111111111111111112'},
            {'cursor': CURSOR_LIMIT_2_WITH_PARK_PAGE_1},
            400,
            {'code': 'invalid_cursor', 'message': 'Invalid cursor'},
            None,
        ),
    ],
)
async def test_checkups_search_get(
        taxi_edc_app_checkups,
        load_json,
        headers,
        params,
        expected_status_code,
        expected_response_body,
        names_list,
):
    response = await taxi_edc_app_checkups.get(
        '/fleet/edc-api/v1/checkups/search', headers=headers, params=params,
    )

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        checkups = load_json('checkups_for_search.json')
        expected_response_body['items'] = []
        for names in names_list:
            item = checkups[names[0]]
            if names[1]:
                item['technical_review'] = checkups[names[1]]
            if names[2]:
                item['medical_review'] = checkups[names[2]]
            expected_response_body['items'].append(item)
    assert response.json() == expected_response_body
