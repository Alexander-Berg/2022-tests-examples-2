import pytest

from test_payments_eda import common
from test_payments_eda import consts as test_consts
from test_payments_eda.stq import consts as stq_consts


# pylint: disable=invalid-name
parametrize_metrics_enabled = pytest.mark.parametrize(
    'metrics_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=False,
            ),
        ),
    ],
)


@parametrize_metrics_enabled
@pytest.mark.parametrize(
    'operation_id, invoice_status, action',
    [
        ('create:123', 'held', 'confirm'),
        ('create:123', 'hold-failed', 'reject'),
        ('change:123', 'held', 'item_change'),
        # TODO: add failures to metrics
        ('change:123', 'hold-failed', 'item_change'),
        ('change:123', 'cleared', 'item_change'),
        # TODO: add failures to metrics
        ('change:123', 'clear-failed', 'item_change'),
    ],
)
@pytest.mark.parametrize(
    'invoice_retrieve_extra, transaction_extra, user_data, extra_labels',
    [
        pytest.param({}, {}, {}, {}, id='Invoice with no extras'),
        # not sure if this situation is possible though
        pytest.param(
            {},
            {'payment_type': None},
            {},
            {'payment_type': 'unknown'},
            id='Transaction without payment type',
        ),
        pytest.param(
            {'service': None},
            {},
            {},
            {'invoice_service': 'unknown'},
            id='Invoice with no `service`',
        ),
        pytest.param(
            {
                'external_user_info': {
                    'user_id': test_consts.DEFAULT_USER_ID,
                    'origin': test_consts.USER_ORIGIN_TAXI,
                },
            },
            {},
            {'id': test_consts.DEFAULT_USER_ID, 'application': 'android'},
            {'user_application': 'android'},
            id='Invoice with `external_user_info`'
            ' with `origin=taxi` in `invoice`',
        ),
        pytest.param(
            {
                'external_user_info': {
                    'user_id': test_consts.DEFAULT_USER_ID,
                    'origin': 'foo',
                },
            },
            {},
            {'id': test_consts.DEFAULT_USER_ID, 'application': 'android'},
            {'user_application': 'unknown'},
            id='Invoice with `external_user_info`'
            ' with non-taxi origin in `invoice`',
        ),
    ],
)
async def test_send_main_metrics(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        get_single_stat_by_label_values,
        stq3_context,
        operation_id,
        invoice_status,
        action,
        metrics_enabled,
        invoice_retrieve_extra,
        transaction_extra,
        user_data,
        extra_labels,
):
    invoice_retrieve_extra = {
        'transactions': [
            {
                **stq_consts.TRANSACTION,
                'operation_id': operation_id,
                **transaction_extra,
            },
        ],
        **invoice_retrieve_extra,
    }
    mock_invoice_retrieve(status=invoice_status, **invoice_retrieve_extra)
    mock_user_api(user_data=user_data)
    mock_eda_event()
    await invoke_callback_task(operation_id=operation_id)
    expected_labels = {
        'sensor': 'callback_notify_metric',
        'error_code': 'none',
        'currency': 'RUB',
        'payment_type': 'card',
        'invoice_service': 'eats',
        'user_application': 'unknown',
        'action': action,
        **extra_labels,
    }
    expected_stat = common.make_stat(expected_labels)
    stat = get_single_stat_by_label_values(
        stq3_context, {'sensor': 'callback_notify_metric'},
    )
    if metrics_enabled:
        assert stat == expected_stat
    else:
        assert stat is None


@parametrize_metrics_enabled
@pytest.mark.parametrize(
    'transaction_status, error_code',
    [
        ('clear_init', 'unknown'),
        ('clear_pending', 'unknown'),
        ('clear_success', 'none'),
        ('clear_fail', 'transaction_clear_fail'),
    ],
)
async def test_send_main_metrics_payment_action(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        get_single_stat_by_label_values,
        stq3_context,
        metrics_enabled,
        transaction_status,
        error_code,
):
    mock_invoice_retrieve(status='cleared')
    mock_user_api()
    mock_eda_event()
    await invoke_callback_task(operation_id='clear', status=transaction_status)
    expected_labels = {
        'sensor': 'callback_notify_metric',
        'error_code': error_code,
        'currency': 'RUB',
        'payment_type': 'unknown',
        'invoice_service': 'eats',
        'user_application': 'unknown',
        'action': 'payment',
    }
    expected_stat = common.make_stat(expected_labels)
    stat = get_single_stat_by_label_values(
        stq3_context, {'sensor': 'callback_notify_metric'},
    )
    if metrics_enabled:
        assert stat == expected_stat
    else:
        assert stat is None


