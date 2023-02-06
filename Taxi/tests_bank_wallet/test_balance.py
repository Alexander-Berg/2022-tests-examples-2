# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_wallet_plugins.generated_tests import *

import pytest


def make_checks(
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        expected_response,
        response,
        status_code: int = 200,
):
    assert response.status_code == status_code
    assert bank_trust_gateway_mock.plus_balance_handler.has_calls
    assert bank_core_statement_mock.wallets_balance2_handler.has_calls
    assert response.json() == expected_response


async def test_get_wallet_one_plus(
        taxi_bank_wallet, bank_core_statement_mock, bank_trust_gateway_mock,
):
    headers = {
        'X-Yandex-BUID': '1',
        'X-YaBank-SessionUUID': '1',
        'X-Yandex-UID': '1',
        'X-YaBank-PhoneID': '1',
        'X-Ya-User-Ticket': '1',
    }

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_balance', headers=headers,
    )

    expected_response = {
        'money': {
            'amount': '10000',
            'currency': 'RUB',
            'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
            'agreement_id': 'test_agreement_id',
        },
        'plus': {'amount': '124', 'currency': 'RUB', 'wallet_id': '42'},
        'status': 'SUCCEEDED',
    }
    make_checks(
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        expected_response,
        response,
    )


async def test_get_wallet_more_one_plus(
        taxi_bank_wallet, bank_core_statement_mock, bank_trust_gateway_mock,
):
    headers = {
        'X-Yandex-BUID': '1',
        'X-YaBank-SessionUUID': '1',
        'X-Yandex-UID': '2',
        'X-YaBank-PhoneID': '1',
        'X-Ya-User-Ticket': '1',
    }

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_balance', headers=headers,
    )

    expected_response = {
        'money': {
            'amount': '10000',
            'currency': 'RUB',
            'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
            'agreement_id': 'test_agreement_id',
        },
        'plus': {'amount': '123', 'currency': 'RUB', 'wallet_id': '39'},
        'status': 'SUCCEEDED',
    }

    make_checks(
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        expected_response,
        response,
    )


async def test_get_wallet_no_rub_plus(
        taxi_bank_wallet, bank_core_statement_mock, bank_trust_gateway_mock,
):
    headers = {
        'X-Yandex-BUID': '1',
        'X-YaBank-SessionUUID': '1',
        'X-Yandex-UID': '3',
        'X-YaBank-PhoneID': '1',
        'X-Ya-User-Ticket': '1',
    }

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_balance', headers=headers,
    )

    expected_response = {
        'money': {
            'amount': '10000',
            'currency': 'RUB',
            'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
            'agreement_id': 'test_agreement_id',
        },
        'plus': {'amount': '0', 'currency': 'RUB'},
        'status': 'SUCCEEDED',
    }

    make_checks(
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        expected_response,
        response,
    )


@pytest.mark.parametrize('uid', ['5', '6'])
async def test_get_wallet_invalid_plus(
        taxi_bank_wallet,
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        uid,
):
    headers = {
        'X-Yandex-BUID': '1',
        'X-YaBank-SessionUUID': '1',
        'X-Yandex-UID': uid,
        'X-YaBank-PhoneID': '1',
        'X-Ya-User-Ticket': '1',
    }
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_balance', headers=headers,
    )
    expected_response = {
        'money': {
            'amount': '10000',
            'currency': 'RUB',
            'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
            'agreement_id': 'test_agreement_id',
        },
        'status': 'PARTIAL_FAILED',
    }
    make_checks(
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        expected_response,
        response,
    )


async def test_get_wallet_no_rub_plus_no_wallet(
        taxi_bank_wallet, bank_core_statement_mock, bank_trust_gateway_mock,
):
    headers = {
        'X-Yandex-BUID': 'bad_buid',
        'X-YaBank-SessionUUID': '1',
        'X-Yandex-UID': '3',
        'X-YaBank-PhoneID': '1',
        'X-Ya-User-Ticket': '1',
    }

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_balance', headers=headers,
    )

    expected_response = {
        'plus': {'amount': '0', 'currency': 'RUB'},
        'status': 'PARTIAL_FAILED',
    }

    make_checks(
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        expected_response,
        response,
    )


async def test_get_wallet_many_rub_pluses_no_wallet(
        taxi_bank_wallet, bank_core_statement_mock, bank_trust_gateway_mock,
):
    headers = {
        'X-Yandex-BUID': 'bad_buid',
        'X-YaBank-SessionUUID': '1',
        'X-Yandex-UID': '4',
        'X-YaBank-PhoneID': '1',
        'X-Ya-User-Ticket': '1',
    }

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_balance', headers=headers,
    )

    expected_response = {'code': '500', 'message': 'Internal Server Error'}

    make_checks(
        bank_core_statement_mock,
        bank_trust_gateway_mock,
        expected_response,
        response,
        500,
    )
