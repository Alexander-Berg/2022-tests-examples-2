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
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYOUTS_SETTINGS_V2={
        'bulk_size': {'__default__': 2, 'data_open_payments': 3},
        'max_iterations': 2,
    },
)
@pytest.mark.parametrize(
    """
    static_data,
    payout_ready_flag,
    dry_run_flag,
    payment_processor_value
    """,
    [
        ('10_static_data.json', False, False, 'OEBS'),
        ('20_static_data.json', False, False, 'OEBS'),
        ('30_static_data.json', True, False, 'OEBS'),
    ],
    ids=[
        'nett_10_iterations_bulk.',
        'nett_20_iterations_bulk.',
        'nett_30_iterations_bulk.',
    ],
)
async def test_120_bulk_process_with_iterations(
        stq3_context,
        load_json,
        static_data,
        payout_ready_flag,
        dry_run_flag,
        payment_processor_value,
        interface_table_revenues='interface.revenues',
        interface_table_payments='interface.payments',
):
    """
        10. payment with refund > revenue with refund, bulk = 2, iterations 2
        20. data_open payments. payout_ready_flag = false, iterations 2
        30. data_open payments. payout_ready_flag = true, iterations 2
    """

    pool = await stq3_context.pg.master_pool

    data_json = load_json(static_data)
    interface_list = [
        {interface_table_revenues: data_json['revenues']},
        {interface_table_payments: data_json['payments']},
        {'payouts.data_open': data_json['data_open_payments']},
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
        payout_ready_flag=payout_ready_flag,
    )

    await stq_payout_common_utils.check_results(pool=pool, data_json=data_json)
