import pytest

from billing_fin_payouts.models.payments import payment as payment_models
from billing_fin_payouts.stq import process_payouts
from . import stq_payout_common_utils


@pytest.mark.now('2022-05-30T00:00:00.000000+00:00')
@pytest.mark.config(BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYOUTS_ENABLED=True)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_ACCRUALS_PAYSYSTYPE_MAPPING={
        'by_product': {'trip_compensation': 'yandex'},
        'by_agent_id': {'agent_psb': 'psb_logist', 'agent_altocar': 'altocar'},
        'by_account_type': {'YANDEX_SERVICE': 'netting'},
    },
)
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
        'nett_50/10. pmt with ref > 0, rev with ref > 0, pmt > rev',
        'nett_50/20. pmt with ref > 0, rev with ref > 0, pmt < rev',
        'nett_50/30. pmt with ref > 0, rev with ref > 0, pmt = rev',
        'nett_50/40. pmt with ref > 0, rev with ref < 0',
    ],
)
async def test_50_payout_ready_netting_task(
        stq3_context,
        load_json,
        static_data,
        dry_run_flag,
        interface_table_revenues='interface.revenues',
        interface_table_payments='interface.payments',
):
    """
        10. payment with refund > revenue with refund
        20. payment with refund < revenue with refund
        30. payment with refund = revenue with refund
        40. payment with refund > 0, revenue with refund < 0
    """

    pool = await stq3_context.pg.master_pool

    data_json = load_json(static_data)
    interface_list = [
        {interface_table_revenues: data_json['revenues']},
        {interface_table_payments: data_json['payments']},
    ]

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
