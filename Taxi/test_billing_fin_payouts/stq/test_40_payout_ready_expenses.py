import pytest

from billing_fin_payouts.models.payments import payment as payment_models
from billing_fin_payouts.stq import process_payouts
from . import stq_payout_common_utils


@pytest.mark.config(BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYOUTS_ENABLED=True)
@pytest.mark.parametrize(
    """
    static_data, dry_run_flag
    """,
    [
        ('10_static_data.json', False),
        ('20_static_data.json', False),
        ('30_static_data.json', False),
        ('40_static_data.json', False),
    ],
    ids=[
        'expenses_10. payment 20+80, refund 60, result payout = 40',
        'expenses_20. payment 20+80, refund 100, result payout = 0',
        'expenses_30. payment 20+80, refund 70+30, result payout = 0',
        'expenses_40. payment 20+80, refund 130, result payout = -30',
    ],
)
async def test_40_payout_ready_expenses_task(
        stq3_context,
        load_json,
        static_data,
        dry_run_flag,
        interface_table='interface.expenses',
):
    """
        10. payment 20+80, refund 60, result payout = 40
        20. payment 20+80, refund 100, result payout = 0
        30. payment 20+80, refund 70+30, result payout = 0
        40. payment 20+80, refund 130, result payout = -30
    """

    pool = await stq3_context.pg.master_pool

    data_json = load_json(static_data)
    interface_list = [{interface_table: data_json['expenses']}]

    await stq_payout_common_utils.load_data(
        pool=pool, interface_list=interface_list,
    )

    task_info = stq_payout_common_utils.build_task_info(
        dry_run=dry_run_flag,
        payment_processor=payment_models.PaymentProcessor.OEBS,
    )

    # run task
    await process_payouts.task(
        stq3_context,
        task_info=task_info,
        client_id='1349515601',
        payout_ready_flag=True,
    )

    await stq_payout_common_utils.check_results(pool=pool, data_json=data_json)
