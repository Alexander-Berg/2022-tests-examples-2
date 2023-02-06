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
        ('50_static_data.json', False),
    ],
    ids=[
        'nett_double_10. pmt with ref > 0, rev with ref > 0, pmt > rev',
        'nett_double_20. case 1 has data, case 2 None, payout_ready_flag=true',
        'nett_double_30. no person_id in interface tables',
        'nett_double_40. pmt with ref > 0,(rev with ref,coupons>0), pmt>rev',
        'nett_double_50. pmt with ref > 0,(rev with ref,coupons<0)',
    ],
)
async def test_70_payout_double_cases_netting_task(
        stq3_context,
        load_json,
        static_data,
        dry_run_flag,
        interface_table_revenues='interface.revenues',
        interface_table_payments='interface.payments',
):
    """
        nett_double_10. payment with refund > revenue with refund
        nett_double_20. case 1 has data, case 2 None, payout_ready_flag=true
        nett_double_30. no person_id in interface tables
        nett_double_40. pmt with ref > 0,(rev with ref,coupons>0), pmt>rev
        nett_double_50. pmt with ref > 0,(rev with ref,coupons<0)
    """

    pool = await stq3_context.pg.master_pool

    data_json = load_json(static_data)

    interface_list = [
        {interface_table_revenues: data_json['revenues1']},
        {interface_table_payments: data_json['payments1']},
    ]

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

    interface_list = [
        {interface_table_revenues: data_json['revenues2']},
        {interface_table_payments: data_json['payments2']},
    ]
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
