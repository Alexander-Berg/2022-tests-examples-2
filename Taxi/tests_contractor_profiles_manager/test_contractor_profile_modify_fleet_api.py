# pylint: disable=C5521, C0302
# flake8: noqa IS001
import pytest


from tests_contractor_profiles_manager.utils import (
    DEFAULT_DUPLICATES_PROFILE,
    DEFAULT_HEADERS_BASE,
    DEFAULT_HEADERS,
    DEFAULT_RETRIEVE_PROFILE,
    DEFAULT_SPECIFICATIONS,
    FLEET_API_KEY_ID,
    PARK_ID,
    SPECIFICATIONS_MAP,
    X_REAL_IP,
)

ENDPOINT_URL_FLEET_API = '/fleet-api/contractors/driver-profile'
ENDPOINT_URL_FLEET = '/fleet/contractor-profiles-manager/v1/contractor-profile'

FLEET_YANDEX_UID = '123'
FLEET_TICKET_PROVIDER = 'yandex'

API_HEADERS = {
    ENDPOINT_URL_FLEET_API: DEFAULT_HEADERS,
    ENDPOINT_URL_FLEET: {
        **DEFAULT_HEADERS_BASE,
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': FLEET_TICKET_PROVIDER,
        'X-Yandex-Login': 'tarasalk',
        'X-Yandex-UID': FLEET_YANDEX_UID,
    },
}

DRIVER_PROFILES_DATA = {
    ENDPOINT_URL_FLEET_API: {'key_id': FLEET_API_KEY_ID},
    ENDPOINT_URL_FLEET: {
        'yandex_uid': FLEET_YANDEX_UID,
        'ticket_provider': FLEET_TICKET_PROVIDER,
    },
}

CONTRACTOR_PROFILE_ID = '12345678'

DEFAULT_RULE_ID = '1234'

DEFAULT_ACCOUNT = {
    'balance_limit': '-500',
    'payment_service_id': '1234560',
    'work_rule_id': DEFAULT_RULE_ID,
    'block_orders_on_balance_below_limit': False,
}
DEFAULT_ORDER_PROVIDER = {'platform': True, 'partner': False}
DEFAULT_LICENSE = {
    'birth_date': '1970-01-15',
    'country': 'rus',
    'expiry_date': '2029-03-07',
    'issue_date': '2020-03-07',
    'number': '1122333444',
}
DEFAULT_LICENSE_EXPERIENCE = {'total_since_date': '2014-03-07'}
DEFAULT_CONTACT_INFO = {'phone': '+79104607457'}
DEFAULT_FULL_NAME = {'last_name': 'Contractor', 'first_name': 'Contractor'}
DEFAULT_PROFILE = {'hire_date': '2021-05-13', 'work_status': 'working'}

DEFAULT_LICENSE_PD_ID = 'license_pd_id'
DEFAULT_EMAIL_PD_ID = 'email_pd_id'
DEFAULT_PHONE_PD_ID = 'phone_pd_id'

PROJECTION = [
    'data.is_removed_by_request',
    'data.license.country',
    'data.license.pd_id',
    'data.license_driver_birth_date',
    'data.license_expire_date',
    'data.license_issue_date',
    'data.license_experience',
    'data.full_name.first_name',
    'data.full_name.middle_name',
    'data.full_name.last_name',
    'data.phone_pd_ids',
    'data.work_status',
    'data.rule_id',
    'data.hire_date',
    'data.fire_date',
    'data.email_pd_ids',
    'data.address',
    'data.comment',
    'data.check_message',
    'data.password',
    'data.created_date',
    'data.balance_limit',
]


def _make_contractor_request_body(
        order_provider,
        full_name,
        contact_info,
        profile,
        account=None,
        driver_license=None,
        driver_license_experience=None,
        is_deaf=None,
        car_id=None,
):
    return {
        'account': account,
        'car_id': car_id,
        'order_provider': order_provider,
        'person': {
            'contact_info': contact_info,
            'driver_license': driver_license,
            'driver_license_experience': driver_license_experience,
            'full_name': full_name,
            'is_deaf': is_deaf,
        },
        'profile': profile,
    }