@parametrize_metrics_enabled
@pytest.mark.parametrize(
    'transaction_extra,extra_labels',
    [
        pytest.param(
            {'no_error_reason_code': ''},
            {'error_code': 'none'},
            id='Invoice with transaction with wrong error reason code',
        ),
        pytest.param(
            {'error_reason_code': 'processing_error'},
            {'error_code': 'processing_error'},
            id='Invoice with transaction with proper error reason code',
        ),
    ],
)
async def test_send_main_metrics_error(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        get_single_stat_by_label_values,
        stq3_context,
        metrics_enabled,
        transaction_extra,
        extra_labels,
):
    operation_id = 'create:123'
    invoice_retrieve_extra = {
        'transactions': [
            {
                **stq_consts.TRANSACTION,
                'operation_id': operation_id,
                **transaction_extra,
            },
        ],
    }
    mock_invoice_retrieve(status='hold-failed', **invoice_retrieve_extra)
    mock_user_api()
    mock_eda_event()
    await invoke_callback_task(operation_id=operation_id)
    expected_labels = {
        'sensor': 'callback_notify_metric',
        'error_code': 'none',
        'currency': 'RUB',
        'payment_type': 'card',
        'invoice_service': 'eats',
        'user_application': 'unknown',
        'action': 'reject',
        **extra_labels,
    }
    expected_stat = common.make_stat(expected_labels)
    stat = get_single_stat_by_label_values(
        stq3_context, {'sensor': 'callback_notify_metric'},
    )
    if metrics_enabled:
        assert stat == expected_stat
    else:
        assert stat is None


# TODO: unify testing for common labels
# TODO: separate test for operation_id format
@pytest.mark.config(PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True)
@pytest.mark.parametrize(
    [
        'operation_id',
        'invoice_extra',
        'transaction_extra',
        'extra_labels',
        'metrics_collected',
    ],
    [
        pytest.param(
            'change:123:tips',
            {},
            {},
            {},
            True,
            id='Invoice with `change_source`=tips and no extra',
        ),
        # not sure if this situation is possible though
        pytest.param(
            'change:123:tips',
            {},
            {'payment_type': None},
            {'payment_type': 'unknown'},
            True,
            id='Transaction without payment type',
        ),
        pytest.param(
            'change:123:tips',
            {'service': None},
            {},
            {'invoice_service': 'unknown'},
            True,
            id='Invoice with no `service`',
        ),
        pytest.param(
            'change:123:tips',
            {},
            {'error_reason_code': 'processing_error'},
            {'error_code': 'processing_error'},
            True,
            id='Invoice with tips and error',
        ),
        pytest.param(
            'change:123:tips',
            {},
            {'error_reason_code': 'processing_error'},
            {'error_code': 'processing_error'},
            True,
            id='Invoice with tips and error',
        ),
        pytest.param(
            'change:123:admin',
            {},
            {},
            {},
            False,
            id='Invoice with `change_source`=admin',
        ),
        pytest.param(
            'create:123',
            {},
            {},
            {},
            False,
            id='Invoice with no `change_source`',
        ),
    ],
)
async def test_send_tips_metrics(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        get_single_stat_by_label_values,
        stq3_context,
        operation_id,
        invoice_extra,
        transaction_extra,
        extra_labels,
        metrics_collected,
):
    invoice_retrieve_extra = {
        'transactions': [
            {
                **stq_consts.TRANSACTION,
                'operation_id': operation_id,
                **transaction_extra,
            },
        ],
        **invoice_extra,
    }
    mock_invoice_retrieve(status='cleared', **invoice_retrieve_extra)
    mock_user_api()
    mock_eda_event()
    await invoke_callback_task(operation_id=operation_id)
    expected_labels = {
        'sensor': 'callback_notify_metric.tips',
        'error_code': 'none',
        'currency': 'RUB',
        'payment_type': 'card',
        'invoice_service': 'eats',
        'user_application': 'unknown',
        **extra_labels,
    }
    expected_stat = common.make_stat(expected_labels)
    stat = get_single_stat_by_label_values(
        stq3_context, {'sensor': 'callback_notify_metric.tips'},
    )
    if metrics_collected:
        assert stat == expected_stat
    else:
        assert stat is None


