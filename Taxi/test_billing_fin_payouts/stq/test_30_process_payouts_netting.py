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
        ('15_static_data.json', True),
        ('20_static_data.json', False),
        ('30_static_data.json', False),
        ('40_static_data.json', False),
        ('50_static_data.json', False),
        ('60_static_data.json', False),
        ('70_static_data.json', False),
        ('80_static_data.json', False),
        ('90_static_data.json', False),
        ('100_static_data.json', False),
        ('110_static_data.json', False),
        ('120_static_data.json', False),
        ('130_static_data.json', False),
        ('140_static_data.json', False),
        ('150_static_data.json', False),
        ('160_static_data.json', False),
        ('170_static_data.json', False),
        ('180_static_data.json', False),
    ],
    ids=[
        'nett_10. pmt with ref > 0, rev with ref > 0, pmt > rev',
        'nett_15. as prev and DRY',
        'nett_20. pmt with ref > 0, rev with ref > 0, pmt < rev',
        'nett_30. pmt with ref > 0, rev with ref > 0, pmt = rev',
        'nett_40. pmt with ref < 0, rev with ref < 0',
        'nett_50. pmt with ref < 0, rev with ref = 0',
        'nett_60. pmt with ref < 0, rev with ref > 0',
        'nett_70. pmt with ref < 0, rev with ref None',
        'nett_80. pmt with ref > 0, rev with ref < 0',
        'nett_90. pmt with ref > 0, rev with ref = 0',
        'nett_100. pmt with ref > 0, rev with ref None',
        'nett_110. pmt with ref = 0, rev with ref < 0',
        'nett_120. pmt with ref = 0, rev with ref = 0',
        'nett_130. pmt with ref = 0, rev with ref > 0',
        'nett_140. pmt with ref = 0, rev with ref None',
        'nett_150. pmt with ref None, rev with ref < 0',
        'nett_160. pmt with ref None, rev with ref = 0',
        'nett_170. pmt with ref None, rev with ref > 0',
        'nett_180. pmt with ref None, rev with ref None',
    ],
)
async def test_30_process_payouts_netting_task(
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
        40. payment with refund < 0, revenue with refund < 0
        50. payment with refund < 0, revenue with refund = 0
        60. payment with refund < 0, revenue with refund > 0
        70. payment with refund < 0, revenue with refund None
        80. payment with refund > 0, revenue with refund < 0
        90. payment with refund > 0, revenue with refund = 0
       100. payment with refund > 0, revenue with refund None
       110. payment with refund = 0, revenue with refund < 0
       120. payment with refund = 0, revenue with refund = 0
       130. payment with refund = 0, revenue with refund > 0
       140. payment with refund = 0, revenue with refund None
       150. payment with refund None, revenue with refund < 0
       160. payment with refund None, revenue with refund = 0
       170. payment with refund None, revenue with refund > 0
       180. payment with refund None, revenue with refund None
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
        stq3_context, task_info=task_info, client_id='1349515601',
    )

    await stq_payout_common_utils.check_results(pool=pool, data_json=data_json)
