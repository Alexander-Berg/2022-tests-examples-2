# pylint: disable=R1705
import datetime
import json

import pytest
import pytz

ENDPOINT = '/v1/contractor/driver-profile'

REQUIRED_FIELDS = [
    'balance_limit',
    'first_name',
    'last_name',
    'license',
    'license_number',
    'license_normalized',
    'license_country',
    'license_expire_date',
    'license_issue_date',
    'license_driver_birth_date',
    'driver_license_pd_id',
    'phone_pd_ids',
    'rule_id',
    'hire_date',
    'balance_deny_onlycard',
    'work_status',
    'providers',
]

NOT_REQUIRED_FIELDS = [
    'address',
    'middle_name',
    'car_id',
    'fire_date',
    'password',
    'email_pd_id',
    'comment',
    'license_experience',
    'check_message',
]

PERSONAL_FIELDS = ['email']

ALL_FIELDS = REQUIRED_FIELDS + NOT_REQUIRED_FIELDS + PERSONAL_FIELDS

DATE_FIELDS = {
    'license_expire_date',
    'license_issue_date',
    'license_driver_birth_date',
    'hire_date',
    'fire_date',
}

FLEET_API_DISPLAY_NAME_PREFIX = 'API7 Key '
FLEET_API_KEY_ID = '17'
X_REAL_IP = '8.7.6.5'

ARRAY_FIELDS = {'phone_pd_ids', 'providers'}

NUMBER_FIELDS = {'balance_limit'}

DEFAULT_SOURCE_SERVICE = 'contractor-profiles-manager'

DEFAULT_REQUEST = {
    'balance_limit': 500.007,
    'first_name': 'qwerwwer',
    'last_name': '324234',
    'license': '4234234',
    'license_number': '4234234',
    'license_normalized': '4234234',
    'license_country': 'rus',
    'license_expire_date': '2020-05-18T00:00:00+03:00',
    'license_issue_date': '2020-05-18T00:00:00+00:00',
    'license_driver_birth_date': '2020-05-18T00:00:00+00:00',
    'phone_pd_ids': ['324234'],
    'rule_id': 'rule_zero',
    'hire_date': '2020-05-18T00:00:00+00:00',
    'balance_deny_onlycard': False,
    'driver_license_pd_id': '1234124124',
    'providers': ['yandex'],
    'work_status': 'working',
}

DEFAULT_EXPECTED_STATE = {
    'first_name': 'Андрей',
    'last_name': 'Мироненко',
    'middle_name': 'Алексеевич',
    'license_country': 'rus',
    'license_expire_date': '2028-11-20T11:11:11+00:00',
    'license_issue_date': '2018-11-20T11:11:11+00:00',
    'license_driver_birth_date': '1939-09-01T00:00:00+00:00',
    'driver_license_pd_id': '123412345DUPID',
}

ADDITIONAL_PARAMS = {'enable_balance_limit_updated_trigger': True}

AUTHOR = {
    'consumer': DEFAULT_SOURCE_SERVICE,
    'identity': {
        'type': 'fleet_api',
        'key_id': FLEET_API_KEY_ID,
        'user_ip': X_REAL_IP,
    },
}

EMAIL_PD_ID = 'qwerqwqw3e34r'
EMAIL = 'test@test.test'

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'

# tvmknife unittest service -s 2031328 -d 111
VALID_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYI4P17EG8:RoWtAz0aK3pOK9e_0gblnXqDm3V1XzrpdEh9'
    'jU2Yl5jsDeVmodf12BBvL6GYIhFA7a8443hSvU8eG_Q0695LqcI7mkDfght0ld48L4qLbPw'
    '1UkVtugoyZch7FwgQWGO0Kmdd37rCOhKKUSHdbAxNiG8z-s5QhrHjwXnduz_oUXg'
)

# tvmknife unittest service -s 12345 -d 111
INVALID_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIuWAQbw:CMKOnwEtJBDXUiR2FO1EynpoKeUIc5qShzX8Os'
    'AHQTRKZLnGLVhU8TP3N6nXLL9DJFWWoHqZzlr8sHni4RCD7N10LGhZ9U2OLg9qvFbTik43Hc'
    'Y4-9nv1FQY1qO4rASQL0mNvPnbMtnPQdPMeNvbXIszctS23kCLKwGUKfSGVZQ'
)


ALLOWED_CONSUMERS_CONFIG = {
    'allowed_consumers': ['contractor-profiles-manager'],
}


@pytest.fixture(name='get_driver')
def _get_driver(mongodb):
    return lambda park_id, contractor_profile_id: mongodb.dbdrivers.find_one(
        dict(park_id=park_id, driver_id=contractor_profile_id),
    )


