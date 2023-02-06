import pytest

from billing_fin_payouts.models.payments import payment as payment_models
from billing_fin_payouts.stq import process_payouts
from . import stq_payout_common_utils


@pytest.mark.now('2022-05-30T00:00:00.000000+00:00')
@pytest.mark.pgsql(dbname='billing_fin_payouts', files=('fill_tables.psql',))
@pytest.mark.config(BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYOUTS_ENABLED=True)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_ACCRUALS_PAYSYSTYPE_MAPPING={
        'by_product': {'trip_compensation': 'yandex'},
        'by_agent_id': {'agent_psb': 'psb_logist', 'agent_altocar': 'altocar'},
        'by_account_type': {'YANDEX_SERVICE': 'netting'},
    },
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYOUTS_SETTINGS_V2={
        'bulk_size': {'__default__': 100},
    },
)
@pytest.mark.parametrize(
    """
    static_data, dry_run_flag, payment_processor_value
    """,
    [('10_static_data.json', True, 'YA_BANK')],
    ids=['coupons_10.'],
)
async def test_130_coupons_in_data_open(
        stq3_context,
        load_json,
        static_data,
        dry_run_flag,
        payment_processor_value,
):
    """
        10. coupons in data_open bug fix
    """

    pool = await stq3_context.pg.master_pool

    data_json = load_json(static_data)

    task_info = stq_payout_common_utils.build_task_info(
        dry_run=dry_run_flag,
        payment_processor=payment_models.PaymentProcessor(
            payment_processor_value,
        ),
    )

    # run task
    await process_payouts.task(
        stq3_context, task_info=task_info, client_id='92057445',
    )

    await stq_payout_common_utils.check_results(pool=pool, data_json=data_json)
