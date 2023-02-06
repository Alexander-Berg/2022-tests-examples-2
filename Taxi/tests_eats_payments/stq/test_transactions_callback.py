# pylint: disable=import-error
# pylint: disable=too-many-lines
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers

NOW = '2020-08-14T14:39:50.265+00:00'

TEST_FEATURE_FLAGS = {
    'transactions_callback_reschedules': {
        'description': 'rescheduling of transactions callback',
        'enabled': True,
    },
}


@pytest.mark.parametrize('is_need_new_revision_service', [True, False])
async def test_purchase_billing_callback_v2(
        stq_runner,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        check_billing_callback,
        assert_db_order,
        upsert_order,
        is_need_new_revision_service,
        experiments3,
):
    experiments3.add_experiment(
        **helpers.make_new_service_revision(is_need_new_revision_service),
    )
    upsert_order('test_order', api_version=2)
    assert_db_order('test_order', expected_api_version=2)

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products-1',
            name='big_mac',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            balance_client_id='123456789',
            details={
                'composition_products': [
                    {
                        'id': 'product-1',
                        'name': 'Product 1',
                        'cost_for_customer': '5.00',
                        'type': 'product',
                    },
                    {
                        'id': 'option-1',
                        'name': 'Option 1',
                        'cost_for_customer': '3.00',
                        'type': 'option',
                    },
                    {
                        'id': 'product-2',
                        'name': 'Product 2',
                        'cost_for_customer': '2.00',
                        'type': 'product',
                    },
                ],
                'discriminator_type': 'composition_products_details',
            },
        ),
        helpers.make_customer_service(
            customer_service_id='delivery',
            name='Delivery',
            cost_for_customer='3.00',
            currency='RUB',
            customer_service_type='delivery',
            vat='nds_20',
            trust_product_id='eda-product-id',
            place_id='place_1',
            balance_client_id='987654321',
        ),
    ]
    customer_services_mock = mock_order_revision_customer_services_details(
        customer_services=customer_services, expected_revision_id='100500',
    )

    transaction_1 = helpers.make_transaction(
        operation_id='create:123456:100500',
        status='clear_success',
        sum=[
            {'amount': '10.00', 'item_id': 'composition-products-1'},
            {'amount': '3.00', 'item_id': 'delivery'},
        ],
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[transaction_1],
        operations=[helpers.make_operation(id='create:123456:100500')],
    )

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'create:123456:100500',
        'operation_status': 'done',
        'notification_type': 'transaction_clear',
        'transactions': [transaction_1],
    }
    await stq_runner.eats_payments_transactions_callback.call(
        task_id=f'test_order:create:123456:100500:done:transaction_clear',
        kwargs=kwargs,
        exec_tries=0,
    )

    check_billing_callback(
        task_id='test_order/create:123456:100500/payment/'
        'c964a582b3b4b3dcd514ab1914a7d2a8',
        order_id='test_order',
        transaction_type='payment',
        event_at='2020-08-14T14:39:50.265+00:00',
        payment_type='card',
        currency='RUB',
        items=[
            {
                'item_id': 'composition-products-1',
                'place_id': 'place_1',
                'balance_client_id': '123456789',
                'amount': '10.00',
                'item_type': 'product',
            },
            {
                'item_id': 'delivery',
                'place_id': 'place_1',
                'balance_client_id': '987654321',
                'amount': '3.00',
                'item_type': 'delivery',
            },
        ],
        terminal_id='57000176',
        external_payment_id='c964a582b3b4b3dcd514ab1914a7d2a8',
    )

    assert customer_services_mock.times_called == 1
    assert invoice_retrieve_mock.times_called == 1


