# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers


@pytest.mark.parametrize(
    'debt_status, debt_collector_calls',
    [
        pytest.param('created', 1, id='Happy path'),
        pytest.param('updated', 0, id='Debt already updated'),
    ],
)
async def test_technical_debt(
        stq,
        experiments3,
        upsert_order,
        insert_items,
        upsert_order_payment,
        upsert_debt_status,
        mock_eats_debt_user_scoring,
        stq_runner,
        mock_order_revision_list,
        mock_transactions_invoice_update,
        mock_transactions_invoice_retrieve,
        mock_debt_collector_update_invoice,
        mock_debt_collector_by_ids,
        debt_status,
        debt_collector_calls,
        taxi_eats_payments_monitor,
):
    upsert_order(
        order_id='test_order', business_type=consts.BUSINESS, api_version=2,
    )
    upsert_order_payment(
        'test_order',
        '27affbc7-de68-4a79-abba-d9bdf48e6e09',
        'card',
        'RUB',
        True,
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
    experiments3.add_experiment(
        **helpers.make_debt_technical_error_experiment(),
    )
    experiments3.add_config(**helpers.make_debt_collector_experiment(True))
    mock_eats_debt_user_scoring(allow_credit=True)
    mock_order_revision_list()
    mock_transactions_invoice_update(operation_id='cancel:abcd')

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

    upsert_debt_status(order_id='test_order', debt_status=debt_status)

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
        technical_error=True,
        error_reason_code='trust2host.couldnt_connect_timeout',
    )

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'create:55555',
        'operation_status': 'failed',
        'notification_type': 'operation_finish',
        'transactions': [transaction_1],
    }

    mock_transactions_invoice_retrieve(
        cleared=payment_items_list, transactions=[transaction_1],
    )

    mock_debt_collector = mock_debt_collector_update_invoice()
    debts = [helpers.make_debt(reason_code='technical_debt')]
    mock_debt_collector_by_ids(debts=debts)

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_debt_collector_metrics',
            labels={'debt_type': 'technical_debt'},
    ) as collector:
        await stq_runner.eats_payments_transactions_callback.call(
            task_id=f'test_order:create:55555', kwargs=kwargs, exec_tries=0,
        )

    metric = collector.get_single_collected_metric()
    if debt_collector_calls:
        assert metric.value == 1
        assert metric.labels == {
            'sensor': 'eats_payments_debt_collector_metrics',
            'debt_type': 'technical_debt',
        }

    if debt_collector_calls > 0:
        helpers.check_callback_mock(
            callback_mock=stq.eda_order_processing_payment_events_callback,
            times_called=1,
            task_id='test_order:create:55555',
            queue='eda_order_processing_payment_events_callback',
            **{
                'order_id': 'test_order',
                'action': 'purchase',
                'status': 'confirmed',
                'revision': 'test_order',
            },
        )

    assert mock_debt_collector.times_called == debt_collector_calls


NOW = '2020-08-12T07:20:00+00:00'

OPERATION_ID = 'create:100500'

TRANSACTIONS_ITEMS = [
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


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    [
        'transactions',
        'debt_status',
        'debt_collector_calls',
        'allow_empty_transactions',
    ],
    [
        pytest.param(
            [
                helpers.make_transaction(
                    external_payment_id='external_payment_id_1',
                    status='hold_pending',
                    operation_id=OPERATION_ID,
                    payment_type='card',
                    terminal_id='456',
                    sum=TRANSACTIONS_ITEMS,
                ),
            ],
            'created',
            1,
            False,
            id='Base case',
        ),
        pytest.param(
            [], 'created', 1, True, id='Invoice without transactions',
        ),
        pytest.param(
            [],
            'created',
            0,
            False,
            id='Invoice without transactions and without debt',
        ),
        pytest.param([], 'updated', 0, False, id='Debt already updated'),
    ],
)
async def test_auto_debt(
        stq,
        experiments3,
        upsert_order,
        insert_items,
        upsert_debt_status,
        mock_eats_debt_user_scoring,
        stq_runner,
        mock_transactions_invoice_retrieve,
        mock_debt_collector_update_invoice,
        mock_debt_collector_by_ids,
        transactions,
        debt_status,
        debt_collector_calls,
        mock_order_revision_list,
        mock_transactions_invoice_update,
        taxi_config,
        allow_empty_transactions,
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
    upsert_order(
        order_id='test_order', business_type=consts.BUSINESS, api_version=2,
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
    experiments3.add_experiment(
        **helpers.make_debt_technical_error_experiment(),
    )
    experiments3.add_config(**helpers.make_debt_collector_experiment(True))
    mock_eats_debt_user_scoring(allow_credit=True)
    mock_order_revision_list()
    mock_transactions_invoice_update(operation_id='cancel:abcd')

    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=TRANSACTIONS_ITEMS,
        ),
    ]

    upsert_debt_status(order_id='test_order', debt_status=debt_status)

    kwargs = {'invoice_id': 'test_order', 'ttl': '2020-08-13T07:20:00+00:00'}

    mock_transactions_invoice_retrieve(
        cleared=payment_items_list,
        transactions=transactions,
        status='holding',
    )

    mock_debt_collector = mock_debt_collector_update_invoice()
    debts = [helpers.make_debt(reason_code='technical_debt')]
    mock_debt_collector_by_ids(debts=debts)

    await stq_runner.eats_payments_debt_check_invoice_status.call(
        task_id=f'test_order:create:55555', kwargs=kwargs, exec_tries=0,
    )

    if debt_collector_calls > 0:
        helpers.check_callback_mock(
            callback_mock=stq.eda_order_processing_payment_events_callback,
            times_called=1,
            task_id='test_order:create:55555',
            queue='eda_order_processing_payment_events_callback',
            **{
                'order_id': 'test_order',
                'action': 'purchase',
                'status': 'confirmed',
                'revision': 'test_order',
            },
        )

    assert mock_debt_collector.times_called == debt_collector_calls
