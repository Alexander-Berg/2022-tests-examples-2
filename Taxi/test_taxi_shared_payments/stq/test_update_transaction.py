import pytest

from taxi_shared_payments.common import helpers
from taxi_shared_payments.repositories import stats as stats_repo
from taxi_shared_payments.stq import update_transaction

DEFAULT_NOW = '2019-06-06T01:00:00.0'


@pytest.mark.parametrize(
    'params, expected_spent',
    [
        pytest.param(
            {
                'transaction_id': 'tr_3',
                'order_id': 'order_id_1',
                'event': 'hold',
                'amount': 100,
                'currency': 'RUB',
            },
            300,
            marks=pytest.mark.now(DEFAULT_NOW),
            id='new_transaction',
        ),
        pytest.param(
            {
                'transaction_id': 'tr_1',
                'order_id': 'order_id_1',
                'event': 'hold',
                'amount': 100,
                'currency': 'RUB',
            },
            200,
            marks=pytest.mark.now(DEFAULT_NOW),
            id='exist_transaction',
        ),
        pytest.param(
            {
                'transaction_id': 'tr_3',
                'order_id': 'order_id_1',
                'event': 'refund',
                'amount': -100,
                'currency': 'RUB',
            },
            100,
            marks=pytest.mark.now(DEFAULT_NOW),
            id='refund',
        ),
        pytest.param(
            {
                'transaction_id': 'tr_1',
                'order_id': 'order_id_1',
                'event': 'refund',
                'amount': -100,
                'currency': 'RUB',
            },
            100,
            marks=pytest.mark.now(DEFAULT_NOW),
            id='refund_same_transaction',
        ),
        pytest.param(
            {
                'transaction_id': 'tr_1',
                'order_id': 'order_id_2',
                'event': 'hold',
                'amount': 100,
                'currency': 'RUB',
            },
            100,
            marks=pytest.mark.now('2019-07-06T01:00:00.0'),
            id='new_month',
        ),
        pytest.param(
            {
                'transaction_id': 'tr_3',
                'order_id': 'order_id_1',
                'event': 'hold',
                'amount': 100,
                'currency': 'USD',
            },
            15200,
            marks=pytest.mark.now(DEFAULT_NOW),
            id='usd',
        ),
    ],
)
async def test_update_transaction(
        stq3_context, mock_all_api, params, expected_spent,
):
    await update_transaction.task(stq3_context, **params)

    now_month = helpers.now_month(utc_tz_offset='+0300')
    stats = await stats_repo.get(stq3_context, 'memb1', now_month)

    assert stats.spent == expected_spent
