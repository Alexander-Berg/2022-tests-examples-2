import decimal

import pytest

from tests_cashback_annihilator import common

BASIC_STQ_KWARGS = {'yandex_uid': '1111111', 'attempt_number': 1}


def _is_base_data_correct(pgsql, expected_status='init'):
    cursor = pgsql['cashback_annihilator'].cursor()
    cursor.execute(
        'SELECT transaction_id, yandex_uid, wallet_id, value, status '
        'FROM cashback_annihilator.transactions '
        'WHERE yandex_uid=\'1111111\';',
    )
    cursor_result = cursor.fetchall()
    if cursor_result:
        pg_result = set(cursor_result[0])
    else:
        pg_result = set()

    print(pg_result)
    expected_db_rows = {
        'w/eb92da32-3174-5ca0-9df5-d42db472a355/13.07.2024/attempt_1',
        '1111111',
        'w/eb92da32-3174-5ca0-9df5-d42db472a355',
        decimal.Decimal('1337.0000'),
        expected_status,
    }

    return not pg_result ^ expected_db_rows


@pytest.mark.pgsql(
    'cashback_annihilator', files=['balances.sql', 'transactions.sql'],
)
async def test_happy_path(stq_runner, mockserver, pgsql):
    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    async def _invoice_create(request):
        assert request.query == {}
        return {}

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    async def _invoice_update(request):
        assert request.query == {}
        return {}

    await stq_runner.cashback_start_annihilation.call(
        task_id='task_id', kwargs=BASIC_STQ_KWARGS, expect_fail=False,
    )

    assert _is_base_data_correct(pgsql, expected_status='in_progress')


@pytest.mark.pgsql(
    'cashback_annihilator', files=['balances.sql', 'transactions.sql'],
)
@pytest.mark.parametrize(
    'errors',
    [
        pytest.param(
            [common.Error.CREATE_TRANSACTION_ERROR],
            id='create_transaction_error',
        ),
        pytest.param(
            [common.Error.CREATE_BAD_REQUEST], id='create_bad_request',
        ),
        pytest.param(
            [common.Error.CREATE_RACE_CONDITION], id='create_race_condition',
        ),
        pytest.param(
            [
                common.Error.CREATE_RACE_CONDITION,
                common.Error.UPDATE_TRANSACTION_ERROR,
            ],
            id='create_race_update_transaction_errors',
        ),
        pytest.param(
            [common.Error.CREATE_RACE_CONDITION, common.Error.UPDATE_MATCH],
            id='create_race_update_match_errors',
        ),
        pytest.param(
            [
                common.Error.CREATE_RACE_CONDITION,
                common.Error.UPDATE_BAD_REQUEST,
            ],
            id='create_race_update_bad_request_errors',
        ),
        pytest.param(
            [
                common.Error.CREATE_RACE_CONDITION,
                common.Error.UPDATE_NOT_FOUND,
            ],
            id='create_race_update_not_found_errors',
        ),
        pytest.param(
            [common.Error.UPDATE_TRANSACTION_ERROR],
            id='update_transaction_error',
        ),
        pytest.param([common.Error.UPDATE_MATCH], id='update_match_error'),
        pytest.param(
            [common.Error.UPDATE_NOT_FOUND], id='update_not_found_error',
        ),
        pytest.param(
            [common.Error.UPDATE_BAD_REQUEST], id='update_bad_request_error',
        ),
    ],
)
async def test_invoice_errors(stq_runner, mockserver, pgsql, errors):
    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    async def _invoice_create(request):
        assert request.query == {}
        error = common.Error.get_single_error(errors)
        if error:
            return mockserver.make_response(status=error['code'], json=error)
        return {}

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    async def _invoice_update(request):
        assert request.query == {}
        error = common.Error.get_single_error(errors, common.UPDATE_RESPONSE)
        if error:
            return mockserver.make_response(status=error['code'], json=error)
        return {}

    stq_failing_errors = [
        common.Error.CREATE_BAD_REQUEST,
        common.Error.UPDATE_BAD_REQUEST,
        common.Error.UPDATE_MATCH,
        common.Error.UPDATE_NOT_FOUND,
    ]
    expect_fail = common.is_any_exists_in_errors(stq_failing_errors, errors)

    if common.Error.CREATE_RACE_CONDITION in errors:
        cursor = pgsql['cashback_annihilator'].cursor()
        cursor.execute(
            'INSERT INTO cashback_annihilator.transactions '
            '(transaction_id, yandex_uid, wallet_id, value, status) '
            'VALUES (\'w/eb92da32-3174-5ca0-9df5-d42db472a355/'
            '13.07.2024/attempt_1\', '
            '\'1111111\', \'w/eb92da32-3174-5ca0-9df5-d42db472a355\', '
            '\'1337.000\', \'init\');',
        )

    await stq_runner.cashback_start_annihilation.call(
        task_id='task_id', kwargs=BASIC_STQ_KWARGS, expect_fail=expect_fail,
    )

    base_block_errors = [
        common.Error.CREATE_TRANSACTION_ERROR,
        common.Error.CREATE_BAD_REQUEST,
    ]
    base_not_block_errors = [
        common.Error.UPDATE_TRANSACTION_ERROR,
        common.Error.UPDATE_BAD_REQUEST,
        common.Error.UPDATE_MATCH,
        common.Error.UPDATE_NOT_FOUND,
        common.Error.CREATE_RACE_CONDITION,
    ]
    errors_affecting_the_status = base_not_block_errors[:4]

    is_base_block = common.is_any_exists_in_errors(base_block_errors, errors)
    is_base_not_block = common.is_any_exists_in_errors(
        base_not_block_errors, errors,
    )
    is_init_status = (
        common.is_any_exists_in_errors(errors_affecting_the_status, errors)
        and not (
            errors[0] == common.Error.CREATE_RACE_CONDITION
            and len(errors) == 1
        )
    )

    base_check = _is_base_data_correct(
        pgsql, expected_status='init' if is_init_status else 'in_progress',
    )

    if is_base_block:
        assert not base_check

    if is_base_not_block:
        assert base_check
