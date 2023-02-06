import datetime
import decimal

import pytest

from tests_cashback_annihilator import common

FAILED_OPERATION_STATUS = 'failed'
DONE_OPERATION_STATUS = 'done'
OPERATION_FINISH_TYPE = 'operation_finish'


def _is_base_operation_finished(pgsql, check_annihilated_at=True):
    cursor = pgsql['cashback_annihilator'].cursor()
    cursor.execute(
        'SELECT transaction_id, yandex_uid, wallet_id, value, status '
        'FROM cashback_annihilator.transactions '
        'WHERE yandex_uid=\'2222222\';',
    )
    cursor_result = cursor.fetchall()
    if cursor_result:
        pg_result = set(cursor_result[0])
    else:
        pg_result = set()

    expected_db_rows = {
        'w/eb92da32-3174-5ca0-9df5-d42db472a355_id3/13.07.2024/attempt_1',
        '2222222',
        'w/eb92da32-3174-5ca0-9df5-d42db472a355_id3',
        decimal.Decimal('100.0000'),
        'done',
    }

    transaction_done = not pg_result ^ expected_db_rows

    cursor.execute(
        'SELECT wallet_id, yandex_uid, balance_to_expire, currency, '
        'annihilation_date, annihilated_at '
        'FROM cashback_annihilator.balances '
        'WHERE yandex_uid=\'2222222\';',
    )
    cursor_result = cursor.fetchall()
    if cursor_result:
        if check_annihilated_at:
            assert cursor_result[0][-1]
        pg_result = set(cursor_result[0][:-1])
    else:
        pg_result = set()

    expected_db_rows = {
        'w/eb92da32-3174-5ca0-9df5-d42db472a355_id3',
        '2222222',
        decimal.Decimal('1337.0000'),
        'RUB',
        datetime.datetime.strptime(
            '2024-07-13 04:01:50+0300', '%Y-%m-%d %H:%M:%S%z',
        ),
    }

    balances_done = not pg_result ^ expected_db_rows

    return transaction_done and balances_done


@pytest.mark.pgsql(
    'cashback_annihilator', files=['balances.sql', 'transactions.sql'],
)
@pytest.mark.parametrize(
    'stq_params,' 'errors',
    [
        pytest.param(
            {
                'invoice_id': 'invoice123',
                'operation_id': (
                    'w/eb92da32-3174-5ca0-9df5-d42db472a355_id3/'
                    '13.07.2024/attempt_1'
                ),
                'operation_status': DONE_OPERATION_STATUS,
                'notification_type': OPERATION_FINISH_TYPE,
                'transactions': [],
            },
            [],
            id='operation_finish_happy_path',
        ),
        pytest.param(
            {
                'invoice_id': 'invoice123',
                'operation_id': (
                    'w/eb92da32-3174-5ca0-9df5-d42db472a355_id3/'
                    '13.07.2024/attempt_1'
                ),
                'operation_status': DONE_OPERATION_STATUS,
                'notification_type': OPERATION_FINISH_TYPE,
                'transactions': [],
            },
            [common.Error.TRANSACTION_NOT_EXISTS],
            id='operation_finish_transaction_not_found',
        ),
        pytest.param(
            {
                'invoice_id': 'invoice123',
                'operation_id': (
                    'w/eb92da32-3174-5ca0-9df5-d42db472a355_id3/'
                    '13.07.2024/attempt_1'
                ),
                'operation_status': FAILED_OPERATION_STATUS,
                'notification_type': OPERATION_FINISH_TYPE,
                'transactions': [],
            },
            [],
            id='operation_failed',
        ),
    ],
)
@pytest.mark.config(
    CASHBACK_ANNIHILATOR_TRANSACTIONS_RETRY_SETTINGS={
        'max_retries': 10,
        'delay': 0,
    },
)
async def test_cashback_annihilation_callback(
        stq_runner, pgsql, stq_params, errors, stq,
):
    stq_failing_errors = [common.Error.TRANSACTION_NOT_EXISTS]

    expect_fail = common.is_any_exists_in_errors(stq_failing_errors, errors)

    if expect_fail:
        cursor = pgsql['cashback_annihilator'].cursor()
        cursor.execute(
            'DELETE FROM cashback_annihilator.transactions '
            'WHERE transaction_id = '
            '\'w/eb92da32-3174-5ca0-9df5-d42db472a355_id3/'
            '13.07.2024/attempt_1\';',
        )

    await stq_runner.cashback_annihilation_callback.call(
        task_id='task_id', kwargs=stq_params, expect_fail=expect_fail,
    )

    if (
            stq_params['notification_type'] == OPERATION_FINISH_TYPE
            and stq_params['operation_status'] == DONE_OPERATION_STATUS
            and not expect_fail
    ):
        assert _is_base_operation_finished(pgsql)
        assert stq.cashback_set_pending_annihilation.times_called == 1

    if (
            stq_params['operation_status'] == FAILED_OPERATION_STATUS
            and not expect_fail
    ):
        assert not _is_base_operation_finished(pgsql, False)
        assert stq.cashback_start_annihilation.times_called == 1
