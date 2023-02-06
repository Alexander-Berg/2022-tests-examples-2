# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from bank_wallet_plugins.generated_tests import *
from tests_bank_wallet import common

HANDLE_URL = '/wallet-support/v1/get_transactions'


def get_body():
    return {'buid': 'e1533b20-b22a-4476-84fd-ccf50878ce02', 'limit': 200}


async def test_transaction_list(
        taxi_bank_wallet, bank_core_statement_mock, access_control_mock,
):
    headers = common.get_support_headers()
    body = get_body()

    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json=body,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_list_handler.has_calls
    json = response.json()
    assert len(json.get('transactions')) == 15
    assert json.get('cursor') is None

    assert json.get('transactions')[4].get('image') == 'YANDEX_EDA_url'

    assert access_control_mock.handler_path == HANDLE_URL


async def test_support_transaction_no_translate(
        taxi_bank_wallet, bank_core_statement_mock, access_control_mock,
):
    headers = common.get_support_headers()
    body = get_body()

    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json=body,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_list_handler.has_calls
    json = response.json()

    assert json.get('transactions')[0].get('additional_fields')[1] == {
        'name': 'Банк отправителя',
        'value': '100000000999',
    }


async def test_access_deny(
        taxi_bank_wallet, bank_core_statement_mock, access_control_mock,
):
    headers = {'X-Bank-Token': 'deny'}
    body = get_body()

    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json=body,
    )

    assert response.status_code == 401
