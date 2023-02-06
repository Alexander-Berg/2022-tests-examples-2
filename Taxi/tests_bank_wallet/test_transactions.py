# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from bank_wallet_plugins.generated_tests import *
from tests_bank_wallet import common


async def test_transaction_list(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {'page_size': 200}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_list_handler.has_calls
    json = response.json()
    assert len(json.get('transactions')) == 15
    assert json.get('cursor') is None

    assert json.get('transactions')[4].get('image') == 'YANDEX_EDA_url'
    assert json.get('transactions')[1].get('cashback') == {
        'amount': '20.00',
        'currency': 'RUB',
    }


async def test_transaction_list_with_page_size(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {'page_size': 1}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_list_handler.has_calls
    json = response.json()
    assert len(json.get('transactions')) == 1
    assert json.get('transactions')[0].get('transaction_id') == '15'
    assert (
        json.get('cursor')
        == 'eyJjdXJzb3Jfa2V5IjoiMTUiLCAicGFnZV9zaXplIjoxfQ=='
    )


async def test_transaction_list_with_cursor(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {'cursor': 'eyJjdXJzb3Jfa2V5IjoiMiIsICJwYWdlX3NpemUiOjF9'}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_list_handler.has_calls
    json = response.json()
    assert len(json.get('transactions')) == 1
    assert json.get('transactions')[0].get('transaction_id') == '1'
    assert json.get('cursor') is None


async def test_transaction_list_with_cursor_and_page_size(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {
        'cursor': 'eyJjdXJzb3Jfa2V5IjoiMiIsICJwYWdlX3NpemUiOjF9',
        'page_size': 200,
    }

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 500
    assert bank_core_statement_mock.transaction_list_handler.has_calls


async def test_transaction_list_without_cursor_and_page_size(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_list_handler.has_calls
    json = response.json()
    assert len(json.get('transactions')) == 15
    assert json.get('cursor') is None


async def test_transaction_list_timeout(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    bank_core_statement_mock.need_timeout_exception = True
    headers = common.get_headers()
    params = {}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 500
    assert bank_core_statement_mock.transaction_list_handler.has_calls


@pytest.mark.parametrize(
    'statements_code,expected_code', [(400, 500), (429, 429), (500, 500)],
)
async def test_transaction_list_error_forwarding(
        taxi_bank_wallet,
        mockserver,
        bank_core_statement_mock,
        statements_code,
        expected_code,
):
    bank_core_statement_mock.needed_error_code = statements_code
    headers = common.get_headers()
    params = {}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == expected_code
    assert bank_core_statement_mock.transaction_list_handler.has_calls


@pytest.mark.parametrize(
    'header_item', ['X-Yandex-BUID', 'X-YaBank-SessionUUID'],
)
async def test_transaction_list_empty_header(taxi_bank_wallet, header_item):
    headers = common.get_headers()
    headers[header_item] = ''
    params = {}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    'header_item', ['X-Yandex-BUID', 'X-YaBank-SessionUUID'],
)
async def test_transaction_list_without_header(taxi_bank_wallet, header_item):
    headers = common.get_headers()
    del headers[header_item]
    params = {}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 401


async def test_transactions_timestamps(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {'page_size': 15}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_list_handler.has_calls
    json = response.json()
    transactions = json.get('transactions')
    assert len(transactions) == 15
    assert json.get('cursor') is None

    assert transactions[0].get('timestamp') == '2018-01-28T12:08:46.372+00:00'
    assert transactions[1].get('timestamp') == '2018-02-01T12:08:47.0+00:00'
    assert transactions[2].get('timestamp') == '2018-02-01T12:08:47.0+00:00'
    assert transactions[3].get('timestamp') == '2018-02-01T12:08:47.0+00:00'
    assert transactions[4].get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert transactions[5].get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert transactions[6].get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert transactions[7].get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert transactions[8].get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert transactions[9].get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert transactions[10].get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert transactions[11].get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert transactions[12].get('timestamp') == '2018-02-01T12:08:48.0+00:00'
    assert transactions[13].get('timestamp') == '2018-02-01T12:08:47.0+00:00'
    assert transactions[14].get('timestamp') == '2018-01-28T12:08:46.372+00:00'


async def test_transactions_merchants(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {'page_size': 15}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_list_handler.has_calls
    json = response.json()
    transactions = json.get('transactions')
    assert len(transactions) == 15
    assert json.get('cursor') is None

    assert transactions[4]['name'] == 'Яндекс.Еда'


@pytest.mark.parametrize('accessor_id', [None, 'public_card_id'])
async def test_transaction_list_v2(
        taxi_bank_wallet, mockserver, bank_core_statement_mock, accessor_id,
):
    headers = common.get_headers()
    params = {'limit': 200, 'agreement_id': 'public_agreement_id'}
    if accessor_id:
        params.update({'accessor_id': accessor_id})

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v2/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 200

    json = response.json()
    assert len(json.get('transactions')) == 15
    assert json.get('cursor') is None

    assert json.get('transactions')[4].get('image') == 'YANDEX_EDA_url'
    assert json.get('transactions')[1].get('cashback') == {
        'amount': '20.00',
        'currency': 'RUB',
    }
    assert bank_core_statement_mock.trx_list_by_agreement_handler.has_calls


@pytest.mark.parametrize('accessor_id', [None, 'public_card_id'])
async def test_transaction_list_v2_with_cursor(
        taxi_bank_wallet, mockserver, bank_core_statement_mock, accessor_id,
):
    headers = common.get_headers()
    params = {
        'cursor': 'eyJjdXJzb3Jfa2V5IjoiMiIsICJwYWdlX3NpemUiOjF9',
        'agreement_id': 'public_agreement_id',
        'limit': 200,
    }
    if accessor_id:
        params.update({'accessor_id': accessor_id})

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v2/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 200
    json = response.json()
    assert len(json.get('transactions')) == 1
    assert json.get('transactions')[0].get('transaction_id') == '1'
    assert json.get('cursor') is None
    assert bank_core_statement_mock.trx_list_by_agreement_handler.has_calls


@pytest.mark.parametrize('accessor_id', [None, 'public_card_id'])
async def test_transaction_list_v2_not_found(
        taxi_bank_wallet, mockserver, bank_core_statement_mock, accessor_id,
):
    handler_prefix = '/bank-core-statement/v1/transactions/grouped-by-status/'
    handler_suffix = 'get-by-agreement-id'

    @mockserver.json_handler(handler_prefix + handler_suffix)
    def _mock_get_transaction_list(request):
        return mockserver.make_response(
            status=404, json={'code': 'NotFound', 'message': 'NotFound'},
        )

    headers = common.get_headers()
    params = {'limit': 200, 'agreement_id': 'public_agreement_id'}
    if accessor_id:
        params.update({'accessor_id': accessor_id})

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v2/get_transactions', headers=headers, json=params,
    )
    assert response.status_code == 404
    assert _mock_get_transaction_list.has_calls


async def test_transactions_no_translate(
        taxi_bank_wallet, mockserver, bank_core_statement_mock,
):
    headers = common.get_headers()
    params = {}

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions', headers=headers, json=params,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.transaction_list_handler.has_calls
    json = response.json()
    assert json.get('transactions')[0].get('additional_fields')[1] == {
        'name': 'Банк отправителя',
        'value': '100000000999',
    }
