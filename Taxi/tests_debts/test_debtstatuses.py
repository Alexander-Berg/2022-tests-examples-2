import json

import bson
import pytest

from tests_debts import utils


@pytest.fixture(name='mock_transactions_invoice')
def _mock_transactions_invoice(mockserver, load_json):
    response_v2 = load_json('transactions/response_invoice_retrive_v2.json')

    @mockserver.json_handler('/transactions/v2/invoice/retrieve')
    def _invoice_retrieve(request):
        return mockserver.make_response(json.dumps(response_v2), 200)


@pytest.fixture(name='mock_order_core')
def _mock_order_core(mockserver, load_json):
    response = load_json('order_core/response.json')

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _order_proc_get_fields(request):
        body = bson.BSON(request.get_data()).decode()
        assert body['fields'] == utils.ORDER_PROC_BULK_GET_FIELDS
        order_id = request.query['order_id']
        return mockserver.make_response(
            response=bson.BSON.encode(response[order_id]),
            status=200,
            content_type='application/bson',
        )


@pytest.fixture(name='mock_antifraud')
def _mock_antifraud(mockserver):
    @mockserver.handler('/antifraud/v1/overdraft/limit')
    def _mock_limit(request):
        return mockserver.make_response({'value': -1, 'currency': 'RUB'}, 200)


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_get_debstatuses_no_debt_payment_state(
        debts_client, mock_order_core, mock_antifraud,
):
    response, code = await debts_client.get_debstatuses(
        yandex_uid='yandex_uid_no_debt', phone_id='phone_id_no_debt',
    )
    assert code == 200
    assert response == {'payment_state': 'no_debt'}


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_get_debstatuses_bad_request(debts_client, mock_antifraud):
    _, code = await debts_client.get_debstatuses(
        yandex_uid='yandex_uid_bad_request',
    )
    assert code == 400


@pytest.mark.config(
    DEBTS_USE_V2_TRANSACTIONS_API=True,
    DEBTS_DEBTSTATUSES_CONTENT=utils.CONFIG_DEBSTATUSES_CONTENT,
)
@pytest.mark.translations(
    client_messages=utils.CLIENT_MESSAGES, tariff=utils.TARIFF_TRANSLATIONS,
)
@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.parametrize(
    'yandex_uid, phone_id, expected_response_path',
    [
        (
            'yandex_uid_diff_currency',
            'phone_id_diff_currency',
            'diff_currency_default.json',
        ),
        (
            'yandex_uid_same_currency',
            'phone_id_same_currency',
            'same_currency_default.json',
        ),
    ],
)
async def test_get_debstatuses_debt_payment_state(
        debts_client,
        yandex_uid,
        phone_id,
        expected_response_path,
        mock_transactions_invoice,
        mock_order_core,
        mock_antifraud,
        load_json,
):
    # Нужно позже добавить свои отдельные заказы в базу
    # когда будем писать полноценные тесты
    response, code = await debts_client.get_debstatuses(
        yandex_uid=yandex_uid, phone_id=phone_id, is_cash_available=True,
    )
    assert code == 200
    expected = load_json(expected_response_path)
    assert response == expected
