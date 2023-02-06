import pytest

from billing_fin_payouts.models.payments import payment as payment_models
from billing_fin_payouts.stq import process_payouts
from test_billing_fin_payouts import common_utils
from . import stq_payout_common_utils


@pytest.mark.config(
    BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYOUTS_ENABLED=True,
    BILLING_FIN_PAYOUTS_CREATE_PAYMENTS_ENABLED=True,
)
@pytest.mark.parametrize(
    """
    payout_ready_flag,
    test_data_json,
    dry_run_flag,
    payment_processor_value
    """,
    [
        (False, 'test_data_netting.json', False, 'YA_BANK'),
        (True, 'test_data_payout_ready.json', False, 'YA_BANK'),
    ],
)
async def test_create_payouts(
        stq3_context,
        process_payouts_task_info,
        stq,
        load_json,
        payout_ready_flag,
        test_data_json,
        dry_run_flag,
        payment_processor_value,
):

    test_data = load_json(test_data_json)

    interface_list = [
        {'interface.revenues': test_data['revenues']},
        {'interface.payments': test_data['payments']},
    ]

    pool = await stq3_context.pg.master_pool
    await stq_payout_common_utils.load_data(
        pool=pool, interface_list=interface_list,
    )

    task_info = stq_payout_common_utils.build_task_info(
        dry_run=dry_run_flag,
        payment_processor=payment_models.PaymentProcessor(
            payment_processor_value,
        ),
    )

    # run process_payouts task
    await process_payouts.task(
        stq3_context,
        task_info=task_info,
        client_id='1349515601',
        payout_ready_flag=payout_ready_flag,
    )

    pool = await stq3_context.pg.master_pool

    await stq_payout_common_utils.check_batches_with_payout_id(
        pool=pool, data_expected=test_data['expected_batches'],
    )

    await stq_payout_common_utils.check_batch_change_log(
        pool=pool, data_expected=test_data['expected_batch_change_log'],
    )

    await stq_payout_common_utils.check_payouts(
        pool=pool, data_expected=test_data['expected_payment_payouts'],
    )

    await stq_payout_common_utils.check_payout_event_log(
        pool=pool, data_expected=test_data['expected_payout_event_log'],
    )

    common_utils.check_stq_calls(
        queue=stq.billing_fin_payouts_create_payments,
        expected_calls=test_data['expected_stq_calls'],
    )
