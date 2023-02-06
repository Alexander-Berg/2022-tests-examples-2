import copy

import pytest


BASE_DONATION_STATUSES = {
    ('yataxi', 'taxi_order_id'): 'started',
    ('market', '777'): 'finished',
    ('yataxi', 'failed_order_id'): 'not_authorized',
}


@pytest.mark.config(TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}])
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    ['brand', 'order_id', 'transactions_order_id', 'donation_status'],
    [
        ('yataxi', 'taxi_order_id', 'taxi_order_id', 'started'),
        ('market', '777', 'market-777', 'finished'),
        ('yataxi', 'failed_order_id', 'failed_order_id', 'not_authorized'),
    ],
)
@pytest.mark.parametrize(
    [
        'notification_type',
        'operation',
        'operation_status',
        'transaction_status',
        'slug',
    ],
    [
        ('operation_finish', 'pay', 'done', 'irrelevant', 'create_success'),
        ('operation_finish', 'pay', 'failed', 'irrelevant', 'create_fail'),
        ('transaction_clear', 'pay', 'done', 'clear_success', 'clear_success'),
        ('transaction_clear', 'pay', 'done', 'clear_fail', 'clear_fail'),
        ('operation_finish', 'refund', 'done', 'irrelevant', 'cancel_success'),
    ],
)
async def test_simple_new(
        pgsql,
        stq_runner,
        get_donation_statuses,
        brand,
        order_id,
        transactions_order_id,
        donation_status,
        notification_type,
        operation,
        operation_status,
        transaction_status,
        slug,
):
    await stq_runner.payments_persey_callback.call(
        task_id='1',
        args=(
            transactions_order_id,
            f'{transactions_order_id}/{operation}',
            operation_status,
            notification_type,
        ),
        kwargs={
            'transactions': [
                {
                    'external_payment_id': '1',
                    'payment_type': 'card',
                    'status': transaction_status,
                },
            ],
        },
    )

    exp_donation_statuses = copy.deepcopy(BASE_DONATION_STATUSES)
    if slug in ['create_success', 'clear_success']:
        if donation_status == 'started':
            exp_donation_statuses[brand, order_id] = 'finished'
    else:
        exp_donation_statuses[brand, order_id] = 'not_authorized'

    assert get_donation_statuses() == exp_donation_statuses
