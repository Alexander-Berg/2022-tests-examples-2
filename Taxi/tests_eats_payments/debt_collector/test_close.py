import pytest

from tests_eats_payments import consts
from tests_eats_payments import db_item_payment_type_plus
from tests_eats_payments import helpers

URL = 'v1/orders/close'

BASE_HEADERS = {
    'X-Yandex-Uid': '100500',
    'X-YaTaxi-User': 'personal_phone_id=123abcdef456789',
}
BASE_BODY = {'id': 'test_order'}

NOW = '2020-08-12T07:20:00+00:00'


@pytest.mark.parametrize(
    'items, debts, expect_fail, invoice_status,' 'update_operation_id',
    [
        pytest.param(
            [
                {
                    'item_id': 'identity_1',
                    'payment_type': 'debt-collector',
                    'plus_amount': '0.00',
                },
            ],
            [],
            True,
            'hold-failed',
            None,
            id='Fail on no debts',
        ),
        pytest.param(
            [
                {
                    'item_id': 'identity_1',
                    'payment_type': 'debt-collector',
                    'plus_amount': '0.00',
                },
            ],
            [helpers.make_debt(reason_code='auto')],
            False,
            'held',
            'update:abcd',
            id='Updating main invoice on close',
        ),
        pytest.param(
            [
                {
                    'item_id': 'identity_1',
                    'payment_type': 'debt-collector',
                    'plus_amount': '0.00',
                },
            ],
            [helpers.make_debt(reason_code='technical_debt')],
            False,
            'hold-failed',
            'cancel:abcd',
            id='Happy path',
        ),
    ],
)
@pytest.mark.now(NOW)
async def test_close(
        upsert_order,
        upsert_debt_status,
        pgsql,
        mock_transactions_invoice_retrieve,
        mock_debt_collector_update_invoice,
        mock_order_revision_list,
        mock_transactions_invoice_update,
        mockserver,
        taxi_eats_payments,
        mock_debt_collector_by_ids,
        items,
        debts,
        expect_fail,
        invoice_status,
        update_operation_id,
):
    upsert_order(
        order_id='test_order', business_type=consts.BUSINESS, api_version=2,
    )

    upsert_debt_status(order_id='test_order', debt_status='updated')

    if items:
        for item in items:
            db_item_payment_type_plus.DBItemPaymentTypePlus(
                pgsql=pgsql,
                item_id=item['item_id'],
                order_id='test_order',
                payment_type=item['payment_type'],
                plus_amount=item['plus_amount'],
                customer_service_type='composition_products',
            ).insert()

    operation_id = 'create:100500'

    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]

    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]

    transaction_1 = helpers.make_transaction(
        external_payment_id='external_payment_id_1',
        status='hold_fail',
        operation_id=operation_id,
        payment_type='card',
        terminal_id='456',
        sum=transactions_items,
    )

    mock_transactions_invoice_retrieve(
        cleared=payment_items_list,
        transactions=[transaction_1],
        status=invoice_status,
    )

    mock_debt_collector_by_ids(debts=debts)
    mock_order_revision_list()

    update_invoice = mock_debt_collector_update_invoice()
    invoice_close_request_body = {**BASE_BODY, **{'clear_eta': NOW}}

    invoice_update_mock = mock_transactions_invoice_update(
        items=[], operation_id=update_operation_id,
    )

    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def _transactions_clear_invoice_handler(request):
        assert request.json == invoice_close_request_body
        return mockserver.make_response(**{'status': 200, 'json': {}})

    body = BASE_BODY
    headers = BASE_HEADERS
    response = await taxi_eats_payments.post(URL, json=body, headers=headers)

    if expect_fail:
        assert response.status == 500
        assert update_invoice.times_called == 0
        assert invoice_update_mock.times_called == 0
    else:
        assert response.status == 200
        assert update_invoice.times_called == 1
        assert invoice_update_mock.times_called == 1
