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
    static_data, dry_run_flag, payment_processor_value
    """,
    [
        ('10_static_data.json', False, 'YA_BANK'),
        ('15_static_data.json', False, 'YA_BANK'),
        ('20_static_data.json', False, 'YA_BANK'),
        ('25_static_data.json', False, 'YA_BANK'),
        ('30_static_data.json', False, 'YA_BANK'),
        ('40_static_data.json', False, 'YA_BANK'),
        ('50_static_data.json', False, 'YA_BANK'),
        ('60_static_data.json', False, 'YA_BANK'),
    ],
    ids=[
        'bank_nett_90/10. pmt with ref > 0, rev with ref > 0, pmt > rev',
        'bank_nett_90/15. pmt with ref > 0, rev with ref > 0, pmt > rev',
        'bank_nett_90/20. pmt with ref > 0, rev with ref > 0, pmt < rev',
        'bank_nett_90/25. pmt with ref > 0, rev with ref > 0, pmt < rev',
        'bank_nett_90/30. pmt with ref > 0, rev with ref > 0, pmt = rev',
        'bank_nett_90/40. pmt with ref > 0, rev with ref < 0',
        'bank_nett_90/50. pmt with ref > 0, (rev with ref,coupons > 0)',
        'bank_nett_90/60. pmt with ref > 0, (rev with ref,coupons < 0)',
    ],
)
async def test_90_bank_payout_ready_netting_task(
        stq3_context,
        load_json,
        static_data,
        dry_run_flag,
        payment_processor_value,
        interface_table_revenues='interface.revenues',
        interface_table_payments='interface.payments',
):
    """
    10. payment with refund > revenue with refund by 1 external_ref
    15. payment with refund > revenue with refund by 3 external_ref
    20. payment with refund < revenue with refund by 1 external_ref
    25. payment with refund < revenue with refund by 3 external_ref
    30. payment with refund = revenue with refund by 1 external_ref
    40. payment with refund > 0, revenue with refund < 0 by 1 external_ref
    50. payment with refund > (revenue with refund & coupons > 0)
    60. payment with refund > (revenue with refund & coupons < 0)
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
        payment_processor=payment_models.PaymentProcessor(
            payment_processor_value,
        ),
    )
    # run task
    await process_payouts.task(
        stq3_context,
        task_info=task_info,
        client_id='1349515601',
        payout_ready_flag=True,
    )

    await stq_payout_common_utils.check_results(pool=pool, data_json=data_json)
