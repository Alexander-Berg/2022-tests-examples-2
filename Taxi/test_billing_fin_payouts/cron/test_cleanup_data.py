import pytest

from billing_fin_payouts.generated.cron import cron_context
from billing_fin_payouts.generated.cron import run_cron
from test_billing_fin_payouts import common_utils


@pytest.mark.now('2022-05-30T00:00:00.000000+00:00')
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_CLEANUP_ENABLED=True,
    BILLING_FIN_PAYOUTS_CLEANUP_SETTINGS={
        '__default__': {
            'enabled': False,
            'ttl_days': 1,
            'consumers': [],
            'bulk_size': 1000,
            'iterations': 3,
        },
        'payouts.accruals': {
            'enabled': True,
            'ttl_days': 1,
            'offset_days': 2,
            'consumers': [
                'billing_fin_payouts.crontasks.upload_accruals_to_arnold',
                'billing_fin_payouts.crontasks.upload_accruals_to_hahn',
                'billing_fin_payouts.crontasks.upload_accruals_to_lb',
            ],
            'bulk_size': 1,
            'iterations': 3,
        },
    },
)
@pytest.mark.parametrize(
    'cron_name, expected_data_json',
    [
        pytest.param(
            'billing_fin_payouts.crontasks.cleanup_accruals',
            'cleanup_accruals_by_ttl_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts',
                    files=['cleanup_accruals_by_ttl.psql'],
                ),
            ],
        ),
    ],
)
async def test_cleanup_accruals(
        cron_name, expected_data_json, load_json, patch, mock_yt_client,
):
    expected_data = load_json(expected_data_json)
    expected_accruals = expected_data['accruals']

    await run_cron.main([cron_name, '-t', '0'])

    context = cron_context.Context()
    await context.on_startup()
    pool = context.pg.master_pool

    await common_utils.check_pg_expected_results(
        pool=pool,
        data_expected=expected_accruals,
        query="""
                select accrual_id,
                    amount,
                    bill_num,
                    billing_contract_id,
                    client_id,
                    dry_run,
                    idempotency_key,
                    partner_currency,
                    paysys_type_cc,
                    reference_amount,
                    reference_currency,
                    service_id,
                    terminalid,
                    transaction_dt,
                    transaction_type,
                    yandex_reward,
                    created_at_utc
                from payouts.accruals
            """,
    )

    await context.on_shutdown()


@pytest.mark.now('2022-06-24T00:00:00Z')
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_CLEANUP_ENABLED=True,
    BILLING_FIN_PAYOUTS_CLEANUP_SETTINGS={
        '__default__': {
            'enabled': False,
            'ttl_days': 1,
            'consumers': [],
            'bulk_size': 1000,
            'iterations': 3,
        },
        'payouts.payout_batches': {
            'enabled': True,
            'ttl_days': 1,
            'offset_days': 2,
            'consumers': [
                (
                    'billing_fin_payouts.crontasks.'
                    'upload_payout_ready_batches_to_arnold'
                ),
                (
                    'billing_fin_payouts.crontasks.'
                    'upload_payout_ready_batches_to_hahn'
                ),
                (
                    'billing_fin_payouts.crontasks.'
                    'upload_export_batches_to_arnold'
                ),
                'billing_fin_payouts.crontasks.upload_export_batches_to_hahn',
            ],
            'bulk_size': 1,
            'iterations': 3,
        },
    },
)
@pytest.mark.parametrize(
    'cron_name, expected_data_json',
    [
        pytest.param(
            'billing_fin_payouts.crontasks.cleanup_export_batches',
            'cleanup_batches_by_ttl_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts',
                    files=['cleanup_batches_by_ttl.psql'],
                ),
            ],
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.cleanup_export_batches',
            'cleanup_batches_by_consumer_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts',
                    files=['cleanup_batches_by_consumer.psql'],
                ),
            ],
        ),
    ],
)
async def test_cleanup_batches(
        cron_name, expected_data_json, load_json, patch, mock_yt_client,
):
    expected_data = load_json(expected_data_json)
    expected_payout_batch = expected_data['payout_batch']
    expected_batch_change_log = expected_data['batch_change_log']

    await run_cron.main([cron_name, '-t', '0'])

    context = cron_context.Context()
    await context.on_startup()
    pool = context.pg.master_pool

    # check payout_batches
    await common_utils.check_pg_expected_results(
        pool=pool,
        data_expected=expected_payout_batch,
        query="""
                select batch_id as payout_batch_id,
                       type_code,
                       status_code,
                       client_id,
                       contract_id,
                       firm_id,
                       contract_type,
                       currency,
                       person_id,
                       amount_w_vat::text as amount_w_vat
                  from payouts.payout_batches
            """,
    )

    # check batch change log
    await common_utils.check_pg_expected_results(
        pool=pool,
        data_expected=expected_batch_change_log,
        query="""
                select
                    batch_id,
                    batch_status_code,
                    idempotency_key
                from payouts.batch_change_log
            """,
    )

    await context.on_shutdown()