async def test_service_fee_callback_v2_billing(
        stq_runner,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        check_billing_callback,
        assert_db_order,
        upsert_order,
):
    upsert_order('test_order', api_version=2)
    assert_db_order('test_order', expected_api_version=2)

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='service-fee-1',
            name='Service Fee',
            cost_for_customer='9.00',
            currency='RUB',
            customer_service_type='service_fee',
            vat='nds_20',
            trust_product_id='service_fee-id',
            place_id='place_1',
        ),
    ]
    customer_services_mock = mock_order_revision_customer_services_details(
        customer_services=customer_services, expected_revision_id='100500',
    )

    transaction_1 = helpers.make_transaction(
        operation_id='create:123456:100500',
        status='clear_success',
        sum=[{'amount': '9.00', 'item_id': 'service-fee-1'}],
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[transaction_1],
        operations=[helpers.make_operation(id='create:123456:100500')],
    )

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'create:123456:100500',
        'operation_status': 'done',
        'notification_type': 'transaction_clear',
        'transactions': [transaction_1],
    }
    await stq_runner.eats_payments_transactions_callback.call(
        task_id=f'test_order:create:123456:100500:done:transaction_clear',
        kwargs=kwargs,
        exec_tries=0,
    )

    check_billing_callback(
        task_id='test_order/create:123456:100500/payment/'
        'c964a582b3b4b3dcd514ab1914a7d2a8',
        order_id='test_order',
        transaction_type='payment',
        event_at='2020-08-14T14:39:50.265+00:00',
        payment_type='card',
        currency='RUB',
        items=[
            {
                'item_id': 'service-fee-1',
                'place_id': 'place_1',
                'balance_client_id': '95332016',
                'amount': '9.00',
                'item_type': 'service_fee',
            },
        ],
        terminal_id='57000176',
        external_payment_id='c964a582b3b4b3dcd514ab1914a7d2a8',
    )

    assert customer_services_mock.times_called == 1
    assert invoice_retrieve_mock.times_called == 1


async def test_refund_billing_callback_v2(
        stq_runner,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        check_billing_callback,
        assert_db_order,
        upsert_order,
):
    upsert_order('test_order', api_version=2)
    assert_db_order('test_order', expected_api_version=2)

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products-1',
            name='big_mac',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            balance_client_id='123456789',
            details=helpers.make_customer_service_details(
                composition_products=[
                    helpers.make_composition_product(
                        composition_product_id='product-1',
                        name='Product 1',
                        cost_for_customer='5.00',
                        composition_product_type='product',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-1',
                        name='Option 1',
                        cost_for_customer='3.00',
                        composition_product_type='option',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 2',
                        cost_for_customer='2.00',
                        composition_product_type='product',
                    ),
                ],
                refunds=[
                    helpers.make_composition_product_refund(
                        refund_revision_id='55555',
                        refund_products=[
                            {'id': 'product-2', 'refunded_amount': '2.00'},
                            {'id': 'option-1', 'refunded_amount': '3.00'},
                        ],
                    ),
                    helpers.make_composition_product_refund(
                        refund_revision_id='refund:444',
                        refund_products=[
                            {'id': 'product-1', 'refunded_amount': '5.00'},
                        ],
                    ),
                ],
            ),
        ),
        helpers.make_customer_service(
            customer_service_id='delivery',
            name='Delivery',
            cost_for_customer='3.00',
            currency='RUB',
            customer_service_type='delivery',
            vat='nds_20',
            trust_product_id='eda-product-id',
            place_id='place_1',
            balance_client_id='987654321',
        ),
    ]
    customer_services_mock = mock_order_revision_customer_services_details(
        customer_services=customer_services,
    )

    transaction_1 = helpers.make_transaction(
        operation_id='refund:100500',
        status='clear_success',
        sum=[
            {'amount': '10.00', 'item_id': 'composition-products-1'},
            {'amount': '3.00', 'item_id': 'delivery'},
        ],
        refunds=[
            helpers.make_refund(
                refund_sum=[
                    helpers.make_transactions_item(
                        item_id='composition-products-1',
                        amount='5.00',
                        fiscal_receipt_info={
                            'personal_tin_id': 'personal-tin-id',
                            'title': 'Big Mac Burger',
                            'vat': 'nds_20',
                        },
                    ),
                ],
                operation_id='refund:55555',
            ),
        ],
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[transaction_1],
        operations=[helpers.make_operation(id='create:100500')],
    )

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'refund:55555',
        'operation_status': 'done',
        'notification_type': 'operation_finish',
        'transactions': [transaction_1],
    }
    await stq_runner.eats_payments_transactions_callback.call(
        task_id=f'test_order:refund:55555:done:operation_finish',
        kwargs=kwargs,
        exec_tries=0,
    )

    check_billing_callback(
        task_id='test_order/refund:55555/refund/'
        'c964a582b3b4b3dcd514ab1914a7d2a8',
        order_id='test_order',
        transaction_type='refund',
        event_at='2020-08-14T14:39:50.265+00:00',
        payment_type='card',
        currency='RUB',
        items=[
            {
                'item_id': 'composition-products-1',
                'place_id': 'place_1',
                'balance_client_id': '123456789',
                'amount': '5.00',
                'item_type': 'product',
            },
        ],
        terminal_id='57000176',
        external_payment_id='c964a582b3b4b3dcd514ab1914a7d2a8',
    )

    assert customer_services_mock.times_called == 1
    assert invoice_retrieve_mock.times_called == 1


