# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers


OPERATION_ID = 'create:100500'
PERSONAL_WALLET_TYPE = 'personal_wallet'

HOLD_SUCCESS = 'hold_success'
HOLD_FAILED = 'hold_fail'

CLEAR_SUCCESS = 'clear_success'
CLEAR_FAIL = 'clear_fail'

EDA_STATUS_OK = 'confirmed'
EDA_STATUS_FAIL = 'rejected'


@pytest.mark.parametrize(
    [
        'operation_id',
        'action',
        'callback_times_called',
        'expect_fail',
        'collect_metrics',
    ],
    [
        ('create:100500', 'purchase', 1, False, True),
        ('update:100500', 'update', 1, False, True),
        ('cancel:100500', 'cancel', 1, False, True),
        ('refund:100500', 'refund', 1, False, True),
        ('add_item:100500', 'add_item', 1, False, True),
        ('a:100500', None, 0, True, False),
        ('foo', None, 0, True, False),
    ],
)
@pytest.mark.parametrize('service', ['grocery', 'eats'])
async def test_ei_offline_orders_processing_notification_operation_type(
        check_transactions_callback_task,
        check_ei_offline_orders_callback,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        operation_id,
        action,
        callback_times_called,
        expect_fail,
        collect_metrics,
        service,
        upsert_order,
):
    upsert_order(
        'test_order', originator=consts.INTEGRATION_OFFLINE_ORDERS_ORIGINATOR,
    )
    insert_items([helpers.make_db_row(item_id='big_mac')])
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[helpers.make_transaction(operation_id=operation_id)],
        service=service,
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='ei_offline_orders_eats_payments_callback_metrics',
            labels={'action': action},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            expect_fail=expect_fail,
            transactions=[
                helpers.make_callback_transaction(status='clear_success'),
            ],
        )

    check_ei_offline_orders_callback(
        order_id='test_order',
        action=action,
        status='confirmed',
        revision='100500',
        times_called=callback_times_called,
    )

    assert invoice_retrieve_mock.times_called == 1

    metric = collector.get_single_collected_metric()

    if collect_metrics:
        assert metric.value == 1
        assert metric.labels == {
            'action': action,
            'currency': 'RUB',
            'payment_type': 'card',
            'sensor': 'ei_offline_orders_eats_payments_callback_metrics',
            'status': 'confirmed',
            'service_name': service,
        }
    else:
        assert metric is None


@pytest.mark.parametrize(
    ['operation_status', 'status'],
    [('done', 'confirmed'), ('failed', 'rejected')],
)
async def test_ei_offline_orders_processing_notification(
        check_transactions_callback_task,
        check_ei_offline_orders_callback,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        status,
        operation_status,
        upsert_order,
):
    upsert_order(
        'test_order', originator=consts.INTEGRATION_OFFLINE_ORDERS_ORIGINATOR,
    )
    insert_items([helpers.make_db_row(item_id='big_mac')])
    operation_id = 'create:100500'
    invoice_retrieve_mock = mock_transactions_invoice_retrieve()
    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='ei_offline_orders_eats_payments_callback_metrics',
            labels={'action': 'purchase', 'status': status},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            transactions=[],
            operation_status=operation_status,
        )

    check_ei_offline_orders_callback(
        order_id='test_order',
        action='purchase',
        status=status,
        revision='100500',
    )

    assert invoice_retrieve_mock.times_called == 1

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'action': 'purchase',
        'currency': 'RUB',
        'payment_type': 'card',
        'sensor': 'ei_offline_orders_eats_payments_callback_metrics',
        'status': status,
        'service_name': consts.DEFAULT_SERVICE,
    }


@pytest.mark.parametrize(
    [
        'operation_status',
        'status',
        'callback_times_called',
        'metrics_collected',
    ],
    [('done', 'confirmed', 1, True), ('failed', 'rejected', 1, True)],
)
async def test_ei_offline_orders_notification_operation_status_no_transaction(
        check_transactions_callback_task,
        taxi_eats_payments_monitor,
        check_ei_offline_orders_callback,
        mock_transactions_invoice_retrieve,
        insert_items,
        operation_status,
        status,
        callback_times_called,
        metrics_collected,
        upsert_order,
):
    upsert_order(
        'test_order', originator=consts.INTEGRATION_OFFLINE_ORDERS_ORIGINATOR,
    )
    insert_items([helpers.make_db_row(item_id='big_mac')])
    operation_id = 'create:100500'
    invoice_retrieve_mock = mock_transactions_invoice_retrieve()

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='ei_offline_orders_eats_payments_callback_metrics',
            labels={'action': 'purchase', 'status': status},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            operation_status=operation_status,
            transactions=[],
        )

    check_ei_offline_orders_callback(
        order_id='test_order',
        action='purchase',
        status=status,
        revision='100500',
        times_called=callback_times_called,
    )

    assert invoice_retrieve_mock.times_called == 1

    metric = collector.get_single_collected_metric()
    if metrics_collected:
        assert metric.labels == {
            'sensor': 'ei_offline_orders_eats_payments_callback_metrics',
            'action': 'purchase',
            'currency': 'RUB',
            'payment_type': 'card',
            'status': status,
            'service_name': consts.DEFAULT_SERVICE,
        }
        assert metric.value == 1
    else:
        assert metric is None


