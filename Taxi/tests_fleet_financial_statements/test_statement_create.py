import decimal

import pytest

from tests_fleet_financial_statements.common import defaults
from tests_fleet_financial_statements.common import errors
from tests_fleet_financial_statements.common import limits


STMT_EXT_ID = '00000000-0000-0000-0000-000000000003'


async def test_default(statement_create, pg_database):
    response = await statement_create(
        id=STMT_EXT_ID,
        json={
            'preset': {
                'work_rule_id': ['WORK_RULE_A'],
                'work_status': ['working'],
                'balance_limit': '50.0001',
                'pay_minimum': '100.0001',
                'pay_maximum': '1000.0001',
                'rounding_multiple': '200.0001',
            },
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'id': STMT_EXT_ID,
        'revision': 1,
        'status': 'preparing',
    }

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                park_id,
                stmt_id,
                stmt_revision,
                stmt_status,
                created_at BETWEEN NOW() - '1 MINUTE'::INTERVAL
                               AND NOW() + '1 MINUTE'::INTERVAL,
                created_by,
                updated_at BETWEEN NOW() - '1 MINUTE'::INTERVAL
                               AND NOW() + '1 MINUTE'::INTERVAL,
                work_rule_id,
                work_status,
                balance_at BETWEEN NOW() - '1 MINUTE'::INTERVAL
                               AND NOW() + '1 MINUTE'::INTERVAL,
                balance_limit,
                pay_mult_of,
                pay_minimum,
                pay_maximum
            FROM
                fleet_financial_statements.finstmt
            WHERE
                park_id = %s
                AND stmt_ext_id = %s
        """,
            [defaults.PARK_ID, STMT_EXT_ID],
        )
        assert cursor.fetchone() == (
            'PARK-01',
            3,
            1,
            'preparing',
            True,
            'Y1000',
            True,
            ['WORK_RULE_A'],
            ['working'],
            True,
            decimal.Decimal('50.0001'),
            decimal.Decimal('200.0001'),
            decimal.Decimal('100.0001'),
            decimal.Decimal('1000.0001'),
        )


async def test_stq_call(statement_create, stq_prepare_client):
    response = await statement_create(id=STMT_EXT_ID)
    assert response.status_code == 200, response.text

    assert stq_prepare_client.times_called == 1
    task = stq_prepare_client.next_call()
    assert task['id'] == f'PARK-01/P/3'
    assert task['kwargs']['park_id'] == defaults.PARK_ID
    assert task['kwargs']['stmt_id'] == 3
    assert task['kwargs']['stmt_revision'] == 1


@pytest.mark.parametrize(
    ['json', 'message'],
    [
        (
            {
                'preset': {
                    'balance_limit': str(
                        limits.MIN_BALANCE_AMOUNT - limits.DECIMAL4_EPSILON,
                    ),
                },
            },
            errors.EM_FIELD_NOT_GE.format(
                'preset.balance_limit', limits.MIN_BALANCE_AMOUNT,
            ),
        ),
        (
            {
                'preset': {
                    'balance_limit': str(
                        limits.MAX_BALANCE_AMOUNT + limits.DECIMAL4_EPSILON,
                    ),
                },
            },
            errors.EM_FIELD_NOT_LE.format(
                'preset.balance_limit', limits.MAX_BALANCE_AMOUNT,
            ),
        ),
        (
            {
                'preset': {
                    'pay_minimum': str(
                        limits.MIN_PAY_AMOUNT - limits.DECIMAL4_EPSILON,
                    ),
                },
            },
            errors.EM_FIELD_NOT_GE.format(
                'preset.pay_minimum', limits.MIN_PAY_AMOUNT,
            ),
        ),
        (
            {
                'preset': {
                    'pay_minimum': str(
                        limits.MAX_PAY_AMOUNT + limits.DECIMAL4_EPSILON,
                    ),
                },
            },
            errors.EM_FIELD_NOT_LE.format(
                'preset.pay_minimum', limits.MAX_PAY_AMOUNT,
            ),
        ),
        (
            {
                'preset': {
                    'pay_maximum': str(
                        limits.MIN_PAY_AMOUNT - limits.DECIMAL4_EPSILON,
                    ),
                },
            },
            errors.EM_FIELD_NOT_GE.format(
                'preset.pay_maximum', limits.MIN_PAY_AMOUNT,
            ),
        ),
        (
            {
                'preset': {
                    'pay_maximum': str(
                        limits.MAX_PAY_AMOUNT + limits.DECIMAL4_EPSILON,
                    ),
                },
            },
            errors.EM_FIELD_NOT_LE.format(
                'preset.pay_maximum', limits.MAX_PAY_AMOUNT,
            ),
        ),
        (
            {
                'preset': {
                    'rounding_multiple': str(
                        limits.MIN_PAY_AMOUNT - limits.DECIMAL4_EPSILON,
                    ),
                },
            },
            errors.EM_FIELD_NOT_GE.format(
                'preset.rounding_multiple', limits.MIN_PAY_AMOUNT,
            ),
        ),
        (
            {
                'preset': {
                    'rounding_multiple': str(
                        limits.MAX_PAY_AMOUNT + limits.DECIMAL4_EPSILON,
                    ),
                },
            },
            errors.EM_FIELD_NOT_LE.format(
                'preset.rounding_multiple', limits.MAX_PAY_AMOUNT,
            ),
        ),
        (
            {'preset': {'pay_minimum': '1001', 'pay_maximum': '1000'}},
            errors.EM_FIELD_NOT_GE.format('preset.pay_maximum', 1001),
        ),
        (
            {
                'preset': {
                    'pay_minimum': '1001',
                    'pay_maximum': '1999',
                    'rounding_multiple': '1000',
                },
            },
            errors.EM_FIELD_NOT_GE.format('preset.pay_maximum', 2000),
        ),
    ],
)
async def test_invalid_argument(statement_create, json, message):
    response = await statement_create(id=STMT_EXT_ID, json=json)
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': errors.EC_INVALID_ARGUMENT,
        'message': message,
    }


async def test_already_exists(statement_create):
    response = await statement_create(
        id='00000000-0000-0000-0000-000000000001',
    )
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': errors.EC_ALREADY_EXISTS,
        'message': errors.EM_ALREADY_EXISTS,
    }

    # check 409 for deleted statements
    response = await statement_create(
        id='00000000-0000-0000-0000-000000000002',
    )
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': errors.EC_ALREADY_EXISTS,
        'message': errors.EM_ALREADY_EXISTS,
    }