@pytest.mark.parametrize(
    (
        'operation_id',
        'operation_status',
        'expected_metric_value',
        'invoice_retrieve_expected_times_called',
        'invoice_clear_expected_times_called',
        'debt_collector_times_called',
    ),
    [
        pytest.param(
            'update:unhold:test_order:123456',
            'done',
            {'hold_unhold_stage': 'update_unhold', 'is_success': '1'},
            1,
            0,
            0,
            id='Unhold is done',
        ),
        pytest.param(
            'update:unhold:test_order:123456',
            'failed',
            {'hold_unhold_stage': 'update_unhold', 'is_success': '0'},
            1,
            0,
            0,
            id='Unhold is failed',
        ),
        pytest.param(
            'update:hold:test_order:123456',
            'done',
            {'hold_unhold_stage': 'update_hold', 'is_success': '1'},
            1,
            1,
            1,
            id='Hold is done',
        ),
        pytest.param(
            'update:hold:test_order:123456',
            'failed',
            {'hold_unhold_stage': 'update_hold', 'is_success': '0'},
            1,
            1,
            1,
            id='Hold failed',
        ),
    ],
)
async def test_hold_unhold(
        stq_runner,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_clear,
        operation_id,
        operation_status,
        expected_metric_value,
        invoice_retrieve_expected_times_called,
        invoice_clear_expected_times_called,
        debt_collector_times_called,
        upsert_order,
        experiments3,
        upsert_debt_status,
        mock_eats_debt_user_scoring_verdict,
        mock_debt_collector_by_ids,
        mock_debt_collector_update_invoice,
        mock_order_revision_list,
        mock_transactions_invoice_update,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve()
    invoice_clear_mock = mock_transactions_invoice_clear()
    upsert_order(
        order_id='test_order',
        api_version=2,
        business_type='restaurant',
        business_specification='{}',
        service='eats',
    )
    experiments3.add_config(**helpers.make_debt_collector_experiment(True))
    mock_order_revision_list()
    upsert_debt_status(order_id='test_order', debt_status='updated')
    mock_eats_debt_user_scoring_verdict(verdict='accept')
    mock_debt_collector_by_ids(
        debts=[helpers.make_debt(reason_code='hold_unhold')],
    )
    mock_transactions_invoice_update()
    mock_debt_update = mock_debt_collector_update_invoice()

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': operation_id,
        'operation_status': operation_status,
        'notification_type': 'operation_finish',
        'transactions': [],
    }

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_hold_unhold_metrics',
            labels={},
    ) as collector:
        await stq_runner.eats_payments_transactions_callback.call(
            task_id=f'test_order:{operation_id}:{operation_status}:'
            f'operation_finish',
            kwargs=kwargs,
            exec_tries=0,
        )

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_hold_unhold_metrics',
        'hold_unhold_stage': expected_metric_value['hold_unhold_stage'],
        'is_success': expected_metric_value['is_success'],
        'currency': 'RUB',
        'payment_type': 'card',
        'service_name': 'eats',
    }

    assert (
        invoice_retrieve_mock.times_called
        == invoice_retrieve_expected_times_called
    )
    assert (
        invoice_clear_mock.times_called == invoice_clear_expected_times_called
    )
    assert mock_debt_update.times_called == debt_collector_times_called


