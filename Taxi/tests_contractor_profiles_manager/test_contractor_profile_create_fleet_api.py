# pylint: disable=C5521
# flake8: noqa IS001
import pytest

from tests_contractor_profiles_manager.utils import (
    DEFAULT_HEADERS,
    FLEET_API_CLIENT_ID,
    FLEET_API_KEY_ID,
    X_REAL_IP,
)

ENDPOINT_URL = '/fleet-api/contractors/driver-profile'

IDEMPOTENCY_TOKEN = '67754336-d4d1-43c1-aadb-cabd06674ea6'

AUTHOR_FLEET_API_HEADERS = {
    **DEFAULT_HEADERS,
    'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
}

DEFAULT_ORDER_PROVIDER = {'platform': False, 'partner': False}


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


@pytest.mark.parametrize(
    'account, order_provider, contact_info, driver_license,'
    'driver_license_experience, full_name, profile, car_id',
    [
        (
            {
                'balance_limit': '-500',
                'payment_service_id': '123456',
                'work_rule_id': '1a0637cca3d8417a8d2af2723205ddee',
                'block_orders_on_balance_below_limit': False,
            },
            {'platform': True, 'partner': False},
            {
                'address': 'Шелепихинская набержная 34к3',
                'email': 'kontakt4kontakt@yandex.ru',
                'phone': '+79104607457',
            },
            {
                'birth_date': '1994-01-01',
                'country': 'rus',
                'expiry_date': '2029-03-07',
                'issue_date': '2019-03-07',
                'number': '1122333444',
            },
            {'total_since_date': '2014-02-27'},
            {
                'last_name': 'Contractor',
                'first_name': 'Contractor',
                'middle_name': 'Романович',
            },
            {'hire_date': '2021-05-13', 'comment': 'Заметки парка'},
            'car_id',
        ),
        (
            {
                'balance_limit': '-500',
                'work_rule_id': '1a0637cca3d8417a8d2af2723205ddee',
                'block_orders_on_balance_below_limit': True,
            },
            DEFAULT_ORDER_PROVIDER,
            {'phone': '+79104607457'},
            {
                'birth_date': '1994-01-01',
                'country': 'rus',
                'expiry_date': '2029-03-07',
                'issue_date': '2019-03-07',
                'number': '1122333444',
            },
            None,
            {'last_name': 'Contractor', 'first_name': 'Contractor'},
            {'hire_date': '2021-05-13'},
            None,
        ),
        (
            {
                'balance_limit': '-500',
                'work_rule_id': '1a0637cca3d8417a8d2af2723205ddee',
                'block_orders_on_balance_below_limit': False,
            },
            DEFAULT_ORDER_PROVIDER,
            {'phone': '+79104607457'},
            {
                'birth_date': '1994-01-01',
                'country': 'rus',
                'expiry_date': '2029-03-07',
                'issue_date': '2019-03-07',
                'number': '1122333444',
            },
            None,
            {'last_name': 'Contractor', 'first_name': 'Contractor'},
            {'hire_date': '2021-05-13'},
            None,
        ),
    ],
)
async def test_post_ok(
        taxi_contractor_profiles_manager,
        mock_parks_driver_creation,
        car_id,
        account,
        order_provider,
        contact_info,
        driver_license,
        driver_license_experience,
        full_name,
        profile,
):
    mock_parks_driver_creation.set_data(
        order_provider=order_provider,
        full_name=full_name,
        contact_info=contact_info,
        profile=profile,
        account=account,
        driver_license=driver_license,
        driver_license_experience=driver_license_experience,
        car_id=car_id,
        fleet_api_client_id=FLEET_API_CLIENT_ID,
        fleet_api_key_id=FLEET_API_KEY_ID,
        real_ip=X_REAL_IP,
        idempotency_token=IDEMPOTENCY_TOKEN,
    )

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
    response = await taxi_contractor_profiles_manager.post(
        ENDPOINT_URL, json=request_body, headers=AUTHOR_FLEET_API_HEADERS,
    )
    assert mock_parks_driver_creation.has_mock_parks_calls, response.text
    assert response.status_code == 200, response.text


@pytest.mark.parametrize(
    'order_provider, contact_info, full_name, profile, header',
    [
        (
            DEFAULT_ORDER_PROVIDER,
            {'phone': 'aaaaaaa'},
            {'last_name': 'Contractor', 'first_name': 'Contractor'},
            {'hire_date': '2021-05-13'},
            AUTHOR_FLEET_API_HEADERS,
        ),
        (
            DEFAULT_ORDER_PROVIDER,
            {'phone': '+9178589894'},
            {'last_name': 'Contractor', 'first_name': 'Contractor'},
            {'hire_date': '2021'},
            AUTHOR_FLEET_API_HEADERS,
        ),
        (
            DEFAULT_ORDER_PROVIDER,
            {'phone': '+9178589894'},
            {'last_name': None, 'first_name': None},
            {'hire_date': '2021-05-13'},
            AUTHOR_FLEET_API_HEADERS,
        ),
        (
            DEFAULT_ORDER_PROVIDER,
            {'phone': '+9178589894'},
            {'last_name': 'Contractor', 'first_name': 'Contractor'},
            {'hire_date': '2021-05-13'},
            {},
        ),
    ],
)
async def test_bad_request(
        taxi_contractor_profiles_manager,
        mock_parks_driver_creation,
        order_provider,
        contact_info,
        full_name,
        profile,
        header,
):
    mock_parks_driver_creation.set_data(
        order_provider=order_provider,
        full_name=full_name,
        contact_info=contact_info,
        profile=profile,
        fleet_api_client_id=FLEET_API_CLIENT_ID,
        fleet_api_key_id=FLEET_API_KEY_ID,
        real_ip=X_REAL_IP,
        idempotency_token=IDEMPOTENCY_TOKEN,
    )

    request_body = _make_contractor_request_body(
        order_provider=order_provider,
        full_name=full_name,
        contact_info=contact_info,
        profile=profile,
    )
    response = await taxi_contractor_profiles_manager.post(
        ENDPOINT_URL, json=request_body, headers=header,
    )
    assert response.status_code == 400, response.text
