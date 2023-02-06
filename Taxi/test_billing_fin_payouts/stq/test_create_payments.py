import pytest

from billing_fin_payouts.stq import create_payments
from test_billing_fin_payouts import common_utils
from . import stq_payout_common_utils


@pytest.mark.pgsql(dbname='billing_fin_payouts', files=('fill_tables.psql',))
@pytest.mark.config(BILLING_FIN_PAYOUTS_STQ_CREATE_PAYMENTS_ENABLED=True)
@pytest.mark.now('2022-06-01T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    """
    test_data_json
    """,
    ['test_data.json'],
)
async def test_create_payments(
        stq3_context,
        create_payments_task_info,
        stq,
        load_json,
        test_data_json,
):
    test_data = load_json(test_data_json)
    await create_payments.task(
        stq3_context, create_payments_task_info, client_id='1349515601',
    )

    pool = await stq3_context.pg.master_pool

    await stq_payout_common_utils.check_payments(
        pool=pool, data_expected=test_data['expected_payments'],
    )

    await stq_payout_common_utils.check_payment_event_log(
        pool=pool, data_expected=test_data['expected_payment_event_log'],
    )

    await stq_payout_common_utils.check_payout_event_log(
        pool=pool, data_expected=test_data['expected_payout_event_log'],
    )

    common_utils.check_stq_calls(
        queue=stq.billing_fin_payouts_process_payments,
        expected_calls=test_data['expected_stq_calls'],
    )

    # check task was rescheduled
    common_utils.check_stq_calls(
        queue=stq.billing_fin_payouts_create_payments,
        expected_calls=[
            {
                'task_id': '1',
                'kwargs': None,
                'args': None,
                'eta': '2022-06-01T00:00:00.000000+00:00',
            },
        ],
    )