@pytest.mark.parametrize(
    'technical_error', [pytest.param(False), pytest.param(True)],
)
async def test_technical_debt(
        stq,
        taxi_eats_payments_monitor,
        mock_eats_debt_user_scoring,
        mock_transactions_invoice_retrieve,
        insert_items,
        experiments3,
        stq_runner,
        technical_error,
        upsert_order,
        upsert_order_payment,
):
    upsert_order('test_order')
    upsert_order_payment(
        'test_order',
        '27affbc7-de68-4a79-abba-d9bdf48e6e09',
        'card',
        'RUB',
        True,
    )
    experiments3.add_experiment(
        **helpers.make_debt_technical_error_experiment(),
    )

    operation_id = 'create:100500'
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
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
        technical_error=technical_error,
        error_reason_code='trust2host.couldnt_connect_timeout',
    )

    transaction_2 = helpers.make_transaction(
        external_payment_id='external_payment_id_2',
        status='clear_success',
        operation_id=operation_id,
        payment_type='personal_wallet',
        terminal_id='456',
        sum=transactions_items,
    )

    mock_transactions_invoice_retrieve(
        cleared=payment_items_list,
        transactions=[transaction_1, transaction_2],
    )

    mock_eats_debt_user_scoring(allow_credit=True)

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'create:55555',
        'operation_status': 'failed',
        'notification_type': 'operation_finish',
        'transactions': [transaction_1, transaction_2],
    }

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_technical_debt_metrics',
            labels={},
    ) as collector:
        await stq_runner.eats_payments_transactions_callback.call(
            task_id=f'test_order:create:55555:done:transaction_clear',
            kwargs=kwargs,
            exec_tries=0,
        )

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_technical_debt_metrics',
        'error': 'trust2host.couldnt_connect_timeout',
        'is_experiment_decision': '1',
        'is_credit_allowed': '1',
    }

    helpers.check_callback_mock(
        callback_mock=stq.eda_order_processing_payment_events_callback,
        times_called=1,
        task_id='test_order:debt',
        queue='eda_order_processing_payment_events_callback',
        **{
            'order_id': 'test_order',
            'action': 'debt',
            'status': 'confirmed',
            'revision': 'test_order',
            'meta': [{'discriminator': 'debt_type', 'value': 'auto'}],
        },
    )


@pytest.mark.parametrize('operation_type', ['create', 'update'])
@pytest.mark.parametrize('allow_empty_transactions', [False, True])
async def test_empty_transactions(
        stq,
        taxi_eats_payments_monitor,
        mock_eats_debt_user_scoring,
        mock_transactions_invoice_retrieve,
        insert_items,
        experiments3,
        stq_runner,
        upsert_order,
        upsert_order_payment,
        operation_type,
        allow_empty_transactions,
        taxi_config,
):
    taxi_config.set_values(
        {
            'EATS_PAYMENTS_FEATURE_FLAGS': {
                'invoice_with_empty_transactions_could_be_treated_as_debt': {
                    'description': '',
                    'enabled': allow_empty_transactions,
                },
            },
        },
    )
    upsert_order('test_order')
    upsert_order_payment(
        'test_order',
        '27affbc7-de68-4a79-abba-d9bdf48e6e09',
        'card',
        'RUB',
        True,
    )
    experiments3.add_experiment(
        **helpers.make_debt_technical_error_experiment(),
    )

    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
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

    mock_transactions_invoice_retrieve(
        cleared=payment_items_list, transactions=[],
    )

    mock_eats_debt_user_scoring(allow_credit=True)

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': f'{operation_type}:55555',
        'operation_status': 'failed',
        'notification_type': 'operation_finish',
        'transactions': [],
    }

    await stq_runner.eats_payments_transactions_callback.call(
        task_id=f'test_order:{operation_type}:55555:failed:transaction_clear',
        kwargs=kwargs,
        exec_tries=0,
    )

    if operation_type == 'create':
        if allow_empty_transactions:
            helpers.check_callback_mock(
                callback_mock=stq.eda_order_processing_payment_events_callback,
                times_called=1,
                task_id='test_order:debt',
                queue='eda_order_processing_payment_events_callback',
                **{
                    'order_id': 'test_order',
                    'action': 'debt',
                    'status': 'confirmed',
                    'revision': 'test_order',
                    'meta': [{'discriminator': 'debt_type', 'value': 'auto'}],
                },
            )
        else:
            helpers.check_callback_mock(
                callback_mock=stq.eda_order_processing_payment_events_callback,
                times_called=1,
                task_id='test_order:create:55555:failed:transaction_clear',
                queue='eda_order_processing_payment_events_callback',
                **{
                    'order_id': 'test_order',
                    'action': 'purchase',
                    'status': 'rejected',
                    'revision': '55555',
                },
            )


