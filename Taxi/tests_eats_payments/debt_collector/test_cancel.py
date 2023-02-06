import pytest


from tests_eats_payments import consts
from tests_eats_payments import db_item_payment_type_plus
from tests_eats_payments import helpers

URL = 'v1/orders/cancel'

NOW = '2020-08-12T07:20:00+00:00'

BASE_PAYLOAD = {'id': 'test_order', 'version': 2, 'revision': 'abcd'}


@pytest.mark.parametrize(
    'items, debts, expect_fail',
    [
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
            id='Happy path',
        ),
    ],
)
async def test_cancel(
        items,
        debts,
        expect_fail,
        mock_transactions_invoice_retrieve,
        mock_debt_collector_update_invoice,
        mock_debt_collector_by_ids,
        mock_transactions_invoice_update,
        mock_transactions_invoice_clear,
        upsert_order,
        upsert_debt_status,
        pgsql,
        taxi_eats_payments,
):
    upsert_order(
        order_id='test_order', business_type=consts.BUSINESS, api_version=2,
    )

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

    upsert_debt_status(order_id='test_order', debt_status='updated')

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
        status='hold_pending',
        operation_id=operation_id,
        payment_type='card',
        terminal_id='456',
        sum=transactions_items,
    )

    mock_transactions_invoice_retrieve(
        cleared=payment_items_list,
        transactions=[transaction_1],
        status='holding',
    )

    update_invoice = mock_debt_collector_update_invoice()
    mock_debt_collector_by_ids(debts=debts)

    transactions_update = mock_transactions_invoice_update(
        items=[], operation_id='cancel:abcd',
    )
    transactions_clear = mock_transactions_invoice_clear()

    response = await taxi_eats_payments.post(URL, json=BASE_PAYLOAD)

    if expect_fail:
        assert response.status == 500
        assert update_invoice.times_called == 0
    else:
        assert response.status == 200
        assert update_invoice.times_called == 1
        assert transactions_update.times_called == 1
        assert transactions_clear.times_called == 1
