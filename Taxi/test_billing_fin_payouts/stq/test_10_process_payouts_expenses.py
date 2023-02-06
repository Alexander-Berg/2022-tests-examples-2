import pytest

from billing_fin_payouts.models.payments import payment as payment_models
from billing_fin_payouts.stq import process_payouts
from . import stq_payout_common_utils


@pytest.mark.config(BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYOUTS_ENABLED=True)
@pytest.mark.parametrize(
    """
    static_data
    """,
    [
        '10_static_data.json',
        '20_static_data.json',
        '30_static_data.json',
        '40_static_data.json',
        '50_static_data.json',
        '60_static_data.json',
        '70_static_data.json',
    ],
    ids=[
        'expenses_10_payment_more_than_refund_part_dry_run',
        'expenses_20_payment_equal_refund',
        'expenses_30_payment_equal_refund',
        'expenses_40_payment_less_than_refund',
        'expenses_50_refund_only',
        'expenses_60_payment_only',
        'expenses_70_without_payment_and_without_refund',
    ],
)
async def test_10_process_payouts_expenses_task(
        stq3_context,
        load_json,
        static_data,
        interface_table='interface.expenses',
):
    """
        10. payment dry_20+80, refund 60, result payout = 20
        20. payment 20+80, refund 100, result payout = 0
        30. payment 20+80, refund 70+30, result payout = 0
        40. payment 20+80, refund 130, result payout = -30
        50. payment None, refund 130, result payout = -130
        60. payment 20+80, refund None, result payout = 100
        70. payment None, refund None, result payout = None
    """

    pool = await stq3_context.pg.master_pool

    data_json = load_json(static_data)
    interface_list = [{interface_table: data_json['expenses']}]

    await stq_payout_common_utils.load_data(
        pool=pool, interface_list=interface_list,
    )
    task_info = stq_payout_common_utils.build_task_info(
        dry_run=False, payment_processor=payment_models.PaymentProcessor.OEBS,
    )
    # run task
    await process_payouts.task(
        stq3_context, task_info=task_info, client_id='1349515601',
    )

    await stq_payout_common_utils.check_results(pool=pool, data_json=data_json)