@pytest.mark.config(EATS_PAYMENTS_FEATURE_FLAGS=TEST_FEATURE_FLAGS)
async def test_personal_wallet_payment_rescheduling_older_tasks(
        testpoint,
        stq,
        stq_runner,
        mock_transactions_invoice_retrieve,
        assert_db_order,
        pgsql,
        upsert_order,
        insert_operations,
):
    order_nr = 'test_order'
    upsert_order(order_nr, api_version=2)
    assert_db_order(order_nr, expected_api_version=2)
    cursor = pgsql['eats_payments'].cursor()
    fetch_tasks_query = (
        f'SELECT task_id, order_nr, version '
        f'FROM eats_payments.transactions_callback_rescheduled_tasks '
        f'WHERE order_nr = \'{order_nr}\' ORDER by version DESC'
    )

    @testpoint('send_notifications')
    def send_notifications(data):
        pass

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'create:123456:100500',
        'operation_status': 'done',
        'notification_type': 'transaction_clear',
        'transactions': [],
    }

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        file_to_load='retrieve_invoice_sbp.json', commit_version=1,
    )
    await stq_runner.eats_payments_transactions_callback.call(
        task_id='first_task', kwargs=kwargs, exec_tries=0,
    )
    assert send_notifications.times_called == 0
    assert invoice_retrieve_mock.times_called == 1

    cursor.execute(fetch_tasks_query)
    stored_task = cursor.fetchall()
    assert len(stored_task) == 1
    assert stored_task[0][0] == 'first_task'
    assert stored_task[0][2] == 1
    assert (
        stq.eats_payments_transactions_callback_rescheduled.times_called == 1
    )
    task_info = stq.eats_payments_transactions_callback_rescheduled.next_call()
    assert task_info['id'] == 'first_task'

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        file_to_load='retrieve_invoice_sbp.json', commit_version=2,
    )
    await stq_runner.eats_payments_transactions_callback.call(
        task_id='second_task', kwargs=kwargs, exec_tries=0,
    )

    assert send_notifications.times_called == 0
    assert invoice_retrieve_mock.times_called == 1
    cursor.execute(fetch_tasks_query)
    stored_tasks = cursor.fetchall()
    assert len(stored_tasks) == 2
    assert stored_tasks[0][0] == 'second_task'
    assert stored_tasks[0][2] == 2
    assert (
        stq.eats_payments_transactions_callback_rescheduled.times_called == 1
    )
    task_info = stq.eats_payments_transactions_callback_rescheduled.next_call()
    assert task_info['id'] == 'second_task'

    cursor.execute(fetch_tasks_query)
    stored_tasks = cursor.fetchall()

    print(stored_tasks)
    await stq_runner.eats_payments_transactions_callback_rescheduled.call(
        task_id='second_task', kwargs=kwargs, exec_tries=0,
    )
    assert send_notifications.times_called == 0
    insert_operations(3, order_nr, 'close', 'update1', 'close')
    await stq_runner.eats_payments_transactions_callback_rescheduled.call(
        task_id='second_task', kwargs=kwargs, exec_tries=0,
    )
    assert send_notifications.times_called == 0
    await stq_runner.eats_payments_transactions_callback_rescheduled.call(
        task_id='first_task', kwargs=kwargs, exec_tries=0,
    )
    assert send_notifications.times_called == 1
    await stq_runner.eats_payments_transactions_callback_rescheduled.call(
        task_id='second_task', kwargs=kwargs, exec_tries=0,
    )
    assert send_notifications.times_called == 2
    cursor.execute(fetch_tasks_query)
    stored_tasks = cursor.fetchall()
    assert not stored_tasks


@pytest.mark.config(EATS_PAYMENTS_FEATURE_FLAGS=TEST_FEATURE_FLAGS)
async def test_dont_send_notifications_for_canceled_sbp(
        testpoint,
        stq,
        stq_runner,
        mock_transactions_invoice_retrieve,
        assert_db_order,
        upsert_order,
        insert_operations,
):
    order_nr = 'test_order'
    upsert_order(order_nr, api_version=2)
    assert_db_order(order_nr, expected_api_version=2)

    @testpoint('send_notifications')
    def send_notifications(data):
        pass

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'create:123456:100500',
        'operation_status': 'done',
        'notification_type': 'transaction_clear',
        'transactions': [],
    }

    mock_transactions_invoice_retrieve(
        file_to_load='retrieve_invoice_sbp.json', commit_version=2,
    )

    await stq_runner.eats_payments_transactions_callback_rescheduled.call(
        task_id='task', kwargs=kwargs, exec_tries=0,
    )
    assert send_notifications.times_called == 0
    insert_operations(3, order_nr, 'Null', 'Null', 'cancel')
    await stq_runner.eats_payments_transactions_callback_rescheduled.call(
        task_id='task', kwargs=kwargs, exec_tries=0,
    )
    assert send_notifications.times_called == 0


