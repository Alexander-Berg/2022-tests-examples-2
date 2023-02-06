# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from bank_wallet_plugins.generated_tests import *
from tests_bank_wallet import common


BUID = '024e7db5-9bd6-4f45-a1cd-2a442e15ffff'
UID = '1'
HANDLE_URL = '/wallet-support/v1/get_plus_balance'


@pytest.fixture(autouse=True)
def bank_userinfo_mock(mockserver):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _mock_get_buid_info(request):
        assert request.json.get('buid') == BUID

        return mockserver.make_response(
            status=200, json={'buid_info': {'buid': BUID, 'yandex_uid': '1'}},
        )

    bank_userinfo_mock.get_buid_info_handler = _mock_get_buid_info

    return bank_userinfo_mock


@pytest.mark.parametrize('body', [{'buid': BUID}, {'uid': UID}])
async def test_ok(
        taxi_bank_wallet, bank_trust_gateway_mock, access_control_mock, body,
):
    headers = common.get_support_headers()
    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json=body,
    )

    assert response.status_code == 200
    assert response.json() == {
        'amount': '124',
        'currency': 'RUB',
        'wallet_id': '42',
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_no_uid(
        taxi_bank_wallet,
        mockserver,
        bank_trust_gateway_mock,
        access_control_mock,
):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _mock_get_buid_info(request):
        return {'buid_info': {'buid': BUID}}

    headers = common.get_support_headers()
    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json={'buid': BUID},
    )

    assert response.status_code == 404


@pytest.mark.parametrize('userinfo_resp_code', [404, 429])
async def test_proxying_userinfo_response(
        taxi_bank_wallet,
        bank_trust_gateway_mock,
        userinfo_resp_code,
        mockserver,
        access_control_mock,
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

    headers = common.get_support_headers()
    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json={'buid': BUID},
    )

    assert response.status_code == userinfo_resp_code


async def test_trust_timeout(
        taxi_bank_wallet,
        bank_trust_gateway_mock,
        mockserver,
        access_control_mock,
):
    @mockserver.json_handler('/bank-trust-gateway/legacy/wallet-balance')
    def _mock_get_plus_balance(request):
        assert request.query.get('uid') == '1'
        raise mockserver.TimeoutError()

    headers = common.get_support_headers()
    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json={'buid': BUID},
    )

    assert bank_userinfo_mock.get_buid_info_handler.has_calls
    assert response.status_code == 500


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
