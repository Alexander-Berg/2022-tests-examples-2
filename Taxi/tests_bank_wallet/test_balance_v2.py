# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_wallet_plugins.generated_tests import *

import pytest

from tests_bank_wallet import common


def make_agreements_balances():
    limits = [common.build_limit('1000', 'RUB', '100', 'MONTH')]
    return [
        {
            'agreement_id': '1',
            'balance': {'amount': '10000', 'currency': 'RUB'},
            'credit_limit': limits,
            'debit_limit': limits,
        },
    ]


async def test_ok(
        taxi_bank_wallet, bank_core_statement_mock, bank_trust_gateway_mock,
):
    bank_core_statement_mock.set_agreements_balances(
        make_agreements_balances(),
    )
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v2/get_balance',
        headers=common.get_headers(),
        json={'agreement_id': '1'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'money': {'amount': '10000', 'currency': 'RUB'},
        'plus': {'amount': '124', 'currency': 'RUB', 'wallet_id': '42'},
    }


async def test_empty_agreements(
        taxi_bank_wallet, bank_core_statement_mock, bank_trust_gateway_mock,
):
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v2/get_balance',
        headers=common.get_headers(),
        json={'agreement_id': '1'},
    )

    assert response.status_code == 500


async def test_multiple_agreements(
        taxi_bank_wallet, bank_core_statement_mock, bank_trust_gateway_mock,
):
    agreements = make_agreements_balances()
    bank_core_statement_mock.set_agreements_balances(agreements + agreements)
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v2/get_balance',
        headers=common.get_headers(),
        json={'agreement_id': '1'},
    )

    assert response.status_code == 500


async def test_agreement_not_found(
        taxi_bank_wallet,
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        mockserver,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/agreements/balance/get', prefix=True,
    )
    def _mock_get_agreements_balances(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'NotFound', 'message': 'Agreement not found'},
        )

    agreements = make_agreements_balances()
    bank_core_statement_mock.set_agreements_balances(agreements + agreements)
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v2/get_balance',
        headers=common.get_headers(),
        json={'agreement_id': '1'},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'handle_path',
    [
        '/bank-core-statement/v1/agreements/balance/get',
        '/bank-trust-gateway/legacy/wallet-balance',
    ],
)
async def test_external_handles_500(
        taxi_bank_wallet,
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        mockserver,
        handle_path,
):
    @mockserver.json_handler(handle_path)
    def _mock_get_agreements_balances(request):
        return mockserver.make_response(status=500)

    bank_core_statement_mock.set_agreements_balances(
        make_agreements_balances(),
    )
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v2/get_balance',
        headers=common.get_headers(),
        json={'agreement_id': '1'},
    )

    assert response.status_code == 500
