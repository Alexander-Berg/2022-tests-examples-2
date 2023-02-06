import pytest

from billing_fin_payouts.models.payments import payment as payment_models
from billing_fin_payouts.stq import process_payouts
from . import stq_payout_common_utils


@pytest.mark.config(BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYOUTS_ENABLED=True)
@pytest.mark.parametrize(
    """
    static_data, dry_run_flag
    """,
    [('10_static_data.json', False), ('20_static_data.json', True)],
    ids=[
        'skip_payout_10_payment_more_than_refund',
        'skip_payout_20_payment_more_than_refund_DRY',
    ],
)
async def test_20_process_payouts_nett_skip_task(
        stq3_context,
        load_json,
        static_data,
        dry_run_flag,
        interface_table='interface.revenues',
):
    """
        10. payment & refund of service_id = 650 (SKIP_PAYOUT) and payment
        20. payment & refund of service_id = 650 (SKIP_PAYOUT) and payment DRY
    """

    pool = await stq3_context.pg.master_pool

    data_json = load_json(static_data)
    interface_list = [{interface_table: data_json['revenues']}]

    await stq_payout_common_utils.load_data(
        pool=pool, interface_list=interface_list,
    )

    task_info = stq_payout_common_utils.build_task_info(
        dry_run=dry_run_flag,
        payment_processor=payment_models.PaymentProcessor.OEBS,
    )
    # run task
    await process_payouts.task(
        stq3_context, task_info=task_info, client_id='1349515601',
    )

    await stq_payout_common_utils.check_results(pool=pool, data_json=data_json)
