# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from bank_wallet_plugins.generated_tests import *
from tests_bank_wallet import common


BUID = '024e7db5-9bd6-4f45-a1cd-2a442e15ffff'
UID = '1234567'
HANDLE_URL = '/wallet-support/v1/get_plus_subscription_info'


@pytest.fixture(autouse=True)
def bank_userinfo_mock(mockserver):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _mock_get_buid_info(request):
        assert request.json.get('buid') == BUID

        return mockserver.make_response(
            status=200, json={'buid_info': {'buid': BUID, 'yandex_uid': UID}},
        )

    bank_userinfo_mock.get_buid_info_handler = _mock_get_buid_info

    return bank_userinfo_mock


@pytest.fixture(autouse=True)
def _blackbox_mock(mockserver):
    class Context:
        def __init__(self):
            self.has_plus = False
            self.blackbox_handle = None

    context = Context()

    @mockserver.json_handler('/blackbox/blackbox')
    def _mock_blackbox(request):
        assert request.query == {
            'attributes': '1015',
            'uid': UID,
            'userip': '127.0.0.1',
            'format': 'json',
            'method': 'userinfo',
        }
        if context.has_plus:
            return {'users': [{'id': UID, 'attributes': {'1015': '1'}}]}

        return {'users': [{'id': UID}]}

    context.blackbox_handle = _mock_blackbox
    return context


@pytest.mark.parametrize('body', [{'buid': BUID}, {'uid': UID}])
@pytest.mark.parametrize('has_plus', [True, False])
async def test_ok(
        taxi_bank_wallet, _blackbox_mock, has_plus, access_control_mock, body,
):
    _blackbox_mock.has_plus = has_plus
    response = await taxi_bank_wallet.post(
        HANDLE_URL, json=body, headers=common.get_support_headers(),
    )

    assert response.status_code == 200
    assert bank_userinfo_mock.get_buid_info_handler.has_calls == (
        'buid' in body
    )
    assert _blackbox_mock.blackbox_handle.has_calls
    assert response.json() == {'has_active_subscription': has_plus}
    assert access_control_mock.handler_path == HANDLE_URL


async def test_no_uid(taxi_bank_wallet, mockserver, access_control_mock):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _mock_get_buid_info(request):
        return {'buid_info': {'buid': BUID}}

    response = await taxi_bank_wallet.post(
        HANDLE_URL, json={'buid': BUID}, headers=common.get_support_headers(),
    )

    assert response.status_code == 404


@pytest.mark.parametrize('userinfo_resp_code', [404, 429])
async def test_proxying_userinfo_response(
        taxi_bank_wallet, userinfo_resp_code, mockserver, access_control_mock,
):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _mock_get_buid_info(request):
        assert request.json.get('buid') == BUID

        return mockserver.make_response(
            status=userinfo_resp_code,
            json={'code': 'error_code', 'message': 'error_message'},
        )

    response = await taxi_bank_wallet.post(
        HANDLE_URL, json={'buid': BUID}, headers=common.get_support_headers(),
    )

    assert response.status_code == userinfo_resp_code


async def test_blackbox_timeout(
        taxi_bank_wallet, mockserver, access_control_mock,
):
    @mockserver.json_handler('/blackbox/blackbox')
    def _mock_blackbox(request):
        raise mockserver.TimeoutError()

    response = await taxi_bank_wallet.post(
        HANDLE_URL, json={'buid': BUID}, headers=common.get_support_headers(),
    )

    assert bank_userinfo_mock.get_buid_info_handler.has_calls
    assert response.status_code == 500


async def test_blackbox_error(
        taxi_bank_wallet, mockserver, access_control_mock,
):
    @mockserver.json_handler('/blackbox/blackbox')
    def _mock_blackbox(request):
        return {
            'users': [{'id': UID}],
            'error': 'some error',
            'exception': {'id': 1, 'value': 'value'},
        }

    response = await taxi_bank_wallet.post(
        HANDLE_URL, json={'buid': BUID}, headers=common.get_support_headers(),
    )

    assert response.status_code == 200


async def test_access_deny(taxi_bank_wallet, access_control_mock):
    headers = {'X-Bank-Token': 'deny'}
    body = {'buid': BUID}

    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json=body,
    )

    assert response.status_code == 401


async def test_empty_request(taxi_bank_wallet, access_control_mock):
    response = await taxi_bank_wallet.post(
        HANDLE_URL, json={}, headers=common.get_support_headers(),
    )

    assert response.status_code == 400


async def test_both_uid_and_buid_400(taxi_bank_wallet, access_control_mock):
    response = await taxi_bank_wallet.post(
        HANDLE_URL,
        json={'buid': BUID, 'uid': UID},
        headers=common.get_support_headers(),
    )

    assert response.status_code == 400