@pytest.mark.config(PARKS_ENABLE_DKVU_CHECK_BEFORE_EDIT=True)
@pytest.mark.parametrize('url', [ENDPOINT_URL_FLEET_API, ENDPOINT_URL_FLEET])
@pytest.mark.parametrize(
    'account, order_provider, contact_info, driver_license,'
    'driver_license_experience, full_name, profile, car_id',
    [
        (
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            {
                'address': 'Шелепихинская набержная 34к3',
                'email': 'kontakt4kontakt@yandex.ru',
                'phone': '+79104607457',
            },
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            {
                'last_name': 'Contractor',
                'first_name': 'Contractor',
                'middle_name': 'Романович',
            },
            {
                'fire_date': '2022-01-01',
                'hire_date': '2021-05-13',
                'comment': 'Заметки парка',
                'feedback': 'Заметкa',
                'work_status': 'fired',
            },
            'car_id',
        ),
        (
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
        ),
    ],
)
async def test_put_ok(
        taxi_contractor_profiles_manager,
        mock_driver_work_rules,
        mock_fleet_parks,
        mock_fleet_vehicles,
        mock_personal,
        mock_taximeter_xservice,
        mock_driver_profiles,
        url,
        car_id,
        account,
        order_provider,
        contact_info,
        driver_license,
        driver_license_experience,
        full_name,
        profile,
):
    request_body = _make_contractor_request_body(
        order_provider=order_provider,
        full_name=full_name,
        contact_info=contact_info,
        profile=profile,
        account=account,
        driver_license=driver_license,
        driver_license_experience=driver_license_experience,
        car_id=car_id,
    )

    has_email = 'email' in contact_info

    mock_fleet_parks.set_data(park_id=PARK_ID)
    mock_driver_work_rules.set_data(
        rule_id=account['work_rule_id'], park_id=PARK_ID,
    )
    mock_fleet_vehicles.set_data(park_id=PARK_ID, vehicle_id=car_id)
    mock_taximeter_xservice.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        status='fail',
    )
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        retrieve_response=DEFAULT_RETRIEVE_PROFILE,
        projection=PROJECTION,
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        payment_service_id=account['payment_service_id'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
        email_pd_id=DEFAULT_EMAIL_PD_ID if has_email else None,
        driver_profile=request_body,
        user_ip=X_REAL_IP,
    )
    mock_driver_profiles.set_data(**DRIVER_PROFILES_DATA[url])

    mock_personal.set_data(
        driver_license=driver_license['number'],
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        phone=contact_info['phone'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
        email=contact_info.get('email'),
        email_pd_id=DEFAULT_EMAIL_PD_ID,
    )

    response = await taxi_contractor_profiles_manager.put(
        url,
        json=request_body,
        headers=API_HEADERS[url],
        params={'contractor_profile_id': CONTRACTOR_PROFILE_ID},
    )
    assert response.status_code == 204, response.text
    assert mock_driver_work_rules.has_mock_get_rule_calls
    assert mock_driver_work_rules.has_mock_rules_compatible_calls
    assert mock_fleet_parks.has_mock_parks_calls
    assert mock_personal.has_store_calls
    assert mock_driver_profiles.has_proxy_retrive_mock_calls
    assert mock_driver_profiles.has_check_duplicates_mock_calls
    assert mock_driver_profiles.has_update_profile_mock_calls
    if car_id is not None:
        assert mock_fleet_vehicles.has_mock_parks_calls


@pytest.mark.parametrize('url', [ENDPOINT_URL_FLEET_API, ENDPOINT_URL_FLEET])
@pytest.mark.parametrize(
    'is_park_found, error_code',
    [(False, 'park_not_found'), (True, 'driver_not_found')],
)
async def test_not_found(
        taxi_contractor_profiles_manager,
        mock_fleet_parks,
        mock_driver_profiles,
        url,
        is_park_found,
        error_code,
):
    mock_fleet_parks.set_data(park_id=PARK_ID, is_park_found=is_park_found)
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        projection=PROJECTION,
    )
    request_body = _make_contractor_request_body(
        order_provider=DEFAULT_ORDER_PROVIDER,
        full_name=DEFAULT_FULL_NAME,
        contact_info=DEFAULT_CONTACT_INFO,
        profile=DEFAULT_PROFILE,
        account=DEFAULT_ACCOUNT,
        driver_license=DEFAULT_LICENSE,
        driver_license_experience=DEFAULT_LICENSE_EXPERIENCE,
    )
    response = await taxi_contractor_profiles_manager.put(
        url,
        json=request_body,
        headers=API_HEADERS[url],
        params={'contractor_profile_id': CONTRACTOR_PROFILE_ID},
    )
    assert response.status_code == 404, response.text
    assert response.json() == {'code': error_code, 'message': error_code}


