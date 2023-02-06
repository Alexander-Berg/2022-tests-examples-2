import pytest

from tests_eats_payments_billing import eats_plus_consts
from tests_eats_payments_billing import eats_plus_helpers


@pytest.mark.parametrize(
    'stq_kwargs, request_arg, eats_billing_processor_arg, expect_fail, '
    'billing_data_times_called, expected_stq_args',
    [
        pytest.param(
            eats_plus_helpers.make_stq_kwargs(
                amount='50',
                comission_cashback='15',
                rewards=[
                    eats_plus_helpers.make_stq_reward(
                        amount='50', source='service',
                    ),
                ],
            ),
            eats_plus_helpers.make_request_arg_payment(
                amount='50',
                amount_per_place='15',
                amount_per_eda='35',
                commission_cashback='15',
            ),
            eats_plus_helpers.make_b_processor_cashback_emis(
                amount='50',
                amount_per_place='15',
                amount_per_eda='35',
                commission_cashback='15',
            ),
            False,
            1,
            eats_plus_helpers.make_billing_events_stq_kwargs(
                order_nr=eats_plus_consts.ORDER_ID,
            ),
            id='Test regular stq',
        ),
        pytest.param(
            eats_plus_helpers.make_stq_kwargs(
                amount='50',
                comission_cashback='15',
                rewards=[
                    eats_plus_helpers.make_stq_reward(
                        amount='50', source='service',
                    ),
                ],
                has_payload=False,
            ),
            eats_plus_helpers.make_request_arg_payment(
                amount='50',
                amount_per_place='15',
                amount_per_eda='35',
                commission_cashback='15',
            ),
            [],
            True,
            0,
            None,
            id='Test empty payload',
        ),
        pytest.param(
            eats_plus_helpers.make_stq_kwargs(
                amount='-10',
                comission_cashback='-10',
                rewards=[
                    eats_plus_helpers.make_stq_reward(
                        amount='-10', source='service',
                    ),
                ],
            ),
            eats_plus_helpers.make_request_arg_payment(
                amount='',
                amount_per_place='',
                amount_per_eda='',
                commission_cashback='',
            ),
            [],
            True,
            0,
            None,
            id='Test negative amount',
        ),
        pytest.param(
            eats_plus_helpers.make_stq_kwargs(
                amount='50',
                comission_cashback='60',
                rewards=[
                    eats_plus_helpers.make_stq_reward(
                        amount='50', source='service',
                    ),
                ],
            ),
            eats_plus_helpers.make_request_arg_payment(
                amount='',
                amount_per_place='',
                amount_per_eda='',
                commission_cashback='',
            ),
            [],
            True,
            1,
            None,
            id='Test negative amount per eda',
        ),
    ],
)
async def test_eats_plus_cashback_emission_proxy(
        stq_runner,
        stq,
        mock_eats_billing_processor,
        mock_order_billing_data,
        mock_eats_billing_storage,
        stq_kwargs,
        request_arg,
        eats_billing_processor_arg,
        expect_fail,
        billing_data_times_called,
        expected_stq_args,
):
    mock_order_billing_data(
        order_id=eats_plus_consts.ORDER_ID,
        response_code=200,
        transaction_date=eats_plus_consts.TRANSACTION_DATE,
    )

    mock_eats_billing_processor = mock_eats_billing_processor(
        expected_requests=eats_billing_processor_arg,
    )

    mock_eats_billing_storage(expected_data=request_arg)

    await stq_runner.eats_plus_cashback_emission.call(
        task_id='sample_task', kwargs=stq_kwargs, expect_fail=expect_fail,
    )

    assert mock_eats_billing_processor.times_called == 0 if expect_fail else 1


async def test_grocery_order_cycle(
        stq_runner,
        stq,
        mock_eats_billing_storage,
        grocery_orders,
        mock_eats_billing_processor,
):
    order_id = eats_plus_consts.GROCERY_CYCLE_ORDER_ID
    grocery_orders.add_order(order_id=order_id, created='2020-03-03T10:04:37Z')

    mock_eats_billing_processor(
        eats_plus_helpers.make_b_processor_cashback_emis(
            order_id=order_id,
            amount='50',
            amount_per_place='15',
            amount_per_eda='35',
            commission_cashback='15',
        ),
    )

    request_arg = eats_plus_helpers.make_request_arg_payment(
        order_id=order_id,
        amount='50',
        amount_per_place='15',
        amount_per_eda='35',
        commission_cashback='15',
    )

    mock_eats_billing_storage(expected_data=request_arg)

    task_id = 'task-id-123'

    await stq_runner.eats_plus_cashback_emission.call(
        task_id=task_id,
        kwargs=eats_plus_helpers.make_stq_kwargs(
            order_id=order_id,
            amount='50',
            comission_cashback='15',
            rewards=[
                eats_plus_helpers.make_stq_reward(
                    amount='50', source='service',
                ),
            ],
        ),
    )