def make_request(expected_state, driver_profile=None, author=None):
    return {
        'author': AUTHOR if author is None else author,
        'update_query': {
            **DEFAULT_REQUEST,
            **(driver_profile if driver_profile else {}),
        },
        'expected_state': expected_state,
        'additional_params': ADDITIONAL_PARAMS,
    }


def make_update_trigger_request(park_id, driver_id, old_car_id, new_car_id):
    driver = {'park_id': park_id, 'driver_id': driver_id}

    old_driver = driver.copy()
    new_driver = driver.copy()
    if old_car_id is not None:
        old_driver['car_id'] = old_car_id
    if new_car_id is not None:
        new_driver['car_id'] = new_car_id
    return {'old_driver': old_driver, 'new_driver': new_driver}


def str_to_datetime(string_date):
    return (
        datetime.datetime.strptime(string_date, '%Y-%m-%dT%H:%M:%S%z')
        .astimezone(pytz.utc)
        .replace(tzinfo=None)
    )


def obj_to_str(obj):
    return json.dumps(obj, separators=(',', ':'))


def prepare_request_to_compare(request_values):
    result = {}
    for field, value in request_values.items():
        if field in DATE_FIELDS:
            result[field] = str_to_datetime(value)
        elif field == 'license_experience':
            result[field] = {'total': str_to_datetime(value['total'])}
        elif field in NUMBER_FIELDS:
            result[field] = float(value)
        else:
            result[field] = value
    return result


def get_set_data(mongo_doc, request_values):
    return {
        field: value
        for field, value in mongo_doc.items()
        if field in request_values
    }


def get_unset_data(mongo_doc, request_values):
    return {
        field: value
        for field, value in mongo_doc.items()
        if field in set(NOT_REQUIRED_FIELDS) - set(request_values.keys())
    }


def value_to_str(field, value, is_mongo_obj=True):
    if value is None:
        return ''
    if field == 'license_experience':
        date = value.get('total')
        if not date:
            return ''
        if not is_mongo_obj:
            date = str_to_datetime(date)
        return obj_to_str({'total': date.strftime(DATETIME_FORMAT)})
    elif field in ARRAY_FIELDS:
        return obj_to_str(value)
    elif field in DATE_FIELDS:
        if is_mongo_obj:
            return value.strftime(DATETIME_FORMAT)
        date = str_to_datetime(value)
        return date.strftime(DATETIME_FORMAT)
    elif field in NUMBER_FIELDS:
        return str(value)
    else:
        return value


def add_personal_data(values):
    result_profile = values.copy()
    if 'email_pd_id' in result_profile:
        result_profile['email'] = EMAIL
    return result_profile


def get_changes(doc, values):
    result = []

    profile = add_personal_data(values)
    for field in ALL_FIELDS:
        old_val = value_to_str(field, doc.get(field))
        new_val = value_to_str(field, profile.get(field), False)
        if new_val == old_val:
            continue
        result.append({'field': field, 'old': old_val, 'new': new_val})
    return result


