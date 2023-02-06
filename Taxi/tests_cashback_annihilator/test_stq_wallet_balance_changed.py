import datetime
import decimal

import pytest


BASIC_STQ_KWARGS = {'yandex_uid': '111', 'wallet_id': 'w/111'}


@pytest.mark.config(
    CASHBACK_START_ANNIHILATION_DATE={
        'general_annihilation_date': (
            datetime.datetime.now() + datetime.timedelta(days=2)
        ).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'enabled': True,
    },
)
@pytest.mark.parametrize(
    'test_case',
    [
        pytest.param('happy', id='happy'),
        pytest.param('not_in_base', id='not_in_base'),
        pytest.param('in_base_equal', id='in_base_equal'),
        pytest.param('pw_error_500', id='pw_error_500'),
        pytest.param('pw_error_404', id='pw_error_404'),
        pytest.param('get_wallet_by_id_error', id='get_wallet_by_id_error'),
    ],
)
async def test_wallet_balance_change(
        stq, stq_runner, mockserver, pgsql, test_case,
):
    @mockserver.handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        balances = [
            {
                'balance': '120.0000',
                'currency': 'RUB',
                'wallet_id': (
                    'w/111'
                    if test_case != 'get_wallet_by_id_error'
                    else 'w/112'
                ),
            },
        ]
        if test_case == 'pw_error_404':
            return mockserver.make_response(json={}, status=404)
        if test_case == 'pw_error_500':
            return mockserver.make_response(json={}, status=500)

        return mockserver.make_response(
            json={'balances': balances}, status=200,
        )

    expect_fail = test_case in [
        'pw_error_500',
        'pw_error_404',
        'get_wallet_by_id_error',
    ]

    cursor = pgsql['cashback_annihilator'].cursor()

    if test_case != 'not_in_base':
        cursor.execute(
            'INSERT INTO cashback_annihilator.balances '
            '(yandex_uid, wallet_id, balance_to_expire,'
            ' currency, annihilation_date) '
            'VALUES (\'111\', \'w/111\', %s, '
            '\'RUB\', \'2024-07-10T10:00:00.00Z\');',
            ['120.000' if test_case == 'in_base_equal' else '140.000'],
        )

    await stq_runner.cashback_annihilator_wallet_balance_changed.call(
        task_id='task_id', kwargs=BASIC_STQ_KWARGS, expect_fail=expect_fail,
    )

    if expect_fail or test_case in ['in_base_equal', 'not_in_base']:
        assert stq.cashback_set_pending_annihilation.times_called == 0

    if test_case == 'happy':
        cursor.execute(
            'SELECT wallet_id, yandex_uid, balance_to_expire '
            'FROM cashback_annihilator.balances '
            'WHERE yandex_uid=\'111\';',
        )
        cursor_result = cursor.fetchall()
        if cursor_result:
            pg_result = set(cursor_result[0])
        else:
            pg_result = set()

        expected_db_rows = {'w/111', '111', decimal.Decimal('120.0000')}

        assert not pg_result ^ expected_db_rows

        assert stq.cashback_set_pending_annihilation.times_called == 1
