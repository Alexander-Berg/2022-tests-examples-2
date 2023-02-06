import pytest

from taxi_billing_tlog import pgaas
from taxi_billing_tlog import yt
from taxi_billing_tlog.crontasks import upload_to_yt
from taxi_billing_tlog.yt import converters
from taxi_billing_tlog.yt import eats_schemas
from taxi_billing_tlog.yt import grocery_schemas
from taxi_billing_tlog.yt import schemas


@pytest.mark.now('2019-08-05T12:00:00')
@pytest.mark.config(
    BILLING_TLOG_UPLOAD_TO_YT_ENABLED=True,
    BILLING_TLOG_UPLOAD_TO_YT_MAX_ITERATIONS=5,
    # Actually defined in journal_json
    BILLING_TLOG_UPLOAD_TO_YT_BATCH_SIZE=50000,
    BILLING_TLOG_YT_COLUMNS_FILTERS={
        'revenues': {'contract_id': {'from_date': '2020-06-25'}},
        'expenses': {'contract_id': {'from_date': '2020-06-25'}},
    },
    BILLING_TLOG_UPLOAD_TO_YT_RESTRICTED_PERIODS=[
        {'start': '13:00', 'end': '15:00'},
    ],
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
        'order': {'payment': 1, 'refund': -1},
        'coupon': {'payment': -1, 'refund': 1},
        'client_b2b_trip_payment': {'payment': 1, 'refund': -1},
        'driver_workshift': {'payment': 1, 'refund': -1},
        'card_trips_agency_commission': {'payment': 1, 'refund': -1},
        'card_trips_acquiring_commission': {'payment': 1, 'refund': -1},
        'food_payment': {'payment': 1, 'refund': -1},
        'subsidy': {'payment': -1, 'refund': 1},
    },
)
@pytest.mark.parametrize(
    'always_optimize_for_scan',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                BILLING_TLOG_UPLOAD_TO_YT_OPTIMIZE_FOR_SCAN_JOURNALS={},
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                BILLING_TLOG_UPLOAD_TO_YT_OPTIMIZE_FOR_SCAN_JOURNALS=[
                    'journal_folder',
                ],
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'journal_json,'
    'expected_data_json,'
    'row_filter_cls,'
    'row_converter_cls,'
    'yt_schema_cls',
    [
        (
            'journal.json',
            'revenues.json',
            pgaas.RevenuesRowFilter,
            converters.RevenuesRowConverter,
            schemas.RevenuesYtSchema,
        ),
        (
            'journal.json',
            'expenses.json',
            pgaas.ExpensesRowFilter,
            converters.ExpensesRowConverter,
            schemas.ExpensesYtSchema,
        ),
        (
            'payments_journal.json',
            'payments.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            schemas.PaymentsYtSchema,
        ),
        (
            'cashback_journal.json',
            'cashback.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            schemas.CashbackYtSchema,
        ),
        (
            'antifraud_check_journal.json',
            'antifraud_check.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            schemas.AntifraudCheckYtSchema,
        ),
        (
            'payment_requests_journal.json',
            'payment_requests.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            schemas.PaymentRequestsYtSchema,
        ),
        (
            'grocery_agent_journal.json',
            'expected_grocery_agent.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            grocery_schemas.GroceryAgentYtSchema,
        ),
        (
            'grocery_revenues_journal.json',
            'expected_grocery_revenues.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            grocery_schemas.GroceryRevenuesYtSchema,
        ),
        (
            'eats_revenues_journal.json',
            'expected_eats_revenues.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            eats_schemas.EatsRevenuesYtSchema,
        ),
        (
            'eats_expenses_journal.json',
            'expected_eats_expenses.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            eats_schemas.EatsExpensesYtSchema,
        ),
        (
            'eats_agent_journal.json',
            'expected_eats_agent.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            eats_schemas.EatsAgentYtSchema,
        ),
        (
            'eats_payments_journal.json',
            'expected_eats_payments.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            eats_schemas.EatsPaymentsYtSchema,
        ),
    ],
)
@pytest.mark.nofilldb
async def test_upload_to_yt(
        patch,
        cron_context,
        mock_psycopg2,
        mock_yt_client,
        load_json,
        journal_json,
        expected_data_json,
        row_filter_cls,
        row_converter_cls,
        yt_schema_cls,
        always_optimize_for_scan,
):
    # pylint: disable=R0914
    journals = load_json(journal_json)
    expected_data = load_json(expected_data_json)

    expected_yt_entries = expected_data['yt_entries']
    expected_yt_create_calls = expected_data['yt_create_calls']
    expected_yt_set_calls = expected_data['yt_set_calls']
    expected_yt_mkdir_calls = expected_data['yt_mkdir_calls']
    expected_yt_exists_calls = expected_data['yt_exists_calls']
    expected_yt_lock_calls = expected_data['yt_lock_calls']

    mock_psycopg2.fetchone_results = journals['max_ids']
    mock_psycopg2.fetchall_results = journals['entries']

    created_yt_clients = []

    # pylint: disable=unused-variable
    @patch('taxi_billing_tlog.crontasks.upload_to_yt.get_yt_client')
    def get_yt_client(context, cluster_name):
        result = mock_yt_client(cluster_name)
        nonlocal created_yt_clients
        created_yt_clients.append(result)
        return result

    upload_to_yt.upload(
        context=cron_context,
        cluster=yt.Cluster(
            name='test_cluster',
            journal_folder='journal_folder',
            schema=yt_schema_cls(cron_context),
        ),
        row_filter=row_filter_cls(),
        row_converter=row_converter_cls(context=cron_context),
        consumer_id='test_consumer_id',
        journal_table='journal',
        log_extra={},
    )

    assert len(created_yt_clients) == 1
    yt_client = created_yt_clients[0]
    assert yt_client.cluster_name == 'test_cluster'

    assert yt_client.exists_calls == expected_yt_exists_calls
    assert yt_client.mkdir_calls == expected_yt_mkdir_calls
    assert yt_client.create_calls == expected_yt_create_calls
    assert yt_client.write_table_calls == expected_yt_entries
    assert yt_client.set_calls == expected_yt_set_calls
    assert yt_client.lock_calls == expected_yt_lock_calls
    assert yt_client.create_calls_optimize_for_scan == always_optimize_for_scan
