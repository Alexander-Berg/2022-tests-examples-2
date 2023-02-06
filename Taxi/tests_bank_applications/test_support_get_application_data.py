import pytest

from tests_bank_applications import common


HANDLE_URL = '/applications-support/v1/get_application_data'


async def test_get_application_data_uid(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': '7948e3a9-623c-4524-a390-9e4264d27a01'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'application_id': '7948e3a9-623c-4524-a390-9e4264d27a01',
        'type': 'REGISTRATION',
        'status': 'FAILED',
        'db_status': 'FAILED',
        'reason': 'error2',
        'uid': common.DEFAULT_YANDEX_UID,
        'additional_params': {'param': 'value'},
        'initiator': {'initiator_type': 'SUPPORT', 'initiator_id': '1234'},
        'operation_type': 'INSERT',
        'operation_at': '2022-02-01T20:28:58.838783+00:00',
    }
    assert access_control_mock.handler_path == HANDLE_URL


@pytest.mark.parametrize('empty_add_params', [True, False])
async def test_get_application_data_buid_simplified_esia(
        taxi_bank_applications,
        mockserver,
        access_control_mock,
        empty_add_params,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a12'
    if empty_add_params:
        application_id = '7948e3a9-623c-4524-a390-9e4264d27a13'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 200
    resp = response.json()
    app = {
        'application_id': application_id,
        'type': 'SIMPLIFIED_IDENTIFICATION_ESIA',
        'status': 'FAILED',
        'db_status': 'FAILED',
        'initiator': {'initiator_id': '1234', 'initiator_type': 'SUPPORT'},
        'buid': common.DEFAULT_YANDEX_BUID,
        'operation_type': 'INSERT',
        'operation_at': '2022-02-10T20:28:58.838783+00:00',
    }
    if not empty_add_params:
        app['additional_params'] = {
            'redirect_url': 'http://redirect.url',
            'esia_state': 'esia.state',
            'data_revision': 1234,
            'auth_code': 'auth.code',
        }
    assert resp == app
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_application_data_kyc(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': '7948e3a9-623c-4524-a390-9e4264d22222'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'application_id': '7948e3a9-623c-4524-a390-9e4264d22222',
        'type': 'KYC',
        'status': 'SUCCESS',
        'db_status': 'SUCCESS',
        'buid': common.DEFAULT_YANDEX_BUID,
        'initiator': {'initiator_type': 'SUPPORT', 'initiator_id': '1234'},
        'reason': 'error4',
        'operation_type': 'INSERT',
        'operation_at': '2022-02-09T20:28:58.838783+00:00',
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_application_data_digital_card(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': '7948e3a9-623c-4524-a390-9e4264d27a05'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'application_id': '7948e3a9-623c-4524-a390-9e4264d27a05',
        'type': 'DIGITAL_CARD_ISSUE',
        'status': 'FAILED',
        'db_status': 'FAILED',
        'buid': common.DEFAULT_YANDEX_BUID,
        'initiator': {'initiator_type': 'SUPPORT', 'initiator_id': '1234'},
        'reason': 'error',
        'operation_type': 'INSERT',
        'operation_at': '2022-02-05T20:28:58.838783+00:00',
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_application_data_plus(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': '3ac0a2cc-637e-4c50-b7c3-87d1e641cb9c'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'additional_params': {},
        'application_id': '3ac0a2cc-637e-4c50-b7c3-87d1e641cb9c',
        'type': 'PLUS',
        'status': 'SUCCESS',
        'db_status': 'SUCCESS',
        'buid': common.DEFAULT_YANDEX_BUID,
        'initiator': {
            'initiator_type': 'BUID',
            'initiator_id': '67754336-d4d1-43c1-aadb-cabd06674ea6',
        },
        'operation_type': 'INSERT',
        'operation_at': '2022-02-03T20:28:58.838783+00:00',
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_application_data_not_found(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': '7948e3a9-623c-4524-a390-9e4264d27a00'},
    )
    assert response.status_code == 404


async def test_get_application_data_without_app_id(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=common.get_support_headers(),
    )
    assert response.status_code == 400


async def test_get_application_data_access_deny(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={'application_id': '7948e3a9-623c-4524-a390-9e4264d27a00'},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1
