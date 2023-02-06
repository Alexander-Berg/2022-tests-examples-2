# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from bank_wallet_plugins.generated_tests import *
from tests_bank_wallet import common

HANDLE_URL = '/wallet-support/v1/transaction/get_info'


def get_body():
    return {
        'buid': 'e1533b20-b22a-4476-84fd-ccf50878ce02',
        'transaction_id': '3',
    }


async def test_get_transaction(
        taxi_bank_wallet, bank_core_statement_mock, access_control_mock,
):
    headers = common.get_support_headers()
    body = get_body()
    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json=body,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_handler.has_calls
    json = response.json()
    base_info = json['base_info']

    assert base_info.get('transaction_id') == '3'
    assert base_info['status']['code'] == 'CLEAR'
    assert base_info['status']['message'] == 'Выполнено'
    assert base_info.get('type') == 'PURCHASE'
    assert base_info.get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert base_info.get('name') == 'Яндекс.Еда'
    assert base_info.get('description') == 'ТРАНСПОРТ'
    assert base_info.get('money') == {'amount': '100', 'currency': 'RUB'}
    assert base_info.get('plus') == {'amount': '50', 'currency': 'RUB'}
    assert base_info.get('image') == 'YANDEX_EDA_url'

    assert json.get('mcc_category') == 'ТРАНСПОРТ'
    assert json.get('mcc') == '4321'
    assert json.get('support_url') == 'some_support_url'

    assert access_control_mock.handler_path == HANDLE_URL


async def test_access_deny(
        taxi_bank_wallet,
        mockserver,
        bank_core_statement_mock,
        access_control_mock,
):
    headers = {'X-Bank-Token': 'deny'}
    body = get_body()

    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json=body,
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    'locale, description, message, name',
    [
        ('ru', 'ТРАНСПОРТ', 'Выполнено', 'Яндекс.Еда'),
        ('en', 'TRANSPORT', 'Done', 'Yandex.Eda'),
        ('fallback_lang', 'ТРАНСПОРТ', 'Выполнено', 'Яндекс.Еда'),
    ],
)
async def test_locale(
        taxi_bank_wallet,
        bank_core_statement_mock,
        locale,
        description,
        message,
        name,
        access_control_mock,
):
    headers = common.get_support_headers()
    headers['X-Request-Language'] = locale

    response = await taxi_bank_wallet.post(
        HANDLE_URL, headers=headers, json=get_body(),
    )

    assert response.status_code == 200
    json = response.json()
    base_info = json['base_info']

    assert base_info.get('name') == name
    assert base_info.get('description') == description
    assert base_info['status']['message'] == message
