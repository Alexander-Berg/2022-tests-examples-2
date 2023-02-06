import pytest

from billing_fin_payouts.models.payments import payment as payment_models
from billing_fin_payouts.stq import process_payouts
from . import stq_payout_common_utils


@pytest.mark.config(BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYOUTS_ENABLED=True)
@pytest.mark.parametrize(
    """
    static_data, dry_run_flag
    """,
    [('10_static_data.json', False), ('20_static_data.json', False)],
    ids=[
        'exp_double_10. double case (case1=40 + case2=10), final result=50',
        'exp_double_20. double case (case1=40 + case2=None), final result=40',
    ],
)
async def test_60_payout_double_cases_expenses_task(
        stq3_context,
        load_json,
        static_data,
        dry_run_flag,
        interface_table='interface.expenses',
):
    """
      exp_double_10. double case (case1=40 + case2=10), final result=50
      exp_double_20. double case (case1=40 + case2=None), final result=40
    """

    pool = await stq3_context.pg.master_pool

    data_json = load_json(static_data)

    interface_list = [{interface_table: data_json['expenses1']}]
    await stq_payout_common_utils.load_data(
        pool=pool, interface_list=interface_list,
    )

    task_info = stq_payout_common_utils.build_task_info(
        dry_run=dry_run_flag,
        payment_processor=payment_models.PaymentProcessor.OEBS,
    )

    # run task 1
    await process_payouts.task(
        stq3_context,
        task_info=task_info,
        client_id='1349515601',
        payout_ready_flag=False,
    )

    interface_list = [{interface_table: data_json['expenses2']}]
    await stq_payout_common_utils.load_data(
        pool=pool, interface_list=interface_list,
    )

    # run task 2
    await process_payouts.task(
        stq3_context,
        task_info=task_info,
        client_id='1349515601',
        payout_ready_flag=True,
    )

    await stq_payout_common_utils.check_results(pool=pool, data_json=data_json)
