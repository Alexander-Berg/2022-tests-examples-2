import pytest

from tests_bank_userinfo import common

HANDLE_URL = '/userinfo-support/v1/get_info_by_phone'
HANDLE_URL_INTERNAL = '/userinfo-internal/v1/get_info_by_phone'


@pytest.mark.parametrize('handle', [HANDLE_URL, HANDLE_URL_INTERNAL])
async def test_get_info_not_found_phone(
        taxi_bank_userinfo, mockserver, access_control_mock, handle,
):
    phone = '+79990001111'
    response = await taxi_bank_userinfo.post(
        handle, headers=common.get_support_headers(), json={'phone': phone},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('handle', [HANDLE_URL, HANDLE_URL_INTERNAL])
async def test_get_info_not_found_buid(
        taxi_bank_userinfo, mockserver, access_control_mock, handle,
):
    phone = '+79990001122'
    response = await taxi_bank_userinfo.post(
        handle, headers=common.get_support_headers(), json={'phone': phone},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('handle', [HANDLE_URL, HANDLE_URL_INTERNAL])
async def test_get_info_ok(
        taxi_bank_userinfo, mockserver, access_control_mock, handle,
):
    phone = '+79990001133'
    response = await taxi_bank_userinfo.post(
        handle, headers=common.get_support_headers(), json={'phone': phone},
    )
    assert response.status_code == 200
    assert response.json() == {
        'uid': 'uid',
        'buid': 'c98504fd-de51-403c-9108-8a0aff5e8d30',
        'phone_id': '024e7db5-9bd6-4f45-a1cd-2a442e15bdf3',
        'phone': phone,
        'buid_status': 'FINAL',
        'operation_type': 'UPDATE',
        'operation_at': '2022-02-01T18:28:58.838783+00:00',
    }
    if handle == HANDLE_URL:
        assert access_control_mock.handler_path == HANDLE_URL


async def test_get_info_access_deny(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    phone = '+79990001111'
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={'phone': phone},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1