@pytest.mark.now('2022-06-25T00:00:00Z')
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_CLEANUP_ENABLED=True,
    BILLING_FIN_PAYOUTS_CLEANUP_SETTINGS={
        '__default__': {
            'enabled': False,
            'ttl_days': 1,
            'consumers': [],
            'bulk_size': 1000,
            'iterations': 3,
        },
        'payouts.data_closed': {
            'enabled': True,
            'ttl_days': 1,
            'offset_days': 2,
            'consumers': [
                (
                    'billing_fin_payouts.crontasks.'
                    'upload_export_batches_data_to_arnold'
                ),
                (
                    'billing_fin_payouts.crontasks.'
                    'upload_export_batches_data_to_hahn'
                ),
            ],
            'bulk_size': 1,
            'iterations': 3,
        },
    },
)
@pytest.mark.parametrize(
    'cron_name, expected_data_json',
    [
        pytest.param(
            'billing_fin_payouts.crontasks.cleanup_batches_data',
            'cleanup_batches_data_by_ttl_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts',
                    files=['cleanup_batches_data_by_ttl.psql'],
                ),
            ],
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.cleanup_batches_data',
            'cleanup_batches_data_by_consumer_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts',
                    files=['cleanup_batches_data_by_consumer.psql'],
                ),
            ],
        ),
    ],
)
async def test_cleanup_batches_data(
        cron_name, expected_data_json, load_json, patch, mock_yt_client,
):
    expected_data = load_json(expected_data_json)
    expected_data_closed = expected_data['data_closed']

    await run_cron.main([cron_name, '-t', '0'])

    context = cron_context.Context()
    await context.on_startup()
    pool = context.pg.master_pool

    # check data_closed
    await common_utils.check_pg_expected_results(
        pool=pool,
        data_expected=expected_data_closed,
        query="""
                select payout_batch_id,
                       transaction_id,
                       branch_type,
                       amount_w_vat::text as amount_w_vat,
                       amount_w_vat_applied::text as amount_w_vat_applied,
                       amount_w_vat_saldo::text as amount_w_vat_saldo,
                       payload
                  from payouts.data_closed
            """,
    )

    await context.on_shutdown()


@pytest.mark.config(
    BILLING_FIN_PAYOUTS_CLEANUP_ENABLED=True,
    BILLING_FIN_PAYOUTS_CLEANUP_SETTINGS={
        '__default__': {
            'enabled': False,
            'ttl_days': 1,
            'consumers': [],
            'bulk_size': 1000,
            'iterations': 3,
        },
        'interface.expenses': {
            'enabled': True,
            'ttl_days': 1,
            'bulk_size': 1000,
            'iterations': 3,
            'consumers': [
                'billing_fin_payouts.crontasks.'
                'upload_interface_expenses_to_arnold',
                'billing_fin_payouts.crontasks.'
                'upload_interface_expenses_to_hahn',
            ],
        },
        'interface.payments': {
            'enabled': True,
            'ttl_days': 1,
            'bulk_size': 1000,
            'iterations': 3,
            'consumers': [
                'billing_fin_payouts.crontasks.'
                'upload_interface_payments_to_arnold',
                'billing_fin_payouts.crontasks.'
                'upload_interface_payments_to_hahn',
            ],
        },
        'interface.revenues': {
            'enabled': True,
            'ttl_days': 1,
            'bulk_size': 1000,
            'iterations': 3,
            'consumers': [
                'billing_fin_payouts.crontasks.'
                'upload_interface_revenues_to_arnold',
                'billing_fin_payouts.crontasks.'
                'upload_interface_revenues_to_hahn',
            ],
        },
    },
)
@pytest.mark.parametrize(
    'cron_name, expected_data_json',
    [
        pytest.param(
            'billing_fin_payouts.crontasks.cleanup_interface_expenses',
            'cleanup_interface_expenses_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts',
                    files=['interface_expenses.psql', 'consumer_cursors.psql'],
                ),
            ],
            id='cleanup_interface_expenses',
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.cleanup_interface_payments',
            'cleanup_interface_payments_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts',
                    files=['interface_payments.psql', 'consumer_cursors.psql'],
                ),
            ],
            id='cleanup_interface_payments',
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.cleanup_interface_revenues',
            'cleanup_interface_revenues_expected.json',
            marks=[
                pytest.mark.pgsql(
                    'billing_fin_payouts',
                    files=['interface_revenues.psql', 'consumer_cursors.psql'],
                ),
            ],
            id='cleanup_interface_revenues',
        ),
    ],
)
@pytest.mark.now('2022-03-23T09:00:00.000000+03:00')
async def test_cleanup_interface_tables(
        cron_name, expected_data_json, load_json,
):
    expected_data = load_json(expected_data_json)
    table_name = expected_data['table_name']
    expected_interface_table = expected_data['expected_interface_table']

    await run_cron.main([cron_name, '-t', '0'])
    context = cron_context.Context()
    await context.on_startup()
    pool = context.pg.master_pool

    # check interface table
    await common_utils.check_pg_expected_results(
        pool=pool,
        data_expected=expected_interface_table,
        query=f"""
            select
                id,
                created_at_utc,
                transaction_id,
                accounting_date,
                client_id,
                contract_id,
                currency,
                amount_tlog,
                amount,
                row_index,
                payload,
                status_code
            from {table_name}
            """,
    )

    await context.on_shutdown()
