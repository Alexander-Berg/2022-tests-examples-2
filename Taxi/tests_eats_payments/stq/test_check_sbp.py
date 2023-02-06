import pytest

from tests_eats_payments import helpers

NOW = '2020-03-31T07:20:00+00:00'
INVOICE_ID = 'test_order'


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    [
        'eater_user_id',
        'taxi_user_id',
        'application',
        'created_at',
        'sbp_url',
        'notification_called',
    ],
    [
        (
            'eater_user_id',
            '',
            'desktop_web',
            '2020-03-31T07:15:00+00:00',
            None,
            0,
        ),
        (
            'eater_user_id',
            '',
            'desktop_web',
            '2020-03-31T07:15:00+00:00',
            'http://url',
            1,
        ),
    ],
)
async def test_check_invoice_status_for_sbp_link(
        stq_runner,
        stq,
        mock_transactions_invoice_retrieve,
        mock_eats_notifications_notification,
        eater_user_id,
        taxi_user_id,
        application,
        created_at,
        sbp_url,
        notification_called,
):

    if sbp_url is None:
        transactions = [
            helpers.make_transaction(
                payment_type='sbp', operation_id='create:100500',
            ),
        ]
    else:
        transactions = [
            helpers.make_transaction(
                payment_type='sbp',
                operation_id='create:100500',
                payment_url=sbp_url,
            ),
        ]

    mock_transactions_invoice_retrieve(transactions=transactions)
    notification = mock_eats_notifications_notification()

    await stq_runner.eats_payments_check_sbp.call(
        task_id='test_order',
        kwargs={
            'invoice_id': INVOICE_ID,
            'eater_user_id': eater_user_id,
            'taxi_user_id': taxi_user_id,
            'application': application,
            'created_at': created_at,
        },
    )
    assert notification.times_called == notification_called