@pytest.mark.parametrize(
    'transaction_operation_status, '
    'expected_operation_status, '
    'expected_fails_count, '
    'use_fallback, invoice_update_times_called',
    [
        pytest.param(
            'failed',
            'failed',
            1,
            False,
            0,
            id='Create is failed. No fallback',
        ),
        pytest.param(
            'failed', 'in_progress', 1, True, 1, id='Create is failed. Retry',
        ),
        pytest.param('done', 'done', 0, False, 0, id='Create is ok'),
    ],
)
async def test_execute_create_operation(
        stq,
        stq_runner,
        experiments3,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        assert_db_order,
        insert_operation,
        fetch_operation,
        upsert_order,
        upsert_order_payment,
        transaction_operation_status,
        expected_operation_status,
        expected_fails_count,
        use_fallback,
        invoice_update_times_called,
):
    upsert_order('test_order', api_version=2)
    assert_db_order('test_order', expected_api_version=2)

    upsert_order_payment(
        'test_order',
        '27affbc7-de68-4a79-abba-d9bdf48e6e09',
        'card',
        'RUB',
        True,
    )

    insert_operation(
        'test_order', '123456', '123456', 'create', 'in_progress', 0,
    )
    fetch_operation('test_order', '123456')

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products-1',
            name='big_mac',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            balance_client_id='123456789',
        ),
        helpers.make_customer_service(
            customer_service_id='delivery',
            name='Delivery',
            cost_for_customer='3.00',
            currency='RUB',
            customer_service_type='delivery',
            vat='nds_20',
            trust_product_id='eda-product-id',
            place_id='place_1',
            balance_client_id='987654321',
        ),
    ]
    mock_order_revision_customer_services(customer_services=customer_services)

    customer_services_details = [
        helpers.make_customer_service(
            customer_service_id='composition-products-1',
            name='big_mac',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            balance_client_id='123456789',
            details=helpers.make_customer_service_details(
                composition_products=[
                    helpers.make_composition_product(
                        composition_product_id='product-1',
                        name='Product 1',
                        cost_for_customer='5.00',
                        composition_product_type='product',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-1',
                        name='Option 1',
                        cost_for_customer='3.00',
                        composition_product_type='option',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 2',
                        cost_for_customer='2.00',
                        composition_product_type='product',
                    ),
                ],
                refunds=[
                    helpers.make_composition_product_refund(
                        refund_revision_id='55555',
                        refund_products=[
                            {'id': 'product-2', 'refunded_amount': '2.00'},
                            {'id': 'option-1', 'refunded_amount': '3.00'},
                        ],
                    ),
                    helpers.make_composition_product_refund(
                        refund_revision_id='refund:444',
                        refund_products=[
                            {'id': 'product-1', 'refunded_amount': '5.00'},
                        ],
                    ),
                ],
            ),
        ),
        helpers.make_customer_service(
            customer_service_id='delivery',
            name='Delivery',
            cost_for_customer='3.00',
            currency='RUB',
            customer_service_type='delivery',
            vat='nds_20',
            trust_product_id='eda-product-id',
            place_id='place_1',
            balance_client_id='987654321',
        ),
    ]
    mock_order_revision_customer_services_details(
        customer_services=customer_services_details,
    )

    mock_transactions_invoice_retrieve(
        file_to_load='retrieve_invoice_create_is_failed.json',
    )

    experiments3.add_config(**helpers.make_operations_config())
    if use_fallback:
        experiments3.add_config(**helpers.make_payment_fallback())

    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(
                item_id='composition-products-1',
                amount='10.00',
                product_id='burger',
            ),
            helpers.make_transactions_item(
                item_id='delivery', amount='3.00', product_id='eda-product-id',
            ),
        ],
    )
    pass_params = {
        'terminal_route_data': {'preferred_processing_cc': 'test_dummy_name'},
    }
    transaction_payload = {
        'payment_fallback': {'fallback_name': 'test_fallback'},
    }
    invoice_update_mock = mock_transactions_invoice_update(
        operation_id='create:1:123456',
        items=[transactions_items],
        pass_params=pass_params,
        transaction_payload=transaction_payload,
    )

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'create:123456',
        'operation_status': transaction_operation_status,
        'notification_type': 'operation_finish',
        'transactions': [],
    }
    await stq_runner.eats_payments_transactions_callback.call(
        task_id=f'test_order:create:123456:failed:operation_finish',
        kwargs=kwargs,
        exec_tries=0,
    )

    if expected_operation_status == 'fail':
        helpers.check_callback_mock(
            callback_mock=stq.eats_payments_operations,
            times_called=1,
            task_id='test_order:1:1',
            queue='eats_payments_operations',
        )

    fetch_operation(
        'test_order',
        '123456',
        '123456',
        expected_operation_status,
        expected_fails_count,
    )

    assert invoice_update_mock.times_called == invoice_update_times_called


