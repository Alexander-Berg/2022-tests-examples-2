import typing

import pytest


from tests_eats_payments import consts
from tests_eats_payments import db_item_payment_type_plus
from tests_eats_payments import helpers

URL = 'v2/orders/update'


@pytest.fixture(name='check_update_order_v2')
def check_update_order_fixture(taxi_eats_payments, mockserver, load_json):
    async def _inner(
            payment_type: typing.Optional[str] = 'card',
            payment_method_id: typing.Optional[str] = '123',
            response_status=200,
            response_body=None,
            ttl: int = None,
    ):
        request_payload = {
            'id': 'test_order',
            'version': 2,
            'revision': 'abcd',
        }
        if payment_type is not None:
            request_payload['payment_method'] = {
                'id': payment_method_id,
                'type': payment_type,
            }

        payload: typing.Dict[str, typing.Any] = {**request_payload}
        if ttl is not None:
            payload['ttl'] = ttl
        response = await taxi_eats_payments.post(URL, json=payload)
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


@pytest.mark.parametrize(
    'items, debts, expect_fail',
    [
        pytest.param(
            [
                {
                    'item_id': 'big_mac',
                    'payment_type': 'debt-collector',
                    'plus_amount': '0.00',
                },
            ],
            [],
            True,
            id='Fail on no debts',
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
            id='Happy path',
        ),
    ],
)
async def test_invoice_update(
        stq,
        upsert_order,
        upsert_debt_status,
        pgsql,
        items,
        debts,
        expect_fail,
        mock_debt_collector_by_ids,
        check_update_order_v2,
        get_db_items_payment_type_by_order_id,
        mock_transactions_invoice_retrieve,
        mock_order_revision_list,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_debt_collector_update_invoice,
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

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='Big Mac Burger',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            personal_tin_id='634333f24bc54736b4ad70dcf69759c7',
        ),
        helpers.make_customer_service(
            customer_service_id='big_mac_2',
            name='Big Mac Burger',
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
    mock_debt_collector_by_ids(debts=debts)
    update_invoice = mock_debt_collector_update_invoice()

    if expect_fail:
        response_status = 500
        payment_type = None
    else:
        response_status = 200
        payment_type = 'card'

    await check_update_order_v2(
        response_status=response_status, payment_type=payment_type,
    )

    if not expect_fail:
        db_items = get_db_items_payment_type_by_order_id('test_order')
        for (_, _, payment_type, _, _) in db_items:
            assert payment_type == 'debt-collector'

        assert update_invoice.times_called == 1
        helpers.check_callback_mock(
            callback_mock=stq.eda_order_processing_payment_events_callback,
            times_called=1,
            task_id='update:test_order:abcd',
            queue='eda_order_processing_payment_events_callback',
            **{
                'order_id': 'test_order',
                'action': 'update',
                'status': 'confirmed',
                'revision': 'abcd',
            },
        )


async def test_update_with_stratagy_sent(
        stq,
        upsert_order,
        upsert_debt_status,
        pgsql,
        mock_transactions_invoice_retrieve,
        mock_order_revision_list,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        check_update_order_v2,
):
    upsert_order(
        order_id='test_order', business_type=consts.BUSINESS, api_version=2,
    )

    items = [
        {
            'item_id': 'big_mac',
            'payment_type': 'debt-collector',
            'plus_amount': '0.00',
        },
    ]

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

    upsert_debt_status(order_id='test_order', debt_status='held')

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
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='Big Mac Burger',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            personal_tin_id='634333f24bc54736b4ad70dcf69759c7',
        ),
        helpers.make_customer_service(
            customer_service_id='big_mac_2',
            name='Big Mac Burger',
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

    await check_update_order_v2(response_status=200, payment_type='card')

    helpers.check_callback_mock(
        callback_mock=stq.eda_order_processing_payment_events_callback,
        times_called=1,
        task_id='update:test_order:abcd',
        queue='eda_order_processing_payment_events_callback',
        **{
            'order_id': 'test_order',
            'action': 'update',
            'status': 'rejected',
            'revision': 'abcd',
        },
    )
