# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers


@pytest.mark.parametrize(
    ['operation_id', 'operation_type'],
    [
        ('create:100500', 'create'),
        ('update:100500', 'update'),
        ('cancel:100500', 'cancel'),
        ('refund:100500', 'refund'),
        ('add_item:100500', 'add_item'),
    ],
)
@pytest.mark.config(EATS_PAYMENTS_TERMINAL_NAMES_MAPPING={'456': 'Terminal1'})
@pytest.mark.parametrize('service', ['grocery', 'eats'])
async def test_payment_metrics_operation_type(
        check_transactions_callback_task,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        operation_id,
        operation_type,
        service,
        upsert_order,
):
    upsert_order('test_order')
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
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='hold_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
        service=service,
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_payment_metrics',
            labels={'operation_type': operation_type},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            transactions=[
                helpers.make_callback_transaction(status='hold_success'),
            ],
        )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_payment_metrics',
        'currency': 'RUB',
        'payment_type': 'card',
        'error_code': 'none',
        'notification_type': 'operation_finish',
        'operation_type': operation_type,
        'transaction_status': 'hold_success',
        'service_name': service,
        'terminal_name': 'Terminal1',
    }


async def test_payment_metrics_transaction_clear(
        check_transactions_callback_task,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        experiments3,
        pgsql,
        insert_items,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        currency='RUB',
        service='eats',
        originator=consts.EDA_CORE_ORIGINATOR,
    )
    order.upsert()

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
    mock_transactions_invoice_retrieve(
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_payment_metrics',
            labels={'operation_type': 'create'},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            transactions=[
                helpers.make_callback_transaction(
                    status='clear_success', payment_type='card',
                ),
            ],
            notification_type='transaction_clear',
        )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_payment_metrics',
        'currency': 'RUB',
        'payment_type': 'card',
        'error_code': 'none',
        'notification_type': 'transaction_clear',
        'operation_type': 'create',
        'transaction_status': 'clear_success',
        'service_name': 'eats',
        'terminal_name': 'no_mapping',
    }


@pytest.mark.parametrize(
    'payment_type', ['card', 'applepay', 'googlepay', 'corp', 'badge'],
)
@pytest.mark.config(EATS_PAYMENTS_TERMINAL_NAMES_MAPPING={'456': 'Terminal1'})
async def test_payment_metrics_payment_type(
        check_transactions_callback_task,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        payment_type,
        upsert_order,
):
    upsert_order('test_order')
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
            payment_type=payment_type, items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        cleared=payment_items_list,
        payment_types=[payment_type],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type=payment_type,
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_payment_metrics',
            labels={'operation_type': 'create'},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            transactions=[
                helpers.make_callback_transaction(
                    status='hold_success', payment_type=payment_type,
                ),
            ],
        )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_payment_metrics',
        'currency': 'RUB',
        'payment_type': payment_type,
        'error_code': 'none',
        'notification_type': 'operation_finish',
        'operation_type': 'create',
        'transaction_status': 'hold_success',
        'service_name': consts.DEFAULT_SERVICE,
        'terminal_name': 'Terminal1',
    }


@pytest.mark.config(EATS_PAYMENTS_TERMINAL_NAMES_MAPPING={'456': 'Terminal1'})
async def test_payment_metrics_error_code(
        check_transactions_callback_task,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        upsert_order,
):
    upsert_order('test_order')
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
    mock_transactions_invoice_retrieve(
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
                error_reason_code='some_code',
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_payment_metrics',
            labels={'operation_type': 'create'},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            transactions=[
                helpers.make_callback_transaction(status='hold_success'),
            ],
        )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_payment_metrics',
        'currency': 'RUB',
        'payment_type': 'card',
        'error_code': 'some_code',
        'notification_type': 'operation_finish',
        'operation_type': 'create',
        'transaction_status': 'hold_success',
        'service_name': consts.DEFAULT_SERVICE,
        'terminal_name': 'Terminal1',
    }


@pytest.mark.parametrize(
    'transaction_status', consts.TRANSACTION_TERMINATE_STATUSES,
)
@pytest.mark.config(EATS_PAYMENTS_TERMINAL_NAMES_MAPPING={'456': 'Terminal1'})
async def test_payment_metrics_transaction_status(
        check_transactions_callback_task,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        transaction_status,
        upsert_order,
):
    upsert_order('test_order')
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
    mock_transactions_invoice_retrieve(
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status=transaction_status,
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_payment_metrics',
            labels={'operation_type': 'create'},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            transactions=[
                helpers.make_callback_transaction(status=transaction_status),
            ],
        )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_payment_metrics',
        'currency': 'RUB',
        'payment_type': 'card',
        'error_code': 'none',
        'notification_type': 'operation_finish',
        'operation_type': 'create',
        'transaction_status': transaction_status,
        'service_name': consts.DEFAULT_SERVICE,
        'terminal_name': 'Terminal1',
    }


async def test_no_metrics_on_repeated_task_execution(
        check_transactions_callback_task,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        testpoint,
        upsert_order,
):
    upsert_order('test_order')
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
    mock_transactions_invoice_retrieve()

    @testpoint('metrics_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_payment_metrics',
            labels={'operation_type': 'create'},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            transactions=[
                helpers.make_callback_transaction(status='clear_success'),
            ],
            exec_tries=1,
        )

    metric = collector.get_single_collected_metric()
    assert metric is None
    assert repeated_task_execution_tp.times_called == 1
