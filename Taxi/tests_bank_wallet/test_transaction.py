# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest
from tests_bank_wallet import common

from bank_wallet_plugins.generated_tests import *
import copy


def make_trx():
    return {
        'transaction_id': '3',  # purchase
        'status': 'CLEAR',
        'type': 'PURCHASE',
        'direction': 'DEBIT',
        'merchant': {
            'merchant_name': 'YANDEX_EDA',
            'merchant_category_code': '4321',
        },
        'timestamp': '2018-02-01T12:08:48.372+00:00',
        'money': {'amount': '100', 'currency': 'RUB'},
        'plus_debit': {'amount': '50', 'currency': 'RUB'},
        'plus_credit': {'amount': '0', 'currency': 'RUB'},
        'fees': [],
    }


async def test_transaction_purchase(
        taxi_bank_wallet, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {'transaction_id': '3'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
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


async def test_transaction_plus_debit(
        taxi_bank_wallet, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {'transaction_id': '6'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_handler.has_calls
    assert response.json()['base_info']['plus'] == {
        'amount': '-51',
        'currency': 'RUB',
    }


@pytest.mark.parametrize(
    'transaction_id,provider', [('10', 'APPLE'), ('11', 'GOOGLE')],
)
async def test_tokens_in_transaction(
        taxi_bank_wallet, bank_core_statement_mock, transaction_id, provider,
):
    headers = common.get_headers()
    params = {'transaction_id': transaction_id}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_handler.has_calls
    assert response.json()['used_token']['provider'] == provider
    assert response.json()['used_token']['pan_suffix'] == '1234'


@pytest.mark.parametrize(
    'payment_system,transaction_id',
    [
        ('MIR', '13'),
        ('AMERICAN_EXPRESS', '14'),
        ('MASTERCARD', '12'),
        ('VISA', '9'),
    ],
)
async def test_used_card_payment_system_in_transaction(
        taxi_bank_wallet,
        bank_core_statement_mock,
        payment_system,
        transaction_id,
):
    headers = common.get_headers()
    params = {'transaction_id': transaction_id}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_handler.has_calls
    assert response.json()['used_card']['payment_system'] == payment_system


@pytest.mark.parametrize(
    'description,transaction_id',
    [
        ('invalid_plus', '4'),
        ('empty_string_plus', '5'),
        ('invalid_debit_plus_currency', '7'),
        ('invalid_credit_plus_currency', '8'),
        ('invalid_credit_almost_zero_amount', '9'),
    ],
)
async def test_transaction_no_plus(
        taxi_bank_wallet,
        bank_core_statement_mock,
        description,
        transaction_id,
):
    headers = common.get_headers()
    params = {'transaction_id': transaction_id}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_handler.has_calls
    assert 'plus' not in response.json()['base_info']


@pytest.mark.parametrize(
    'locale, description, message, name',
    [
        ('ru', 'ТРАНСПОРТ', 'Выполнено', 'Яндекс.Еда'),
        ('en', 'TRANSPORT', 'Done', 'Yandex.Eda'),
        ('fallback_lang', 'ТРАНСПОРТ', 'Выполнено', 'Яндекс.Еда'),
    ],
)
async def test_transaction_purchase_empty_config_and_another_locale(
        taxi_bank_wallet,
        bank_core_statement_mock,
        locale,
        description,
        message,
        name,
):
    headers = common.get_headers()
    params = {'transaction_id': '3'}
    headers['X-Request-Language'] = locale

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    json = response.json()
    base_info = json['base_info']

    assert base_info.get('name') == name
    assert base_info.get('description') == description
    assert base_info['status']['message'] == message


@pytest.mark.parametrize(
    'trx_id, name, description, status_message',
    [
        ('2', 'Иван А', 'Перевод', 'Выполнено'),
        ('1', 'Иван А', 'Перевод', 'Выполнено'),
    ],
)
async def test_transactions(
        taxi_bank_wallet,
        bank_core_statement_mock,
        trx_id,
        name,
        description,
        status_message,
):
    headers = common.get_headers()
    params = {'transaction_id': trx_id}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    json = response.json()
    base_info = json['base_info']
    assert base_info.get('name') == name
    assert base_info.get('description') == description
    assert base_info['status']['message'] == status_message


async def test_transaction_not_found(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {'transaction_id': 'NOT_FOUND'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 404
    assert bank_core_statement_mock.transaction_handler.has_calls


async def test_transaction_timeout(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    bank_core_statement_mock.need_timeout_exception = True
    headers = common.get_headers()
    params = {'transaction_id': '1'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 500
    assert bank_core_statement_mock.transaction_handler.has_calls


@pytest.mark.parametrize(
    'statements_code,expected_code',
    [(401, 500), (404, 404), (429, 429), (500, 500)],
)
async def test_transaction_error_forwarding(
        taxi_bank_wallet,
        mockserver,
        bank_core_statement_mock,
        statements_code,
        expected_code,
):
    bank_core_statement_mock.needed_error_code = statements_code
    headers = common.get_headers()
    params = {'transaction_id': '1'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == expected_code
    assert bank_core_statement_mock.transaction_handler.has_calls


@pytest.mark.parametrize(
    'header_item', ['X-Yandex-BUID', 'X-YaBank-SessionUUID'],
)
async def test_transaction_empty_header(taxi_bank_wallet, header_item):
    headers = common.get_headers()
    headers[header_item] = ''
    params = {'transaction_id': '1'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'header_item', ['X-Yandex-BUID', 'X-YaBank-SessionUUID'],
)
async def test_transaction_without_header(taxi_bank_wallet, header_item):
    headers = common.get_headers()
    del headers[header_item]
    params = {'transaction_id': '1'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 500


@pytest.mark.xfail(reason='need check empty string')
async def test_transaction_empty_transaction_id(taxi_bank_wallet):
    headers = common.get_headers()
    params = {'transaction_id': ''}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 400


async def test_transaction_without_transaction_id(taxi_bank_wallet):
    headers = common.get_headers()
    params = {}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'statements_type, direction, expected_type, name, description',
    [
        ('C2C_BY_PHONE', 'DEBIT', 'TRANSFER_OUT', 'Иван А', 'Перевод'),
        ('C2C_BY_PHONE', 'CREDIT', 'TRANSFER_IN', 'Иван А', 'Перевод'),
        ('ACCOUNT2ACCOUNT', 'DEBIT', 'TRANSFER_OUT', 'Иван А', 'Перевод'),
        ('ACCOUNT2ACCOUNT', 'CREDIT', 'TRANSFER_IN', 'Иван А', 'Перевод'),
        ('PURCHASE', 'DEBIT', 'PURCHASE', 'Яндекс.Еда', 'ТРАНСПОРТ'),
        ('REFUND', 'CREDIT', 'REFUND', 'Яндекс.Еда', 'ТРАНСПОРТ'),
        ('CARD2ACCOUNT', 'CREDIT', 'TOPUP', 'Пополнение', 'С карты'),
        ('UNKNOWN_STATUS', 'CREDIT', 'TOPUP', 'Пополнение', ''),
        ('UNKNOWN_STATUS', 'DEBIT', 'PURCHASE', 'Покупка', ''),
        ('UNDEFINED', 'CREDIT', 'TOPUP', 'Пополнение', ''),
        ('UNDEFINED', 'DEBIT', 'PURCHASE', 'Покупка', ''),
    ],
)
async def test_transaction_type(
        taxi_bank_wallet,
        mockserver,
        statements_type,
        direction,
        expected_type,
        name,
        description,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        _response = {
            'transaction_id': '3',  # purchase
            'status': 'CLEAR',
            'type': statements_type,
            'direction': direction,
            'timestamp': '2018-02-01T12:08:48.372+00:00',
            'money': {'amount': '100', 'currency': 'RUB'},
            'plus_debit': {'amount': '50', 'currency': 'RUB'},
            'plus_credit': {'amount': '0', 'currency': 'RUB'},
            'fees': [],
        }
        if statements_type in ['C2C_BY_PHONE', 'ACCOUNT2ACCOUNT']:
            _response.update(
                {
                    'rrn': '205500001071',
                    'auth_code': 'CY8PZ5',
                    'originator_system_name': 'Payment Hub',
                    'merchant': {
                        'merchant_name': '',
                        'merchant_country': '',
                        'merchant_category_code': '',
                    },
                    'description': 'Комментарий',
                    'c2c-details': {
                        'phone': '+79123456789',
                        'bank-id': '100000000004',
                        'name': 'Иван Иванович А',
                        'operation-code': 'A2053112902642010000057BD2157589',
                    },
                },
            )
        else:
            _response.update(
                {
                    'merchant': {
                        'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                        'merchant_name': 'YANDEX_EDA',
                        'merchant_country': 'Russia',
                        'merchant_city': 'Moscow',
                        'merchant_category_code': '4321',
                    },
                },
            )
        return _response

    headers = common.get_headers()
    params = {'transaction_id': '3'}
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    json = response.json()
    assert json['base_info']['type'] == expected_type
    assert json['base_info']['name'] == name
    assert json['base_info']['description'] == description


@pytest.mark.parametrize(
    'payment_system, card_number, description',
    [
        ('MIR', '*****************1234', 'С карты МИР ···· 1234'),
        (
            'MASTER_CARD',
            '*****************1234',
            'С карты MasterCard ···· 1234',
        ),
        ('VISA', '*****************1234', 'С карты Visa ···· 1234'),
        ('UNDEFINED', '*****************1234', 'С карты ···· 1234'),
        ('AMERICAN_EXPRESS', '*****************1234', 'С карты ···· 1234'),
        ('MIR', '*******12', 'С карты МИР ···· 12'),
        ('UNDEFINED', None, 'С карты'),
        (None, None, 'С карты'),
        (None, '*****************1234', 'С карты ···· 1234'),
    ],
)
async def test_card_description(
        taxi_bank_wallet, mockserver, payment_system, card_number, description,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        return {
            'transaction_id': '3',  # purchase
            'status': 'CLEAR',
            'type': 'CARD2ACCOUNT',
            'direction': 'CREDIT',
            'timestamp': '2018-02-01T12:08:48.372+00:00',
            'merchant': {
                'merchant_name': 'YANDEX_EDA',
                'merchant_category_code': '4321',
            },
            'money': {'amount': '100', 'currency': 'RUB'},
            'plus_debit': {'amount': '50', 'currency': 'RUB'},
            'plus_credit': {'amount': '0', 'currency': 'RUB'},
            'fees': [],
            'payment_system': payment_system,
            'card_number': card_number,
        }

    headers = common.get_headers()
    params = {'transaction_id': '3'}
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert response.json()['base_info']['name'] == 'Пополнение'
    assert response.json()['base_info']['description'] == description


async def test_no_merchant(taxi_bank_wallet, mockserver):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        return {
            'transaction_id': '3',  # purchase
            'status': 'CLEAR',
            'type': 'PURCHASE',
            'direction': 'DEBIT',
            'timestamp': '2018-02-01T12:08:48.372+00:00',
            'money': {'amount': '100', 'currency': 'RUB'},
            'plus_debit': {'amount': '50', 'currency': 'RUB'},
            'plus_credit': {'amount': '0', 'currency': 'RUB'},
            'fees': [],
        }

    headers = common.get_headers()
    params = {'transaction_id': '3'}
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    json = response.json()
    base_info = json['base_info']

    assert base_info.get('timestamp') == '2018-02-01T12:08:48.372+00:00'
    assert base_info.get('name') == 'Покупка'
    assert base_info.get('description') == 'Прочее'
    assert 'mcc_category' not in json
    assert 'mcc' not in json


async def test_no_mcc(taxi_bank_wallet, mockserver):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        return {
            'transaction_id': '3',  # purchase
            'status': 'CLEAR',
            'type': 'PURCHASE',
            'direction': 'DEBIT',
            'merchant': {'merchant_name': 'YANDEX_EDA'},
            'timestamp': '2018-02-01T12:08:48.372+00:00',
            'money': {'amount': '100', 'currency': 'RUB'},
            'plus_debit': {'amount': '50', 'currency': 'RUB'},
            'plus_credit': {'amount': '0', 'currency': 'RUB'},
            'fees': [],
        }

    headers = common.get_headers()
    params = {'transaction_id': '3'}
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    json = response.json()
    base_info = json['base_info']

    assert base_info.get('timestamp') == '2018-02-01T12:08:48.372+00:00'
    assert base_info.get('name') == 'Яндекс.Еда'
    assert base_info.get('description') == 'Прочее'
    assert 'mcc_category' not in json
    assert 'mcc' not in json


@pytest.mark.config(BANK_WALLET_TRANSACTIONS_TANKER_KEYS=common.TANKER_KEYS)
async def test_transaction_purchase_empty_config_not_found_translation(
        taxi_bank_wallet, mockserver, taxi_config,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        trx = make_trx()
        trx['merchant']['merchant_category_code'] = '0000'
        return trx

    headers = common.get_headers()
    params = {'transaction_id': '3'}

    tanker_key_bad_extra_mcc = copy.deepcopy(common.TANKER_KEYS)
    tanker_key_bad_extra_mcc['extra_mcc_category'] = 'no_key'

    taxi_config.set_values(
        {'BANK_WALLET_TRANSACTIONS_TANKER_KEYS': tanker_key_bad_extra_mcc},
    )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'locale, mcc_category',
    [('ru', 'Прочее'), ('en', 'Other'), ('fallback_lang', 'Прочее')],
)
@pytest.mark.config(BANK_WALLET_TRANSACTIONS_TANKER_KEYS=common.TANKER_KEYS)
async def test_unknown_mcc(
        taxi_bank_wallet, mockserver, taxi_config, locale, mcc_category,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        trx = make_trx()
        trx['merchant']['merchant_category_code'] = '0000'
        return trx

    headers = common.get_headers()
    headers['X-Request-Language'] = locale
    params = {'transaction_id': '3'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    json = response.json()
    base_info = json['base_info']

    assert response.status_code == 200

    assert base_info.get('description') == mcc_category
    assert json.get('mcc_category') == mcc_category
    assert json.get('mcc') == '0000'


async def test_unknown_merchant_name(taxi_bank_wallet, mockserver):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        trx = make_trx()
        trx['merchant']['merchant_category_code'] = '1234'
        trx['merchant']['merchant_name'] = 'KFC'
        return trx

    headers = common.get_headers()
    params = {'transaction_id': '3'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    json = response.json()
    base_info = json['base_info']

    assert response.status_code == 200

    assert base_info.get('name') == 'KFC'


@pytest.mark.parametrize(
    'payment_system, card_number, description',
    [('MIR', '*****************1234', 'С карты МИР ···· 1234')],
)
async def test_card_description_bad_arg_key(
        taxi_bank_wallet,
        mockserver,
        payment_system,
        card_number,
        description,
        taxi_config,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        return {
            'transaction_id': '3',
            'status': 'CLEAR',
            'type': 'CARD2ACCOUNT',
            'direction': 'DEBIT',
            'timestamp': '2018-02-01T12:08:48.372+00:00',
            'merchant': {
                'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                'merchant_name': 'YANDEX_EDA',
                'merchant_country': 'Russia',
                'merchant_city': 'Moscow',
                'merchant_category_code': '4321',
            },
            'money': {'amount': '100', 'currency': 'RUB'},
            'plus_debit': {'amount': '50', 'currency': 'RUB'},
            'plus_credit': {'amount': '0', 'currency': 'RUB'},
            'fees': [],
            'payment_system': payment_system,
            'card_number': card_number,
        }

    headers = common.get_headers()
    params = {'transaction_id': '3'}
    tanker_keys_bad_number_arg_name = copy.deepcopy(common.TANKER_KEYS)
    tanker_keys_bad_number_arg_name['card_description_template'] = {
        'without_params': '',
        'with_payment_system': '',
        'with_number': '',
        'with_payment_system_and_number': common.LONG_KEY,
        'number_arg_name': 'bad_key',
        'payment_system_arg_name': 'payment_type',
    }

    taxi_config.set_values(
        {
            'BANK_WALLET_TRANSACTIONS_TANKER_KEYS': (
                tanker_keys_bad_number_arg_name
            ),
        },
    )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'locale, error_title',
    [
        ('ru', 'Не выполнено'),
        ('en', 'Failed'),
        ('fallback_lang', 'Не выполнено'),
    ],
)
async def test_error_message(
        locale, error_title, mockserver, taxi_bank_wallet,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
    )
    def _mock_get_transaction(request):
        trx = make_trx()
        trx['status'] = 'FAIL'
        trx['error'] = {
            'code': 0,
            'title': 'Title',
            'description': 'Description',
        }
        return trx

    headers = common.get_headers()
    headers['X-Request-Language'] = locale
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info',
        headers=headers,
        json={'transaction_id': '3'},
    )

    assert response.status_code == 200
    assert response.json()['error']['title'] == error_title


async def test_error_message_bad_config(
        mockserver, taxi_bank_wallet, taxi_config,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
    )
    def _mock_get_transaction(request):
        trx = make_trx()
        trx['status'] = 'FAIL'
        trx['error'] = {
            'code': 0,
            'title': 'Title',
            'description': 'Description',
        }
        return trx

    tanker_keys_config = taxi_config.get(
        'BANK_WALLET_TRANSACTIONS_TANKER_KEYS',
    )
    tanker_keys_config.pop('error_type')
    taxi_config.set_values(
        {'BANK_WALLET_TRANSACTIONS_TANKER_KEYS': tanker_keys_config},
    )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info',
        headers=common.get_headers(),
        json={'transaction_id': '3'},
    )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'status, direction, tr_type, name, comment, status_message',
    [
        (
            'HOLD',
            'DEBIT',
            'TRANSFER_OUT',
            'Иван А',
            'Без комментариев',
            'В обработке',
        ),
        (
            'CLEAR',
            'CREDIT',
            'TRANSFER_IN',
            'Иван А',
            'Без комментариев',
            'Выполнено',
        ),
        (
            'CLEAR',
            'DEBIT',
            'TRANSFER_OUT',
            'Иван А',
            'Без комментариев',
            'Выполнено',
        ),
        ('CLEAR', 'DEBIT', 'TRANSFER_OUT', 'Иван А', None, 'Выполнено'),
        (
            'FAIL',
            'DEBIT',
            'TRANSFER_OUT',
            'Иван А',
            'Без комментариев',
            'Не выполнено',
        ),
    ],
)
@pytest.mark.parametrize('transfer_type', ['C2C_BY_PHONE', 'ACCOUNT2ACCOUNT'])
async def test_transfer(
        taxi_bank_wallet,
        mockserver,
        status,
        direction,
        tr_type,
        name,
        comment,
        status_message,
        transfer_type,
):
    if transfer_type == 'ACCOUNT2ACCOUNT':
        bank_id = '100000000150'
        bank_name = 'Яндекс Банк'
    else:
        bank_id = '100000000004'
        bank_name = 'Тинькофф'

    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        result = {
            'transaction_id': '1',
            'status': status,
            'type': transfer_type,
            'direction': direction,
            'timestamp': '2018-01-28T12:08:46.372+00:00',
            'money': {'amount': '10000', 'currency': 'RUB'},
            'plus_debit': {'amount': '0', 'currency': 'RUB'},
            'plus_credit': {'amount': '0', 'currency': 'RUB'},
            'fees': [],
            'rrn': '205500001071',
            'auth_code': 'CY8PZ5',
            'originator_system_name': 'Payment Hub',
            'merchant': {
                'merchant_name': '',
                'merchant_country': '',
                'merchant_category_code': '',
            },
            'c2c-details': {
                'phone': '+79123456789',
                'bank-id': bank_id,
                'name': 'Иван Иванович А',
            },
        }
        if comment:
            result['description'] = comment
        if status != 'FAIL':
            result['c2c-details']['operation-code'] = 'some code'
        return result

    headers = common.get_headers()
    params = {'transaction_id': '1'}
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    tr_info = response.json()['base_info']
    assert tr_info['type'] == tr_type
    assert tr_info['name'] == name
    assert tr_info['description'] == 'Перевод'

    additional_fields = []
    if status == 'HOLD':
        pending = (
            'Сумма пока не зачислена на счёт — '
            'сообщим, как только это случится'
        )
        additional_fields.append({'value': pending})

    transfer_phone_name = (
        'Перевод по номеру телефона'
        if tr_type == 'TRANSFER_OUT'
        else 'Перевод c номера телефона'
    )
    transfer_phone = {'name': transfer_phone_name, 'value': '+7 912 345-67-89'}
    additional_fields.append(transfer_phone)

    b_name = 'Банк отправителя'
    if tr_type == 'TRANSFER_OUT':
        b_name = 'Банк получателя'
    transfer_bank = {'name': b_name, 'value': bank_name}
    additional_fields.append(transfer_bank)

    additional_fields.append({'name': 'Статус', 'value': status_message})

    if comment:
        transfer_comment = {'name': 'Комментарий', 'value': comment}
        additional_fields.append(transfer_comment)

    if status != 'FAIL':
        operation_code = {'name': 'Код операции', 'value': 'some code'}
        additional_fields.append(operation_code)

    assert tr_info['additional_fields'] == additional_fields


@pytest.mark.parametrize(
    'expected_amount, executed_amount, result_amount',
    [
        ('100.00', '20.00', '20.00'),
        ('100.00', '20.0', '20.0'),
        ('100.00', '0.00', '100.00'),
        ('100.00', '10.1234', None),
    ],
)
async def test_money_cashback(
        taxi_bank_wallet,
        mockserver,
        expected_amount,
        executed_amount,
        result_amount,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        trx = make_trx()
        trx['cashback'] = {
            'cashbackType': 'MONEY',
            'currency': 'RUB',
            'expectedAmount': expected_amount,
            'executedAmount': executed_amount,
        }
        return trx

    headers = common.get_headers()
    params = {'transaction_id': '3'}
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    json = response.json()
    if result_amount:
        assert json['base_info']['cashback'] == {
            'amount': result_amount,
            'currency': 'RUB',
        }
    else:
        assert 'cashback' not in json['base_info']


async def test_get_plus_credit_from_cashback_field(
        taxi_bank_wallet, mockserver,
):
    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        trx = make_trx()
        trx['cashback'] = {
            'cashbackType': 'PLUS',
            'currency': 'RUB',
            'expectedAmount': '100',
            'executedAmount': '10',
        }
        return trx

    headers = common.get_headers()
    params = {'transaction_id': '3'}
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert response.json()['base_info']['plus']['amount'] == '10'