@pytest.mark.parametrize('url', [ENDPOINT_URL_FLEET_API, ENDPOINT_URL_FLEET])
@pytest.mark.config(
    OPTEUM_CARD_DRIVER_FIELDS_EDIT={
        'enable': True,
        'fields': ['first_name'],
        'enable_backend': True,
        'cities': [],
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable_support': False,
        'enable_support_users': [],
    },
)
async def test_validation_disabled_fields(
        taxi_contractor_profiles_manager,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_personal,
        url,
):
    request_body = _make_contractor_request_body(
        order_provider=DEFAULT_ORDER_PROVIDER,
        full_name={**DEFAULT_FULL_NAME, 'first_name': 'new name'},
        contact_info=DEFAULT_CONTACT_INFO,
        profile=DEFAULT_PROFILE,
        account=DEFAULT_ACCOUNT,
        driver_license=DEFAULT_LICENSE,
        driver_license_experience=DEFAULT_LICENSE_EXPERIENCE,
    )

    mock_fleet_parks.set_data(park_id=PARK_ID)
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        retrieve_response=DEFAULT_RETRIEVE_PROFILE,
        projection=PROJECTION,
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        payment_service_id=DEFAULT_ACCOUNT['payment_service_id'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
        email_pd_id=DEFAULT_EMAIL_PD_ID,
        driver_profile=request_body,
        key_id=FLEET_API_KEY_ID,
        user_ip=X_REAL_IP,
    )
    mock_personal.set_data(
        driver_license=DEFAULT_LICENSE['number'],
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        phone=DEFAULT_CONTACT_INFO['phone'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
    )

    response = await taxi_contractor_profiles_manager.put(
        url,
        json=request_body,
        headers=API_HEADERS[url],
        params={'contractor_profile_id': CONTRACTOR_PROFILE_ID},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'cannot_edit_first_name',
        'message': 'cannot_edit_first_name',
    }


@pytest.mark.parametrize('url', [ENDPOINT_URL_FLEET_API, ENDPOINT_URL_FLEET])
@pytest.mark.config(
    OPTEUM_CARD_DRIVER_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['middle_name'],
        'enable_backend': True,
        'cities': [],
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable_support': False,
        'enable_support_users': [],
    },
)
async def test_validation_required_fields(
        taxi_contractor_profiles_manager,
        mock_fleet_parks,
        mock_driver_profiles,
        url,
):
    mock_fleet_parks.set_data(park_id=PARK_ID)
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        projection=PROJECTION,
    )
    request_body = _make_contractor_request_body(
        order_provider=DEFAULT_ORDER_PROVIDER,
        full_name=DEFAULT_FULL_NAME,
        contact_info=DEFAULT_CONTACT_INFO,
        profile=DEFAULT_PROFILE,
        account=DEFAULT_ACCOUNT,
        driver_license=DEFAULT_LICENSE,
        driver_license_experience=DEFAULT_LICENSE_EXPERIENCE,
    )
    response = await taxi_contractor_profiles_manager.put(
        url,
        json=request_body,
        headers=API_HEADERS[url],
        params={'contractor_profile_id': CONTRACTOR_PROFILE_ID},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'missing_required_field_middle_name',
        'message': 'missing_required_field_middle_name',
    }


