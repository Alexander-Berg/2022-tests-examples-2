# pylint: disable=import-error
# pylint: disable=too-many-lines
# pylint: disable=line-too-long

import pytest

from tests_eats_payments import helpers

NOW = '2020-08-14T14:39:50.265+00:00'


@pytest.mark.parametrize(
    'transaction_status, testpoint_entries_amount',
    [('hold_success', 0), ('hold_fail', 1)],
)
@pytest.mark.now(NOW)
async def test_delayed_hold(
        stq_runner,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_customer_services,
        mock_order_revision_list,
        transaction_status,
        testpoint,
        testpoint_entries_amount,
        upsert_order,
):
    upsert_order(
        order_id='test_order',
        business_type='restaurant',
        business_specification='{}',
    )

    @testpoint('task_rescheduled')
    def test_point(request):
        pass

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        None,
        None,
        None,
        **{
            'commit_version': 15,
            'payment_types': ['card'],
            'transactions': [
                helpers.make_transaction(
                    **{
                        'initial_sum': [
                            helpers.make_transactions_item(
                                item_id='big_mac', amount='3.00',
                            ),
                        ],
                        'payment_type': 'card',
                        'operation_id': 'update:hold:id',
                        'sum': [
                            helpers.make_transactions_item(
                                item_id='big_mac', amount='0',
                            ),
                        ],
                        'status': transaction_status,
                    },
                ),
            ],
            'operations': [helpers.make_operation(**{'id': 'update:hold:id'})],
        },
    )

    mock_order_revision_list(revisions=[{'revision_id': '123-321'}])

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='3.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    customer_services_mock = mock_order_revision_customer_services(
        customer_services=customer_services,
    )
    items = [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac', amount='3.00',
                ),
            ],
        ),
    ]
    invoice_update_mock = mock_transactions_invoice_update(
        items=items,
        operation_id='update:hold:test_order:123-321',
        payment_type='card',
        version=2,
    )

    kwargs = {'invoice_id': 'test_order', 'revision': '123-321'}
    await stq_runner.eats_payments_delayed_hold.call(
        task_id=f'update:hold:test_order', kwargs=kwargs, exec_tries=0,
    )

    assert invoice_retrieve_mock.times_called == 2

    assert customer_services_mock.times_called == 1
    assert invoice_update_mock.times_called == 1

    assert test_point.times_called == testpoint_entries_amount
