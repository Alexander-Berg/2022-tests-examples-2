# pylint: disable=C5521
# flake8: noqa IS001
import pytest

from tests_contractor_profiles_manager.utils import DEFAULT_HEADERS, PARK_ID

ENDPOINT_URL = '/fleet-api/contractors/driver-profile'

DEFAULT_LICENSE_PD_ID = 'license_pd_id'
DEFAULT_EMAIL_PD_ID = 'email_pd_id'
DEFAULT_PHONE_PD_ID = 'phone_pd_id'
DEFAULT_LICENSE = 'A111PP'
DEFAULT_EMAIL = 'test@test.ru'
DEFAULT_PHONE = '+79104607457'
PROJECTION = [
    'data.address',
    'data.balance_deny_onlycard',
    'data.balance_limit',
    'data.car_id',
    'data.check_message',
    'data.comment',
    'data.email_pd_ids',
    'data.fire_date',
    'data.full_name.first_name',
    'data.full_name.last_name',
    'data.full_name.middle_name',
    'data.hire_date',
    'data.license.country',
    'data.license.pd_id',
    'data.license_driver_birth_date',
    'data.license_experience',
    'data.license_expire_date',
    'data.license_issue_date',
    'data.password',
    'data.phone_pd_ids',
    'data.providers',
    'data.rule_id',
    'data.work_status',
]


@pytest.mark.parametrize('contractor_profile_id', ['12345678', '123456789'])
async def test_get_ok(
        taxi_contractor_profiles_manager,
        load_json,
        mock_driver_profiles,
        mock_personal,
        contractor_profile_id,
):
    retrieve_response = load_json('driver_profiles.json')[
        contractor_profile_id
    ]
    expected_response = load_json('responses.json')[contractor_profile_id]
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=contractor_profile_id,
        retrieve_response=retrieve_response,
        projection=PROJECTION,
    )

    mock_personal.set_data(
        driver_license=DEFAULT_LICENSE,
        license_pd_id=DEFAULT_LICENSE_PD_ID,
        phone=DEFAULT_PHONE,
        phone_pd_id=DEFAULT_PHONE_PD_ID,
        email=DEFAULT_EMAIL,
        email_pd_id=DEFAULT_EMAIL_PD_ID,
    )

    response = await taxi_contractor_profiles_manager.get(
        ENDPOINT_URL,
        headers=DEFAULT_HEADERS,
        params={'contractor_profile_id': contractor_profile_id},
    )
    assert mock_driver_profiles.has_proxy_retrive_mock_calls, response.text
    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_driver_not_found(
        taxi_contractor_profiles_manager, mock_driver_profiles,
):
    contractor_profile_id = 'wrong_driver_id'
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=contractor_profile_id,
        retrieve_response=None,
        projection=PROJECTION,
    )

    response = await taxi_contractor_profiles_manager.get(
        ENDPOINT_URL,
        headers=DEFAULT_HEADERS,
        params={'contractor_profile_id': contractor_profile_id},
    )
    assert mock_driver_profiles.has_proxy_retrive_mock_calls, response.text
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'driver_not_found',
        'message': 'driver_not_found',
    }


async def test_personal_not_found(
        taxi_contractor_profiles_manager,
        load_json,
        mock_driver_profiles,
        mock_personal,
):
    contractor_profile_id = '1234567890'
    retrieve_response = load_json('driver_profiles.json')[
        contractor_profile_id
    ]
    expected_response = load_json('responses.json')[contractor_profile_id]
    mock_driver_profiles.set_data(
        park_id=PARK_ID,
        contractor_profile_id=contractor_profile_id,
        retrieve_response=retrieve_response,
        projection=PROJECTION,
    )

    mock_personal.set_data(
        license_pd_id='wrong_license_pd_id',
        phone_pd_id='wrong_phone_pd_id',
        email_pd_id='wrong_email_pd_id',
        error_code=404,
    )

    response = await taxi_contractor_profiles_manager.get(
        ENDPOINT_URL,
        headers=DEFAULT_HEADERS,
        params={'contractor_profile_id': contractor_profile_id},
    )
    assert mock_driver_profiles.has_proxy_retrive_mock_calls, response.text
    assert response.status_code == 200, response.text
    assert response.json() == expected_response
