import pytest

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


def make_logistic_experiment(
        send_enabled, eats_payments_billing_enabled,
) -> dict:
    return {
        'name': 'eats_payments_logistic_notifications',
        'consumers': ['eats-payments-billing/logistic-notifications'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {
                    'send_logistic_notifications_enabled': send_enabled,
                    'send_logistics_notifications_from_eats_payments_billing': (  # noqa: E501 pylint: disable=line-too-long
                        eats_payments_billing_enabled
                    ),
                },
            },
        ],
    }


@pytest.mark.parametrize(
    'stq_kwargs, expect_fail, send_enabled,'
    'eats_payments_billing_enabled, expected_output_stq_args,'
    'times_called',
    [
        pytest.param(
            helpers.make_stq_kwargs(transaction_type='payment', items=[]),
            False,
            True,
            True,
            None,
            0,
            id='Test payment with no items',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='delivery', amount='1000',
                    ),
                ],
            ),
            False,
            True,
            False,
            None,
            0,
            id='Test eats_payments_billing disabled',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='delivery', amount='1000',
                    ),
                ],
            ),
            False,
            False,
            True,
            None,
            0,
            id='Test experiment disabled',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='delivery', amount='100',
                    ),
                    helpers.make_stq_item(
                        item_id='3', item_type='assembly', amount='1',
                    ),
                    helpers.make_stq_item(
                        item_id='4', item_type='tips', amount='99',
                    ),
                ],
            ),
            False,
            True,
            True,
            [
                helpers.make_logistic_stq_kwargs(
                    amount='99',
                    item_type='tips',
                    status='payment',
                    payment_type='card',
                ),
                helpers.make_logistic_stq_kwargs(
                    amount='1',
                    item_type='assembly',
                    status='payment',
                    payment_type='card',
                ),
                helpers.make_logistic_stq_kwargs(
                    amount='100',
                    item_type='delivery',
                    status='payment',
                    payment_type='card',
                ),
            ],
            3,
            id='Test sending only delivery, assembly and tips',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='refund',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='delivery', amount='100',
                    ),
                    helpers.make_stq_item(
                        item_id='3', item_type='assembly', amount='1',
                    ),
                    helpers.make_stq_item(
                        item_id='4', item_type='tips', amount='99',
                    ),
                ],
            ),
            False,
            True,
            True,
            [
                helpers.make_logistic_stq_kwargs(
                    amount='99',
                    item_type='tips',
                    status='refund',
                    payment_type='card',
                ),
                helpers.make_logistic_stq_kwargs(
                    amount='1',
                    item_type='assembly',
                    status='refund',
                    payment_type='card',
                ),
                helpers.make_logistic_stq_kwargs(
                    amount='100',
                    item_type='delivery',
                    status='refund',
                    payment_type='card',
                ),
            ],
            3,
            id='Test refund',
        ),
    ],
)
async def test_logistic_notification(
        stq_runner,
        stq,
        experiments3,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        stq_kwargs,
        expect_fail,
        send_enabled,
        eats_payments_billing_enabled,
        expected_output_stq_args,
        times_called,
):
    mock_order_billing_data(
        order_id=consts.ORDER_ID,
        response_code=200,
        transaction_date=consts.TRANSACTION_DATE,
        order_type='native',
        flow_type='retail',
    )

    mock_eats_billing_storage()
    mock_eats_billing_processor()

    experiments3.add_config(
        **make_logistic_experiment(
            send_enabled=send_enabled,
            eats_payments_billing_enabled=eats_payments_billing_enabled,
        ),
    )

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id=consts.TASK_ID, kwargs=stq_kwargs, expect_fail=expect_fail,
    )

    if times_called > 0:
        for arg in expected_output_stq_args:
            task_info = (
                stq.eda_order_logistic_payment_events_callback.next_call()
            )
            task_id = task_info['id']
            task_kwargs = task_info['kwargs']
            task_kwargs.pop('log_extra')
            assert task_kwargs == arg
            assert task_id == f'{consts.TASK_ID}/{arg["item_type"]}'


@pytest.mark.parametrize(
    'stq_payment_type, logistic_payment_type',
    [
        pytest.param('card', 'card'),
        pytest.param('postpayment', 'card'),
        pytest.param('sbp', 'card'),
        pytest.param('applepay', 'applepay'),
        pytest.param('googlepay', 'googlepay'),
        pytest.param('corp', 'corp'),
        pytest.param('badge', 'badge'),
    ],
)
async def test_payment_types(
        stq_runner,
        stq,
        experiments3,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        stq_payment_type,
        logistic_payment_type,
):
    mock_order_billing_data(
        order_id=consts.ORDER_ID,
        response_code=200,
        transaction_date=consts.TRANSACTION_DATE,
        order_type='native',
        flow_type='retail',
    )

    mock_eats_billing_storage()
    mock_eats_billing_processor()

    experiments3.add_config(
        **make_logistic_experiment(
            send_enabled=True, eats_payments_billing_enabled=True,
        ),
    )

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id=consts.TASK_ID,
        kwargs=helpers.make_stq_kwargs(
            transaction_type='payment',
            items=[
                helpers.make_stq_item(
                    item_id='1', item_type='delivery', amount='100',
                ),
            ],
            payment_type=stq_payment_type,
        ),
        expect_fail=False,
    )

    task_info = stq.eda_order_logistic_payment_events_callback.next_call()
    task_kwargs = task_info['kwargs']
    task_kwargs.pop('log_extra')
    assert task_kwargs == helpers.make_logistic_stq_kwargs(
        amount='100',
        item_type='delivery',
        status='payment',
        payment_type=logistic_payment_type,
    )
