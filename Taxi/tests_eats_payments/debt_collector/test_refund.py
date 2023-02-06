import typing

import pytest


from tests_eats_payments import consts
from tests_eats_payments import db_item_payment_type_plus
from tests_eats_payments import helpers
from tests_eats_payments import models

URL = 'v2/orders/refund'


OPERATION_ID = 'refund:abcd'
ORDER_ID = 'test_order'

COMPLEMENT = models.Complement(amount='1.00')

BASE_PAYLOAD = {'order_id': ORDER_ID, 'version': 2, 'revision': 'abcd'}


@pytest.fixture(name='mock_refund_invoice_retrieve')
def _mock_refund_invoice_retrieve(mock_transactions_invoice_retrieve):
    def _inner(
            *args, invoice_status: typing.Optional[str] = 'cleared', **kwargs,
    ):
        return mock_transactions_invoice_retrieve(
            status=invoice_status, *args, **kwargs,
        )

    return _inner


@pytest.fixture(name='check_refund')
def check_refund_fixture(taxi_eats_payments, mockserver, load_json):
    async def _inner(payload, response_status=200, response_body=None):
        payload: typing.Dict[str, typing.Any] = {**payload}
        response = await taxi_eats_payments.post(URL, json=payload)
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


@pytest.mark.parametrize(
    'items, debts, expect_fail, version',
    [
        pytest.param(
            [
                {
                    'item_id': 'big_mac',
                    'payment_type': 'debt-collector',
                    'plus_amount': '0.00',
                },
            ],
            [helpers.make_debt(reason_code='technical_debt')],
            False,
            2,
            id='Happy path',
        ),
        pytest.param(
            [
                {
                    'item_id': 'big_mac',
                    'payment_type': 'debt-collector',
                    'plus_amount': '0.00',
                },
            ],
            [helpers.make_debt(reason_code='technical_debt')],
            False,
            3,
            id='Test version mismatch',
        ),
    ],
)
async def test_invoice_update(
        upsert_order,
        upsert_debt_status,
        pgsql,
        items,
        debts,
        expect_fail,
        mock_refund_invoice_retrieve,
        mock_order_revision_list,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_update,
        check_refund,
        version,
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

    previous_operation_items = [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products-0', amount='5.00',
                ),
            ],
        ),
    ]

    invoice_retrieve_items = [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products-0', amount='3.00',
                ),
            ],
        ),
    ]

    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=previous_operation_items,
    )
    operation2 = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )

    mock_refund_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation1, operation2],
    )

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products-0',
            name='Composition products',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            personal_tin_id='634333f24bc54736b4ad70dcf69759c7',
        ),
    ]

    mock_order_revision_customer_services(customer_services=customer_services)
    mock_order_revision_customer_services_details(
        customer_services=customer_services,
    )
    mock_order_revision_list()
    transactions_update_mock = mock_transactions_invoice_update(
        invoice_id='test_order-debt',
        operation_id='refund:abcd',
        payment_type='card',
        items=[
            helpers.make_transactions_payment_items(
                payment_type='card',
                items=[
                    helpers.make_transactions_item(
                        item_id='composition-products-0',
                        amount='2.00',
                        fiscal_receipt_info={
                            'personal_tin_id': (
                                '634333f24bc54736b4ad70dcf69759c7'
                            ),
                            'vat': 'nds_20',
                            'title': 'Composition products',
                        },
                    ),
                ],
            ),
        ],
    )

    if expect_fail:
        response_status = 500
    else:
        response_status = 200

    payload = BASE_PAYLOAD
    payload['version'] = version
    await check_refund(response_status=response_status, payload=payload)
    if not expect_fail:
        assert transactions_update_mock.times_called == 1