@pytest.mark.config(DRIVER_PROFILES_ALLOWED_CONSUMERS=ALLOWED_CONSUMERS_CONFIG)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    ('park_id', 'contractor_profile_id', 'driver_request', 'expected_state'),
    [
        ('dbid_0', 'uuid_0', {}, DEFAULT_EXPECTED_STATE),
        (
            'dbid_1',
            'uuid_1',
            {
                'balance_limit': 500,
                'address': 'test',
                'middle_name': 'test_middle',
                'car_id': '123456',
                'fire_date': '2021-05-18T00:00:00+03:00',
                'password': '0',
                'email_pd_id': 'qwerqwqw3e34r',
                'comment': 'good',
                'license_experience': {'total': '2021-05-18T00:00:00+03:00'},
            },
            {
                'first_name': 'Андрей',
                'last_name': 'Мироненко',
                'driver_license_pd_id': '123DUPID',
                'license_expire_date': '2028-11-20T11:11:11.000+00:00',
                'license_issue_date': '2018-11-20T11:11:11.000+00:00',
                'license_driver_birth_date': '1939-09-01T00:00:00.000+00:00',
                'license_experience': {
                    'total': '2020-01-01T00:00:00.000+00:00',
                },
            },
        ),
    ],
)
async def test_success_update(
        taxi_driver_profiles,
        get_driver,
        mockserver,
        park_id,
        contractor_profile_id,
        driver_request,
        expected_state,
        mock_contractor_balances,
):
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _personal_retrieve(request):
        request.get_data()
        return {'id': EMAIL_PD_ID, 'value': EMAIL}

    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        assert body == {
            'park_id': park_id,
            'change_info': {
                'object_id': contractor_profile_id,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': get_changes(driver_before, driver_profile),
            },
            'author': {
                'dispatch_user_id': FLEET_API_KEY_ID,
                'display_name': (
                    f'{FLEET_API_DISPLAY_NAME_PREFIX}{FLEET_API_KEY_ID}'
                ),
                'user_ip': X_REAL_IP,
            },
        }
        return {}

    @mockserver.json_handler(
        '/taximeter-xservice/utils/driver-updated-trigger',
    )
    def _mock_changef_logger(request):
        assert request.json == make_update_trigger_request(
            park_id,
            contractor_profile_id,
            driver_before.get('car_id'),
            driver_request.get('car_id'),
        )
        return {}

    driver_before = get_driver(park_id, contractor_profile_id)
    mock_contractor_balances.save_old_balance_limit(
        park_id, contractor_profile_id,
    )

    request_body = make_request(expected_state, driver_request)
    driver_profile = request_body['update_query']
    for _ in range(3):  # idempotency test
        response = await taxi_driver_profiles.put(
            ENDPOINT,
            headers={
                'X-Real-IP': X_REAL_IP,
                'X-Fleet-API-Key-ID': FLEET_API_KEY_ID,
                'X-Ya-Service-Ticket': VALID_SERVICE_TICKET,
            },
            params=dict(
                park_id=park_id, contractor_profile_id=contractor_profile_id,
            ),
            json=request_body,
        )
        assert response.status_code == 200

    mock_contractor_balances.check(park_id, contractor_profile_id)
    driver_after = get_driver(park_id, contractor_profile_id)
    assert not get_unset_data(driver_after, driver_profile)
    assert get_set_data(
        driver_after, driver_profile,
    ) == prepare_request_to_compare(driver_profile)
    assert driver_after['updated_ts'] != driver_before['updated_ts']
    assert driver_after['modified_date'] != driver_before['modified_date']


@pytest.mark.config(DRIVER_PROFILES_ALLOWED_CONSUMERS=ALLOWED_CONSUMERS_CONFIG)
@pytest.mark.config(TVM_ENABLED=True)
async def test_change_author(
        taxi_driver_profiles, get_driver, mockserver, mock_contractor_balances,
):
    park_id = 'dbid_0'
    contractor_profile_id = 'uuid_0'

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _personal_retrieve(request):
        request.get_data()
        return {'id': EMAIL_PD_ID, 'value': EMAIL}

    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        assert body == {
            'park_id': park_id,
            'change_info': {
                'object_id': contractor_profile_id,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': get_changes(driver_before, driver_profile),
            },
            'author': {
                'dispatch_user_id': '678',
                'display_name': 'Ruslan',
                'user_ip': '',
            },
        }
        return {}

    @mockserver.json_handler(
        '/taximeter-xservice/utils/driver-updated-trigger',
    )
    def _mock_changef_logger(request):
        assert request.json == make_update_trigger_request(
            park_id, contractor_profile_id, driver_before.get('car_id'), None,
        )
        return {}

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock_get_users_list(request):
        assert request.json == {
            'offset': 0,
            'query': {
                'park': {'id': park_id},
                'user': {'passport_uid': ['12345']},
            },
        }
        return {
            'offset': 0,
            'users': [
                {
                    'id': '678',
                    'park_id': park_id,
                    'display_name': 'Ruslan',
                    'is_enabled': True,
                    'is_confirmed': True,
                    'is_superuser': False,
                    'is_multifactor_authentication_required': False,
                    'is_usage_consent_accepted': True,
                },
            ],
        }

    driver_before = get_driver(park_id, contractor_profile_id)
    mock_contractor_balances.save_old_balance_limit(
        park_id, contractor_profile_id,
    )

    request_body = make_request(
        DEFAULT_EXPECTED_STATE,
        author={
            'consumer': DEFAULT_SOURCE_SERVICE,
            'identity': {
                'type': 'user',
                'passport_id': '12345',
                'ticket_provider': 'yandex',
            },
        },
    )
    driver_profile = request_body['update_query']

    response = await taxi_driver_profiles.put(
        ENDPOINT,
        headers={
            'X-Real-IP': X_REAL_IP,
            'X-Fleet-API-Key-ID': FLEET_API_KEY_ID,
            'X-Ya-Service-Ticket': VALID_SERVICE_TICKET,
        },
        params=dict(
            park_id=park_id, contractor_profile_id=contractor_profile_id,
        ),
        json=request_body,
    )
    assert response.status_code == 200

    mock_contractor_balances.check(park_id, contractor_profile_id)
    driver_after = get_driver(park_id, contractor_profile_id)
    assert not get_unset_data(driver_after, driver_profile)
    assert get_set_data(
        driver_after, driver_profile,
    ) == prepare_request_to_compare(driver_profile)
    assert driver_after['updated_ts'] != driver_before['updated_ts']
    assert driver_after['modified_date'] != driver_before['modified_date']