@pytest.mark.parametrize('url', [ENDPOINT_URL_FLEET_API, ENDPOINT_URL_FLEET])
@pytest.mark.now('2020-06-12T00:00:00Z')
@pytest.mark.parametrize(
    'contractor_profile_id, account, order_provider,'
    'contact_info, driver_license, driver_license_experience,'
    'full_name, profile, car_id, error_code',
    [
        (
            # cannot_edit_removed_driver
            '123456789',
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'cannot_edit_removed_driver',
        ),
        (
            # fire_date_not_allowed_when_work_status_is_not_fired
            '1234567890',
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            {
                'fire_date': '2022-01-01',
                'hire_date': '2021-05-13',
                'comment': 'Заметки парка',
                'feedback': 'Заметкa',
                'work_status': 'working',
            },
            None,
            'fire_date_not_allowed_when_work_status_is_not_fired',
        ),
        (
            # duplicate_driver_license
            '1234567890',
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'duplicate_driver_license',
        ),
        (
            # duplicate_phone (is_courier)
            '12345678901',
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'duplicate_phone',
        ),
        (
            # duplicate_phone (is_working)
            '12345678903',
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'duplicate_phone',
        ),
        (
            # duplicate_payment_service_id
            '12345678902',
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'duplicate_payment_service_id',
        ),
        (
            # invalid_balance_limit
            '12345678902',
            {
                'balance_limit': '1000000009',
                'payment_service_id': '1234560',
                'work_rule_id': '1234',
                'block_orders_on_balance_below_limit': False,
            },
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'invalid_balance_limit',
        ),
        (
            # invalid_driver_license
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            {
                'birth_date': '1994-01-01',
                'country': 'rus',
                'expiry_date': '2029-03-07',
                'issue_date': '2019-03-07',
                'number': '1122333444RWERWERW',
            },
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'invalid_driver_license',
        ),
        (
            # invalid_hire_date
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            {'hire_date': '2221-05-13', 'work_status': 'working'},
            None,
            'invalid_hire_date',
        ),
        (
            # invalid_hire_date
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            {'hire_date': '1821-05-13', 'work_status': 'working'},
            None,
            'invalid_hire_date',
        ),
        (
            # invalid_license_experience_total_since
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            {'total_since_date': '2022-02-27'},
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'invalid_license_experience_total_since',
        ),
        (
            # no_such_car
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            'wrong_car_id',
            'no_such_car',
        ),
        (
            # payment_card_number_in_address
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            {
                'address': 'Шел5469700013493448епихинская набержная 34к3',
                'phone': '+79104607457',
            },
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'payment_card_number_in_address',
        ),
        (
            # payment_card_number_in_email
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            {'email': 'q5469700013493448@ya.ru', 'phone': '+79104607457'},
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'payment_card_number_in_email',
        ),
        (
            # payment_card_number_in_comment
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            {
                'hire_date': '2021-05-13',
                'comment': 'Заме5469700013493448тки парка',
                'work_status': 'working',
            },
            None,
            'payment_card_number_in_comment',
        ),
        (
            # payment_card_number_in_feedback
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            {
                'hire_date': '2021-05-13',
                'feedback': 'Заме5469700013493448тки',
                'work_status': 'working',
            },
            None,
            'payment_card_number_in_feedback',
        ),
        (
            # unsupported_driver_license_country
            CONTRACTOR_PROFILE_ID,
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            {
                'birth_date': '1994-01-01',
                'country': '111',
                'expiry_date': '2029-03-07',
                'issue_date': '2019-03-07',
                'number': '1122333444',
            },
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'unsupported_driver_license_country',
        ),
        (
            # forbidden_signalq_working_status
            '12345678904',
            DEFAULT_ACCOUNT,
            DEFAULT_ORDER_PROVIDER,
            DEFAULT_CONTACT_INFO,
            {
                'birth_date': '1994-01-01',
                'country': '111',
                'expiry_date': '2029-03-07',
                'issue_date': '2019-03-07',
                'number': '1122333444',
            },
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
            None,
            'forbidden_signalq_working_status',
        ),
    ],
)
async def test_bad_request(
        taxi_contractor_profiles_manager,
        mock_driver_work_rules,
        mock_fleet_parks,
        mock_fleet_vehicles,
        mock_personal,
        mock_driver_profiles,
        url,
        load_json,
        contractor_profile_id,
        car_id,
        account,
        order_provider,
        contact_info,
        driver_license,
        driver_license_experience,
        full_name,
        profile,
        error_code,
):
    request_body = _make_contractor_request_body(
        order_provider=order_provider,
        full_name=full_name,
        contact_info=contact_info,
        profile=profile,
        account=account,
        driver_license=driver_license,
        driver_license_experience=driver_license_experience,
        car_id=car_id,
    )

    has_email = 'email' in contact_info
    retrieve_profile = load_json('driver_profiles.json').get(
        contractor_profile_id, DEFAULT_RETRIEVE_PROFILE,
    )
    duplicates_profiles = load_json('driver_profile_duplicates.json').get(
        contractor_profile_id, DEFAULT_DUPLICATES_PROFILE,
    )
    specifications = SPECIFICATIONS_MAP.get(
        contractor_profile_id, DEFAULT_SPECIFICATIONS,
    )

    mock_fleet_parks.set_data(park_id=PARK_ID, specifications=specifications)
    mock_driver_work_rules.set_data(
        rule_id=account['work_rule_id'], park_id=PARK_ID,
    )
    mock_fleet_vehicles.set_data(
        park_id=PARK_ID, vehicle_id=car_id, is_vehicle_found=False,
    )

    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=contractor_profile_id,
        retrieve_response=retrieve_profile,
        projection=PROJECTION,
        check_duplicates_response=duplicates_profiles,
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        payment_service_id=account['payment_service_id'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
        email_pd_id=DEFAULT_EMAIL_PD_ID if has_email else None,
        driver_profile=request_body,
        key_id=FLEET_API_KEY_ID,
        user_ip=X_REAL_IP,
    )
    mock_personal.set_data(
        driver_license=driver_license['number'],
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        phone=contact_info['phone'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
        email=contact_info.get('email'),
        email_pd_id=DEFAULT_EMAIL_PD_ID,
    )

    response = await taxi_contractor_profiles_manager.put(
        url,
        json=request_body,
        headers=API_HEADERS[url],
        params={'contractor_profile_id': contractor_profile_id},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': error_code, 'message': error_code}
    assert mock_fleet_parks.has_mock_parks_calls
    assert mock_driver_profiles.has_proxy_retrive_mock_calls


@pytest.mark.parametrize('url', [ENDPOINT_URL_FLEET_API, ENDPOINT_URL_FLEET])
@pytest.mark.parametrize(
    'returned_rule_id, work_rule_type,returned_rule_compatible_id,'
    'response_code, error_code',
    [
        # wrong work rule type
        ('1234', 'vezet', '1234', 200, 'invalid_work_rule_id'),
        # v1/work-rules - bad request
        ('12345', 'park', '1234', 400, 'invalid_work_rule_id'),
        # work rule id not found
        ('12345', 'park', '1234', 404, 'invalid_work_rule_id'),
        # incompatible work rule
        ('1234', 'park', '12345', 200, 'incompatible_work_rule'),
    ],
)
async def test_invalid_work_rule(
        taxi_contractor_profiles_manager,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_personal,
        mock_driver_work_rules,
        url,
        returned_rule_id,
        work_rule_type,
        returned_rule_compatible_id,
        response_code,
        error_code,
):
    mock_fleet_parks.set_data(park_id=PARK_ID)
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        retrieve_response=DEFAULT_RETRIEVE_PROFILE,
        projection=PROJECTION,
    )
    mock_driver_work_rules.set_data(
        park_id=PARK_ID,
        rule_id=DEFAULT_RULE_ID,
        work_type=work_rule_type,
        returned_rule_id=returned_rule_id,
        response_code=response_code,
        returned_rule_compatible_id=returned_rule_compatible_id,
    )
    mock_personal.set_data(
        driver_license=DEFAULT_LICENSE['number'],
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        phone=DEFAULT_CONTACT_INFO['phone'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
    )
    request_body = _make_contractor_request_body(
        order_provider=DEFAULT_ORDER_PROVIDER,
        full_name=DEFAULT_FULL_NAME,
        contact_info=DEFAULT_CONTACT_INFO,
        profile=DEFAULT_PROFILE,
        account=DEFAULT_ACCOUNT,
        driver_license=DEFAULT_LICENSE,
        driver_license_experience=DEFAULT_LICENSE_EXPERIENCE,
    )
    response = await taxi_contractor_profiles_manager.put(
        url,
        json=request_body,
        headers=API_HEADERS[url],
        params={'contractor_profile_id': CONTRACTOR_PROFILE_ID},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': error_code, 'message': error_code}
    assert mock_fleet_parks.has_mock_parks_calls


@pytest.mark.parametrize('url', [ENDPOINT_URL_FLEET_API, ENDPOINT_URL_FLEET])
@pytest.mark.parametrize(
    'account, contact_info, driver_license, full_name, profile',
    [
        (
            # invalid_string (comment)
            DEFAULT_ACCOUNT,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_FULL_NAME,
            {
                'hire_date': '2021-05-13',
                'work_status': 'working',
                'comment': '\ufefftest',
            },
        ),
        (
            # invalid_string (feedback)
            DEFAULT_ACCOUNT,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            DEFAULT_FULL_NAME,
            {
                'hire_date': '2021-05-13',
                'work_status': 'working',
                'feedback': '\ufefftest',
            },
        ),
        (
            # invalid_string (country)
            DEFAULT_ACCOUNT,
            DEFAULT_CONTACT_INFO,
            {
                'birth_date': '1994-01-01',
                'country': 'rus\ufeff',
                'expiry_date': '2029-03-07',
                'issue_date': '2019-03-07',
                'number': '1122333444',
            },
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
        ),
        (
            # invalid_string (number)
            DEFAULT_ACCOUNT,
            DEFAULT_CONTACT_INFO,
            {
                'birth_date': '1994-01-01',
                'country': 'rus',
                'expiry_date': '2029-03-07',
                'issue_date': '2019-03-07',
                'number': '\ufeff1122333444',
            },
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
        ),
        (
            # invalid_string (address)
            DEFAULT_ACCOUNT,
            {'address': '\ufeffMoscow', 'phone': '+79104607457'},
            DEFAULT_LICENSE,
            DEFAULT_FULL_NAME,
            DEFAULT_PROFILE,
        ),
        (
            # invalid_string (first_name)
            DEFAULT_ACCOUNT,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            {'last_name': 'Contractor', 'first_name': 'Contractor\ufeff'},
            DEFAULT_PROFILE,
        ),
        (
            # invalid_string (last_name)
            DEFAULT_ACCOUNT,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            {'last_name': 'Cont\ufeffractor', 'first_name': 'Contractor'},
            DEFAULT_PROFILE,
        ),
        (
            # invalid_string (middle_name)
            DEFAULT_ACCOUNT,
            DEFAULT_CONTACT_INFO,
            DEFAULT_LICENSE,
            {
                'last_name': 'Contractor',
                'first_name': 'Contractor',
                'middle_name': 'Contractorich\ufeff',
            },
            DEFAULT_PROFILE,
        ),
    ],
)
async def test_invalid_string(
        taxi_contractor_profiles_manager,
        mock_driver_work_rules,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_personal,
        url,
        account,
        contact_info,
        driver_license,
        full_name,
        profile,
):
    request_body = _make_contractor_request_body(
        order_provider=DEFAULT_ORDER_PROVIDER,
        full_name=full_name,
        contact_info=contact_info,
        profile=profile,
        account=account,
        driver_license=driver_license,
        driver_license_experience=DEFAULT_LICENSE_EXPERIENCE,
    )

    mock_fleet_parks.set_data(park_id=PARK_ID)
    mock_driver_work_rules.set_data(
        rule_id=account['work_rule_id'], park_id=PARK_ID,
    )

    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        retrieve_response=DEFAULT_RETRIEVE_PROFILE,
        projection=PROJECTION,
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        payment_service_id=account['payment_service_id'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
        driver_profile=request_body,
        key_id=FLEET_API_KEY_ID,
        user_ip=X_REAL_IP,
    )

    mock_personal.set_data(
        driver_license=DEFAULT_LICENSE['number'],
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        phone=DEFAULT_CONTACT_INFO['phone'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
    )

    response = await taxi_contractor_profiles_manager.put(
        url,
        json=request_body,
        headers=API_HEADERS[url],
        params={'contractor_profile_id': CONTRACTOR_PROFILE_ID},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_string',
        'message': 'invalid_string',
    }


@pytest.mark.parametrize('url', [ENDPOINT_URL_FLEET_API, ENDPOINT_URL_FLEET])
@pytest.mark.config(PARKS_ENABLE_DKVU_CHECK_BEFORE_EDIT=True)
@pytest.mark.parametrize(
    'driver_license, license_pd_id, driver_license_experience, full_name',
    [
        (
            # cannot_edit_driver_license_and_full_name_when_dkvu_passed
            # (first_name)
            DEFAULT_LICENSE,
            'license_pd_id_',
            DEFAULT_LICENSE_EXPERIENCE,
            {
                'first_name': 'Рус',
                'last_name': 'Убер',
                'middle_name': 'Москва',
            },
        ),
        (
            # cannot_edit_driver_license_and_full_name_when_dkvu_passed
            # (last_name)
            DEFAULT_LICENSE,
            'license_pd_id_',
            DEFAULT_LICENSE_EXPERIENCE,
            {
                'first_name': 'Водитель',
                'last_name': 'Уб',
                'middle_name': 'Москва',
            },
        ),
        (
            # cannot_edit_driver_license_and_full_name_when_dkvu_passed
            # (middle_name)
            DEFAULT_LICENSE,
            'license_pd_id_',
            DEFAULT_LICENSE_EXPERIENCE,
            {
                'first_name': 'Водитель',
                'last_name': 'Убер',
                'middle_name': 'Питер',
            },
        ),
        (
            # cannot_edit_driver_license_and_full_name_when_dkvu_passed
            # (license_pd_id)
            DEFAULT_LICENSE,
            DEFAULT_LICENSE_PD_ID,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
        ),
        (
            # cannot_edit_driver_license_and_full_name_when_dkvu_passed
            # (birth_date)
            {
                'birth_date': '1980-01-15',
                'country': 'rus',
                'expiry_date': '2029-03-07',
                'issue_date': '2020-03-07',
                'number': '1122333444',
            },
            DEFAULT_LICENSE_PD_ID,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
        ),
        (
            # cannot_edit_driver_license_and_full_name_when_dkvu_passed
            # (expiry_date)
            {
                'birth_date': '1970-01-15',
                'country': 'rus',
                'expiry_date': '2028-03-07',
                'issue_date': '2020-03-07',
                'number': '1122333444',
            },
            DEFAULT_LICENSE_PD_ID,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
        ),
        (
            # cannot_edit_driver_license_and_full_name_when_dkvu_passed
            # (issue_date)
            {
                'birth_date': '1970-01-15',
                'country': 'rus',
                'expiry_date': '2029-03-07',
                'issue_date': '2025-03-07',
                'number': '1122333444',
            },
            DEFAULT_LICENSE_PD_ID,
            DEFAULT_LICENSE_EXPERIENCE,
            DEFAULT_FULL_NAME,
        ),
        (
            # cannot_edit_driver_license_and_full_name_when_dkvu_passed
            # (license_experience)
            {
                'birth_date': '1970-01-15',
                'country': 'rus',
                'expiry_date': '2029-03-07',
                'issue_date': '2025-03-07',
                'number': '1122333444',
            },
            DEFAULT_LICENSE_PD_ID,
            None,
            DEFAULT_FULL_NAME,
        ),
        (
            # cannot_edit_driver_license_and_full_name_when_dkvu_passed
            # (license_experience)
            {
                'birth_date': '1970-01-15',
                'country': 'rus',
                'expiry_date': '2029-03-07',
                'issue_date': '2025-03-07',
                'number': '1122333444',
            },
            DEFAULT_LICENSE_PD_ID,
            {'total_since_date': '2016-03-07'},
            DEFAULT_FULL_NAME,
        ),
    ],
)
async def test_license_and_full_name_unchanged(
        taxi_contractor_profiles_manager,
        mock_driver_work_rules,
        mock_fleet_parks,
        mock_personal,
        mock_driver_profiles,
        mock_taximeter_xservice,
        url,
        driver_license,
        license_pd_id,
        driver_license_experience,
        full_name,
):
    request_body = _make_contractor_request_body(
        order_provider=DEFAULT_ORDER_PROVIDER,
        full_name=full_name,
        contact_info=DEFAULT_CONTACT_INFO,
        profile=DEFAULT_PROFILE,
        account=DEFAULT_ACCOUNT,
        driver_license=driver_license,
        driver_license_experience=driver_license_experience,
    )

    mock_fleet_parks.set_data(park_id=PARK_ID)
    mock_driver_work_rules.set_data(
        rule_id=DEFAULT_ACCOUNT['work_rule_id'], park_id=PARK_ID,
    )
    mock_personal.set_data(
        driver_license=driver_license['number'],
        license_pd_id=license_pd_id,
        phone=DEFAULT_CONTACT_INFO['phone'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
    )
    mock_taximeter_xservice.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        status='success',
    )
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        retrieve_response=DEFAULT_RETRIEVE_PROFILE,
        projection=PROJECTION,
        license_pd_id=license_pd_id,
        payment_service_id=DEFAULT_ACCOUNT['payment_service_id'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
        driver_profile=request_body,
        key_id=FLEET_API_KEY_ID,
        user_ip=X_REAL_IP,
    )

    response = await taxi_contractor_profiles_manager.put(
        url,
        json=request_body,
        headers=API_HEADERS[url],
        params={'contractor_profile_id': CONTRACTOR_PROFILE_ID},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'cannot_edit_driver_license_and_full_name_when_dkvu_passed',
        'message': 'cannot_edit_driver_license_and_full_name_when_dkvu_passed',
    }


@pytest.mark.parametrize('url', [ENDPOINT_URL_FLEET_API, ENDPOINT_URL_FLEET])
async def test_conflict(
        taxi_contractor_profiles_manager,
        mock_driver_work_rules,
        mock_fleet_parks,
        mock_personal,
        mock_driver_profiles,
        url,
):
    request_body = _make_contractor_request_body(
        order_provider=DEFAULT_ORDER_PROVIDER,
        full_name=DEFAULT_FULL_NAME,
        contact_info=DEFAULT_CONTACT_INFO,
        profile=DEFAULT_PROFILE,
        account=DEFAULT_ACCOUNT,
        driver_license=DEFAULT_LICENSE,
        driver_license_experience=DEFAULT_LICENSE_EXPERIENCE,
    )

    mock_fleet_parks.set_data(park_id=PARK_ID)
    mock_driver_work_rules.set_data(
        rule_id=DEFAULT_ACCOUNT['work_rule_id'], park_id=PARK_ID,
    )
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        retrieve_response=DEFAULT_RETRIEVE_PROFILE,
        projection=PROJECTION,
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        payment_service_id=DEFAULT_ACCOUNT['payment_service_id'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
        driver_profile=request_body,
        user_ip=X_REAL_IP,
        save_response_code=409,
    )
    mock_driver_profiles.set_data(**DRIVER_PROFILES_DATA[url])
    mock_personal.set_data(
        driver_license=DEFAULT_LICENSE['number'],
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        phone=DEFAULT_CONTACT_INFO['phone'],
        phone_pd_id=DEFAULT_PHONE_PD_ID,
    )

    response = await taxi_contractor_profiles_manager.put(
        url,
        json=request_body,
        headers=API_HEADERS[url],
        params={'contractor_profile_id': CONTRACTOR_PROFILE_ID},
    )
    assert response.status_code == 409, response.text