@pytest.mark.parametrize(
    'operation_status, status',
    [('done', EDA_STATUS_OK), ('failed', EDA_STATUS_FAIL)],
)
async def test_callback_after_hold_composite_operation(
        check_transactions_callback_task,
        taxi_eats_payments_monitor,
        check_ei_offline_orders_callback,
        mock_transactions_invoice_retrieve,
        operation_status,
        status,
        upsert_order,
):
    upsert_order(
        'test_order', originator=consts.INTEGRATION_OFFLINE_ORDERS_ORIGINATOR,
    )
    primary_transaction_id = 'primary-id'
    complement_transaction_id = 'complement-id'

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                operation_id=OPERATION_ID,
                status=HOLD_SUCCESS,
                external_payment_id=primary_transaction_id,
            ),
            helpers.make_transaction(
                operation_id=OPERATION_ID,
                status=CLEAR_SUCCESS,
                external_payment_id=complement_transaction_id,
                payment_type=PERSONAL_WALLET_TYPE,
            ),
        ],
        payment_types=['card', PERSONAL_WALLET_TYPE],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='ei_offline_orders_eats_payments_callback_metrics',
            labels={'action': 'purchase', 'status': status},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=OPERATION_ID,
            transactions=[],
            operation_status=operation_status,
        )

    check_ei_offline_orders_callback(
        order_id='test_order',
        action='purchase',
        status=status,
        revision='100500',
    )

    assert invoice_retrieve_mock.times_called == 1

    if status is not None:
        assert collector.collected_metrics == [
            metrics_helpers.Metric(
                labels={
                    'sensor': (
                        'ei_offline_orders_eats_payments_callback_metrics'
                    ),
                    'action': 'purchase',
                    'currency': 'RUB',
                    'payment_type': 'card',
                    'status': status,
                    'service_name': consts.DEFAULT_SERVICE,
                },
                value=1,
            ),
            metrics_helpers.Metric(
                labels={
                    'sensor': (
                        'ei_offline_orders_eats_payments_callback_metrics'
                    ),
                    'action': 'purchase',
                    'currency': 'RUB',
                    'payment_type': PERSONAL_WALLET_TYPE,
                    'status': status,
                    'service_name': consts.DEFAULT_SERVICE,
                },
                value=1,
            ),
        ]
    else:
        assert not collector.collected_metrics


async def test_no_metrics_on_repeated_task_execution(
        check_transactions_callback_task,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        testpoint,
        upsert_order,
):
    upsert_order(
        'test_order', originator=consts.INTEGRATION_OFFLINE_ORDERS_ORIGINATOR,
    )
    insert_items([helpers.make_db_row(item_id='big_mac')])
    operation_id = 'create:100500'
    mock_transactions_invoice_retrieve(transactions=[])

    @testpoint('ei_offline_orders_notification_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='ei_offline_orders_eats_payments_callback_metrics',
            labels={'action': 'purchase', 'status': 'confirmed'},
    ) as collector:
        await check_transactions_callback_task(
            operation_id=operation_id,
            operation_status='done',
            transactions=[],
            exec_tries=1,
        )

    metric = collector.get_single_collected_metric()
    assert metric is None
    assert repeated_task_execution_tp.times_called == 1


@pytest.mark.parametrize(
    'notification_type, callback_times_called',
    [('transaction_clear', 0), ('operation_finish', 1)],
)
async def test_ignore_not_operation_finish(
        check_transactions_callback_task,
        check_ei_offline_orders_callback,
        mock_transactions_invoice_retrieve,
        experiments3,
        pgsql,
        notification_type,
        callback_times_called,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        currency='RUB',
        service='eats',
        originator=consts.INTEGRATION_OFFLINE_ORDERS_ORIGINATOR,
    )
    order.upsert()
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                operation_id=OPERATION_ID, status='clear_success',
            ),
            helpers.make_transaction(
                operation_id=OPERATION_ID,
                status='clear_success',
                payment_type=PERSONAL_WALLET_TYPE,
            ),
        ],
        payment_types=['card', PERSONAL_WALLET_TYPE],
    )

    await check_transactions_callback_task(
        operation_id=OPERATION_ID,
        notification_type=notification_type,
        transactions=[],
    )

    check_ei_offline_orders_callback(
        order_id='test_order',
        action='purchase',
        status=EDA_STATUS_OK,
        revision='100500',
        times_called=callback_times_called,
    )

    assert invoice_retrieve_mock.times_called == 1


async def test_retrieve_failed(
        check_transactions_callback_task,
        check_ei_offline_orders_callback,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        mockserver,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        error=mockserver.TimeoutError(),
    )
    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='ei_offline_orders_eats_payments_callback_metrics',
            labels={'action': 'purchase'},
    ) as collector:
        await check_transactions_callback_task(
            operation_id='create:100500', expect_fail=True,
        )

    check_ei_offline_orders_callback(times_called=0)
    assert invoice_retrieve_mock.times_called == 1

    metric = collector.get_single_collected_metric()

    assert metric is None