@pytest.mark.config(DRIVER_PROFILES_ALLOWED_CONSUMERS=ALLOWED_CONSUMERS_CONFIG)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    ('park_id', 'contractor_profile_id', 'expected_state'),
    [('dbid_1', 'uuid_1', {}), ('dbid_0', 'uuid_0', {'first_name': 'Павел'})],
)
async def test_conflict(
        taxi_driver_profiles,
        get_driver,
        park_id,
        contractor_profile_id,
        expected_state,
):
    driver_before = get_driver(park_id, contractor_profile_id)

    response = await taxi_driver_profiles.put(
        ENDPOINT,
        headers={
            'X-Real-IP': X_REAL_IP,
            'X-Fleet-API-Key-ID': FLEET_API_KEY_ID,
            'X-Ya-Service-Ticket': VALID_SERVICE_TICKET,
        },
        params=dict(
            park_id=park_id, contractor_profile_id=contractor_profile_id,
        ),
        json=make_request(expected_state),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': 'Driver\'s profile wasn\'t updated',
    }

    driver_after = get_driver(park_id, contractor_profile_id)
    assert driver_before == driver_after


@pytest.mark.config(DRIVER_PROFILES_ALLOWED_CONSUMERS=ALLOWED_CONSUMERS_CONFIG)
@pytest.mark.config(TVM_ENABLED=True)
async def test_contractor_not_found(taxi_driver_profiles):
    park_id = 'dbid_1'
    contractor_profile_id = 'random_uuid'

    response = await taxi_driver_profiles.put(
        ENDPOINT,
        headers={
            'X-Real-IP': X_REAL_IP,
            'X-Fleet-API-Key-ID': FLEET_API_KEY_ID,
            'X-Ya-Service-Ticket': VALID_SERVICE_TICKET,
        },
        params=dict(
            park_id=park_id, contractor_profile_id=contractor_profile_id,
        ),
        json=make_request({}),
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Contractor not found',
    }


@pytest.mark.config(DRIVER_PROFILES_ALLOWED_CONSUMERS=ALLOWED_CONSUMERS_CONFIG)
@pytest.mark.config(TVM_ENABLED=True)
async def test_wrong_source_service(taxi_driver_profiles, get_driver):
    park_id = 'dbid_0'
    contractor_profile_id = 'uuid_0'
    driver_before = get_driver(park_id, contractor_profile_id)

    response = await taxi_driver_profiles.put(
        ENDPOINT,
        headers={
            'X-Real-IP': X_REAL_IP,
            'X-Fleet-API-Key-ID': FLEET_API_KEY_ID,
            'X-Ya-Service-Ticket': INVALID_SERVICE_TICKET,
        },
        params=dict(
            park_id=park_id, contractor_profile_id=contractor_profile_id,
        ),
        json=make_request({}),
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Requests are not allowed for this consumer',
    }

    driver_after = get_driver(park_id, contractor_profile_id)
    assert driver_before == driver_after


@pytest.mark.config(DRIVER_PROFILES_ALLOWED_CONSUMERS=ALLOWED_CONSUMERS_CONFIG)
@pytest.mark.config(TVM_ENABLED=True)
async def test_failed_get_personal_data(
        taxi_driver_profiles, get_driver, mockserver,
):
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _personal_retrieve(request):
        request.get_data()
        return mockserver.make_response(
            json={'code': '', 'message': ''}, status=404,
        )

    park_id = 'dbid_0'
    contractor_profile_id = 'uuid_0'
    driver_before = get_driver(park_id, contractor_profile_id)

    response = await taxi_driver_profiles.put(
        ENDPOINT,
        headers={
            'X-Real-IP': X_REAL_IP,
            'X-Fleet-API-Key-ID': FLEET_API_KEY_ID,
            'X-Ya-Service-Ticket': VALID_SERVICE_TICKET,
        },
        params=dict(
            park_id=park_id, contractor_profile_id=contractor_profile_id,
        ),
        json=make_request(
            DEFAULT_EXPECTED_STATE, {'email_pd_id': 'qwerqwqw3e34r'},
        ),
    )
    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }
    assert _personal_retrieve.has_calls

    driver_after = get_driver(park_id, contractor_profile_id)
    assert driver_before == driver_after
