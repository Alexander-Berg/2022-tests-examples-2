# pylint: disable=import-error
# pylint: disable=too-many-lines
# pylint: disable=line-too-long

import pytest

from tests_eats_payments import helpers

NOW = '2020-08-14T14:39:50.265+00:00'


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    (
        'transaction_initial_sum',
        'transaction_sum',
        'transaction_status',
        'expected_action',
        'pass_afs_params',
        'trust_afs_params',
    ),
    [
        pytest.param(
            [helpers.make_transactions_item(item_id='big_mac', amount='3.00')],
            [helpers.make_transactions_item(item_id='big_mac', amount='0')],
            'hold_success',
            'update',
            False,  # pass_afs_params
            None,  # trust_afs_params
            id='Unholded invoice with transaction hold_success. Hold again',
        ),
        pytest.param(
            [helpers.make_transactions_item(item_id='big_mac', amount='3.00')],
            [helpers.make_transactions_item(item_id='big_mac', amount='0')],
            'hold_success',
            'update',
            True,  # pass_afs_params
            {'request': 'mit'},  # trust_afs_params
            id='Unholded invoice with transaction hold_success. '
            'Hold again with mit',
        ),
        pytest.param(
            [helpers.make_transactions_item(item_id='big_mac', amount='3.00')],
            [helpers.make_transactions_item(item_id='big_mac', amount='3.00')],
            'hold_success',
            'clear',
            False,  # pass_afs_params
            None,  # trust_afs_params
            id='Updated invoice is ready for clearing',
        ),
        pytest.param(
            [helpers.make_transactions_item(item_id='big_mac', amount='4.00')],
            [helpers.make_transactions_item(item_id='big_mac', amount='3.00')],
            'hold_success',
            'reschedule',
            False,  # pass_afs_params
            None,  # trust_afs_params
            id='Invoice updating is in progress. Reschedule a task',
        ),
        pytest.param(
            [helpers.make_transactions_item(item_id='big_mac', amount='0')],
            [helpers.make_transactions_item(item_id='big_mac', amount='3.00')],
            'hold_resize',
            'reschedule',
            False,  # pass_afs_params
            None,  # trust_afs_params
            id='Invoice with transaction hold_resize. '
            'Invoice updating is in progress. Reschedule a task',
        ),
    ],
)
@pytest.mark.parametrize('payment_type', ['card', 'applepay'])
async def test_hold_unhold_callback(
        stq_runner,
        mockserver,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_transactions_invoice_clear,
        mock_order_revision_customer_services,
        mock_order_revision_list,
        transaction_initial_sum,
        transaction_sum,
        transaction_status,
        expected_action,
        payment_type,
        stq,
        experiments3,
        pass_afs_params,
        trust_afs_params,
        upsert_order,
):
    upsert_order(
        order_id='test_order',
        business_type='restaurant',
        business_specification='{}',
    )
    experiments3.add_config(
        **helpers.make_pass_afs_params_experiment(pass_afs_params),
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        None,
        None,
        None,
        **{
            'commit_version': 15,
            'payment_types': [payment_type],
            'transactions': [
                helpers.make_transaction(
                    **{
                        'initial_sum': transaction_initial_sum,
                        'payment_type': payment_type,
                        'sum': transaction_sum,
                        'status': transaction_status,
                    },
                ),
            ],
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
            payment_type=payment_type, items=transaction_initial_sum,
        ),
    ]
    invoice_update_mock = mock_transactions_invoice_update(
        items=items,
        operation_id='update:hold:test_order:123-321',
        payment_type=payment_type,
        version=2,
        trust_afs_params=trust_afs_params,
    )

    invoice_clear_mock = mock_transactions_invoice_clear()

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def mock_stq_reschedule(request):
        return {}

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'update:unhold:test_order',
    }
    await stq_runner.eats_payments_hold_unhold.call(
        task_id=f'update:unhold:test_order', kwargs=kwargs, exec_tries=0,
    )

    assert invoice_retrieve_mock.times_called == 1

    if expected_action == 'update':
        assert customer_services_mock.times_called == 1
        assert invoice_update_mock.times_called == 1
        assert invoice_clear_mock.times_called == 0
        assert mock_stq_reschedule.times_called == 0
        assert stq.eats_payments_delayed_hold.times_called == 1
    elif expected_action == 'clear':
        assert customer_services_mock.times_called == 0
        assert invoice_update_mock.times_called == 0
        assert invoice_clear_mock.times_called == 1
        assert mock_stq_reschedule.times_called == 0
        assert stq.eats_payments_delayed_hold.times_called == 0
    elif expected_action == 'reschedule':
        assert customer_services_mock.times_called == 0
        assert invoice_update_mock.times_called == 0
        assert invoice_clear_mock.times_called == 0
        assert mock_stq_reschedule.times_called == 1
        assert stq.eats_payments_delayed_hold.times_called == 0