@pytest.mark.config(PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True)
@pytest.mark.parametrize(
    'task_retries,metrics_collected', [(0, True), (1, False), (6, False)],
)
async def test_metrics_not_collected_on_task_retry(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        get_single_stat_by_label_values,
        stq3_context,
        task_retries,
        metrics_collected,
):
    operation_id = 'create:123'
    invoice_retrieve_extra = {
        'transactions': [
            {**stq_consts.TRANSACTION, 'operation_id': operation_id},
        ],
    }
    mock_invoice_retrieve(status='held', **invoice_retrieve_extra)
    mock_user_api()
    mock_eda_event()
    await invoke_callback_task(
        operation_id=operation_id, task_exec_retries=task_retries,
    )
    stat = get_single_stat_by_label_values(
        stq3_context, {'sensor': 'callback_notify_metric'},
    )
    if metrics_collected:
        assert stat is not None
    else:
        assert stat is None


@pytest.mark.config(PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True)
@pytest.mark.parametrize(
    'transaction_extra,totals_type',
    [({}, 'success'), ({'error_reason_code': 'processing_error'}, 'error')],
)
async def test_send_statuses_metrics(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        get_stats_by_label_values,
        stq3_context,
        transaction_extra,
        totals_type,
):
    operation_id = 'create:123'
    invoice_retrieve_extra = {
        'transactions': [
            {
                **stq_consts.TRANSACTION,
                'operation_id': operation_id,
                **transaction_extra,
            },
        ],
    }
    mock_invoice_retrieve(status='hold-failed', **invoice_retrieve_extra)
    mock_user_api()
    mock_eda_event()
    expected_labels = [
        {
            'sensor': 'callback_notify_metric.statuses',
            'type': totals_type,
            'payment_type': 'card',
            'invoice_service': 'eats',
            'user_application': 'unknown',
        },
        {
            'sensor': 'callback_notify_metric.statuses',
            'type': 'total',
            'payment_type': 'card',
            'invoice_service': 'eats',
            'user_application': 'unknown',
        },
    ]
    expected_stats = [common.make_stat(labels) for labels in expected_labels]
    await invoke_callback_task(operation_id=operation_id)
    stats = get_stats_by_label_values(
        stq3_context, {'sensor': 'callback_notify_metric.statuses'},
    )
    assert stats == expected_stats


@pytest.mark.config(PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True)
@pytest.mark.parametrize(
    'transaction_extra,totals_type',
    [({}, 'success'), ({'error_reason_code': 'processing_error'}, 'error')],
)
async def test_send_total_statuses_metrics(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        get_stats_by_label_values,
        stq3_context,
        transaction_extra,
        totals_type,
):
    operation_id = 'create:123'
    invoice_retrieve_extra = {
        'transactions': [
            {
                **stq_consts.TRANSACTION,
                'operation_id': operation_id,
                **transaction_extra,
            },
        ],
    }
    mock_invoice_retrieve(status='hold-failed', **invoice_retrieve_extra)
    mock_user_api()
    mock_eda_event()
    expected_labels = [
        {
            'sensor': 'callback_notify_metric.total_statuses',
            'type': totals_type,
        },
        {'sensor': 'callback_notify_metric.total_statuses', 'type': 'total'},
    ]
    expected_stats = [common.make_stat(labels) for labels in expected_labels]
    await invoke_callback_task(operation_id=operation_id)
    stats = get_stats_by_label_values(
        stq3_context, {'sensor': 'callback_notify_metric.total_statuses'},
    )
    assert stats == expected_stats