@pytest.mark.parametrize(
    'operation_type, operation_id, transaction_operation_status, '
    'expected_operation_status, notification_type, '
    'expected_fails_count',
    [
        pytest.param(
            'close',
            'create:123456',
            'done',
            'done',
            'transaction_clear',
            0,
            id='Close is ok',
        ),
        pytest.param(
            'update',
            'update:123456',
            'done',
            'done',
            'operation_finish',
            0,
            id='Update is ok',
        ),
        pytest.param(
            'refund',
            'refund:123456',
            'done',
            'done',
            'operation_finish',
            0,
            id='Refund is ok',
        ),
    ],
)
async def test_execute_operations(
        stq,
        stq_runner,
        experiments3,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        assert_db_order,
        insert_operation,
        fetch_operation,
        upsert_order,
        operation_type,
        operation_id,
        transaction_operation_status,
        expected_operation_status,
        notification_type,
        expected_fails_count,
):
    upsert_order('test_order', api_version=2)
    assert_db_order('test_order', expected_api_version=2)

    insert_operation(
        'test_order', '123456', '123456', operation_type, 'in_progress', 0,
    )
    fetch_operation('test_order', '123456')

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            balance_client_id='123456789',
            details=helpers.make_customer_service_details(
                composition_products=[
                    helpers.make_composition_product(
                        composition_product_id='product-1',
                        name='Product 1',
                        cost_for_customer='5.00',
                        composition_product_type='product',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-1',
                        name='Option 1',
                        cost_for_customer='3.00',
                        composition_product_type='option',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 2',
                        cost_for_customer='2.00',
                        composition_product_type='product',
                    ),
                ],
                refunds=[
                    helpers.make_composition_product_refund(
                        refund_revision_id='55555',
                        refund_products=[
                            {'id': 'product-2', 'refunded_amount': '2.00'},
                            {'id': 'option-1', 'refunded_amount': '3.00'},
                        ],
                    ),
                    helpers.make_composition_product_refund(
                        refund_revision_id='refund:444',
                        refund_products=[
                            {'id': 'product-1', 'refunded_amount': '5.00'},
                        ],
                    ),
                ],
            ),
        ),
        helpers.make_customer_service(
            customer_service_id='delivery',
            name='Delivery',
            cost_for_customer='3.00',
            currency='RUB',
            customer_service_type='delivery',
            vat='nds_20',
            trust_product_id='eda-product-id',
            place_id='place_1',
            balance_client_id='987654321',
        ),
    ]
    mock_order_revision_customer_services_details(
        customer_services=customer_services,
    )

    mock_transactions_invoice_retrieve(
        file_to_load='retrieve_invoice_paid_by_personal_wallet.json',
    )

    experiments3.add_config(**helpers.make_operations_config())

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': operation_id,
        'operation_status': transaction_operation_status,
        'notification_type': notification_type,
        'transactions': [],
    }
    await stq_runner.eats_payments_transactions_callback.call(
        task_id=f'test_order:create:123456:100500:failed:transaction_clear',
        kwargs=kwargs,
        exec_tries=0,
    )

    fetch_operation(
        'test_order',
        '123456',
        None,
        expected_operation_status,
        expected_fails_count,
    )
