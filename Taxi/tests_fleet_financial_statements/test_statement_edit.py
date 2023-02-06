import decimal

import dateutil
import pytest

from tests_fleet_financial_statements.common import defaults
from tests_fleet_financial_statements.common import errors
from tests_fleet_financial_statements.common import jsonx
from tests_fleet_financial_statements.common import limits


async def test_default(statement_edit, retrieve_driver_profiles, pg_database):
    response = await statement_edit(json={'commission_percent': '10'})
    assert response.status_code == 200, response.text
    assert response.json() == {
        'id': defaults.STMT_EXT_ID,
        'revision': 3,
        'status': 'draft',
    }

    assert retrieve_driver_profiles.times_called == 0

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                stmt_revision,
                updated_at BETWEEN NOW() - '1 HOUR'::INTERVAL
                               AND NOW() + '1 HOUR'::INTERVAL,
                edited_at BETWEEN NOW() - '1 HOUR'::INTERVAL
                              AND NOW() + '1 HOUR'::INTERVAL,
                edited_by,
                bcm_percent,
                bcm_minimum
            FROM
                fleet_financial_statements.finstmt
            WHERE
                park_id = %s
                AND stmt_id = %s
        """,
            [defaults.PARK_ID, defaults.STMT_ID],
        )
        assert cursor.fetchone() == (
            3,
            True,
            True,
            ['Y1001', 'Y1000'],
            decimal.Decimal('0.1'),
            decimal.Decimal('100'),
        )


async def test_change_nothing(
        statement_edit, retrieve_driver_profiles, pg_database,
):
    response = await statement_edit(
        json={
            'commission_percent': '5',
            'commission_minimum': '100',
            'entries': [
                {'driver_profile_id': 'DRIVER-00'},
                {'driver_profile_id': 'DRIVER-01', 'pay_amount': '1000'},
                {'driver_profile_id': 'DRIVER-02', 'pay_amount': '2000'},
                {'driver_profile_id': 'DRIVER-03', 'pay_amount': '3000'},
            ],
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'id': defaults.STMT_EXT_ID,
        'revision': 2,
        'status': 'draft',
    }

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                stmt_revision,
                edited_at,
                edited_by,
                bcm_percent,
                bcm_minimum,
                total_ent_count,
                total_pay_amount,
                total_bcm_amount
            FROM
                fleet_financial_statements.finstmt
            WHERE
                park_id = %s
                AND stmt_id = %s
        """,
            [defaults.PARK_ID, defaults.STMT_ID],
        )
        return cursor.fetchone() == (
            2,
            dateutil.parser.parse('2020-01-01T14:00:00+03:00'),
            ['Y1001'],
            decimal.Decimal('0.1'),
            decimal.Decimal('100'),
            5,
            decimal.Decimal('15000'),
            decimal.Decimal('771.4285'),
        )


@pytest.mark.parametrize(
    [
        'request_commission_percent',
        'request_commission_minimum',
        'expected_total',
    ],
    [
        (None, None, decimal.Decimal('771.4285')),
        (None, decimal.Decimal('200'), decimal.Decimal('1038.0952')),
        (decimal.Decimal('10'), None, decimal.Decimal('1372.7274')),
        (decimal.Decimal('0'), decimal.Decimal('0'), decimal.Decimal('0')),
        (
            decimal.Decimal('0'),
            decimal.Decimal('200'),
            decimal.Decimal('1000'),
        ),
        (
            decimal.Decimal('10'),
            decimal.Decimal('0'),
            decimal.Decimal('1363.6365'),
        ),
        (
            decimal.Decimal('10'),
            decimal.Decimal('200'),
            decimal.Decimal('1490.9092'),
        ),
    ],
)
async def test_change_commission(
        statement_edit,
        retrieve_driver_profiles,
        pg_database,
        request_commission_percent,
        request_commission_minimum,
        expected_total,
):
    response = await statement_edit(
        json={
            'commission_percent': (
                str(request_commission_percent)
                if request_commission_percent is not None
                else None
            ),
            'commission_minimum': (
                str(request_commission_minimum)
                if request_commission_minimum is not None
                else None
            ),
        },
    )
    assert response.status_code == 200, response.text

    assert retrieve_driver_profiles.times_called == 0

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                bcm_percent,
                bcm_minimum,
                total_bcm_amount
            FROM
                fleet_financial_statements.finstmt
            WHERE
                park_id = %s
                AND stmt_id = %s
        """,
            [defaults.PARK_ID, defaults.STMT_ID],
        )
        assert cursor.fetchone() == (
            request_commission_percent / 100
            if request_commission_percent is not None
            else decimal.Decimal('0.05'),
            request_commission_minimum
            if request_commission_minimum is not None
            else decimal.Decimal('100'),
            expected_total,
        )


@pytest.mark.parametrize(
    ['request_entries', 'expected_total'],
    [
        (
            [('DRIVER-06', decimal.Decimal('0'))],
            (6, decimal.Decimal('15000'), decimal.Decimal('771.4285')),
        ),
        (
            [('DRIVER-06', decimal.Decimal('1000'))],
            (6, decimal.Decimal('16000'), decimal.Decimal('871.4285')),
        ),
        (
            [('DRIVER-06', decimal.Decimal('3000'))],
            (6, decimal.Decimal('18000'), decimal.Decimal('914.2856')),
        ),
        (
            [('DRIVER-06', decimal.Decimal('5000'))],
            (6, decimal.Decimal('20000'), decimal.Decimal('1009.5237')),
        ),
        (
            [
                ('DRIVER-06', decimal.Decimal('5000')),
                ('DRIVER-07', decimal.Decimal('5000')),
            ],
            (7, decimal.Decimal('25000'), decimal.Decimal('1247.6189')),
        ),
    ],
)
async def test_create_entries(
        statement_edit,
        retrieve_driver_profiles,
        pg_database,
        request_entries,
        expected_total,
):
    response = await statement_edit(
        json={
            'entries': [
                {'driver_profile_id': dp_id, 'pay_amount': str(amount)}
                for dp_id, amount in request_entries
            ],
        },
    )
    assert response.status_code == 200, response.text

    assert retrieve_driver_profiles.times_called == 1
    request = retrieve_driver_profiles.next_call()['request']
    assert request.query == {'consumer': 'fleet-financial-statements'}
    assert jsonx.sort(request.json, 'id_in_set') == {
        'id_in_set': [f'PARK-01_{dp_id}' for dp_id, _ in request_entries],
    }

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                total_ent_count,
                total_pay_amount,
                total_bcm_amount
            FROM
                fleet_financial_statements.finstmt
            WHERE
                park_id = %s
                AND stmt_id = %s
        """,
            [defaults.PARK_ID, defaults.STMT_ID],
        )
        assert cursor.fetchone() == expected_total

        cursor.execute(
            """
            SELECT
                ent_id,
                driver_id,
                pay_amount
            FROM
                fleet_financial_statements.finstmt_entry
            WHERE
                park_id = %s
                AND stmt_id = %s
                AND driver_id = ANY(%s)
            ORDER BY
                ent_id
        """,
            [
                defaults.PARK_ID,
                defaults.STMT_ID,
                [dp_id for dp_id, _ in request_entries],
            ],
        )
        assert cursor.fetchall() == [
            (ent_id, dp_id, amount)
            for ent_id, (dp_id, amount) in enumerate(request_entries, 1 + 5)
        ]


@pytest.mark.parametrize(
    ['request_entries', 'expected_total'],
    [
        (
            [('DRIVER-01', decimal.Decimal('0'))],
            (5, decimal.Decimal('14000'), decimal.Decimal('671.4285')),
        ),
        (
            [('DRIVER-01', decimal.Decimal('1000'))],
            (5, decimal.Decimal('15000'), decimal.Decimal('771.4285')),
        ),
        (
            [('DRIVER-01', decimal.Decimal('3000'))],
            (5, decimal.Decimal('17000'), decimal.Decimal('814.2856')),
        ),
        (
            [('DRIVER-01', decimal.Decimal('5000'))],
            (5, decimal.Decimal('19000'), decimal.Decimal('909.5237')),
        ),
        (
            [
                ('DRIVER-01', decimal.Decimal('5000')),
                ('DRIVER-03', decimal.Decimal('5000')),
            ],
            (5, decimal.Decimal('21000'), decimal.Decimal('1004.7618')),
        ),
    ],
)
async def test_update_entries(
        statement_edit,
        retrieve_driver_profiles,
        pg_database,
        request_entries,
        expected_total,
):
    response = await statement_edit(
        json={
            'entries': [
                {'driver_profile_id': dp_id, 'pay_amount': str(amount)}
                for dp_id, amount in request_entries
            ],
        },
    )
    assert response.status_code == 200, response.text

    assert retrieve_driver_profiles.times_called == 1
    request = retrieve_driver_profiles.next_call()['request']
    assert request.query == {'consumer': 'fleet-financial-statements'}
    assert jsonx.sort(request.json, 'id_in_set') == {
        'id_in_set': [f'PARK-01_{dp_id}' for dp_id, _ in request_entries],
    }

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                total_ent_count,
                total_pay_amount,
                total_bcm_amount
            FROM
                fleet_financial_statements.finstmt
            WHERE
                park_id = %s
                AND stmt_id = %s
        """,
            [defaults.PARK_ID, defaults.STMT_ID],
        )
        assert cursor.fetchone() == expected_total

        cursor.execute(
            """
            SELECT
                driver_id,
                pay_amount
            FROM
                fleet_financial_statements.finstmt_entry
            WHERE
                park_id = %s
                AND stmt_id = %s
                AND driver_id = ANY(%s)
            ORDER BY
                ent_id
        """,
            [
                defaults.PARK_ID,
                defaults.STMT_ID,
                [dp_id for dp_id, _ in request_entries],
            ],
        )
        assert cursor.fetchall() == request_entries


# @pytest.mark.parametrize(
#     ['request_entries', 'expected_total'],
#     [
#         (
#             ['DRIVER-01'],
#             (4, decimal.Decimal('14000'), decimal.Decimal('671.4285')),
#         ),
#         (
#             ['DRIVER-03'],
#             (4, decimal.Decimal('12000'), decimal.Decimal('628.5714')),
#         ),
#         (
#             ['DRIVER-05'],
#             (4, decimal.Decimal('10000'), decimal.Decimal('533.3333')),
#         ),
#         (
#             ['DRIVER-01', 'DRIVER-03'],
#             (3, decimal.Decimal('11000'), decimal.Decimal('528.5714')),
#         ),
#     ],
# )
# async def test_delete_entries(
#         statement_edit,
#         retrieve_driver_profiles,
#         pg_database,
#         request_entries,
#         expected_total,
# ):
#     response = await statement_edit(
#         json={
#             'entries': [
#                 {'driver_profile_id': dp_id} for dp_id in request_entries
#             ],
#         },
#     )
#     assert response.status_code == 200, response.text

#     assert retrieve_driver_profiles.times_called == 0

#     with pg_database.cursor() as cursor:
#         cursor.execute(
#             """
#             SELECT
#                 total_entries,
#                 total_pay_amount,
#                 total_bcm_amount
#             FROM
#                 fleet_financial_statements.financial_statement
#             WHERE
#                 id = %s
#         """,
#             [DEFAULT_STATEMENT_ID],
#         )
#         assert cursor.fetchone() == expected_total

#         cursor.execute(
#             """
#             SELECT
#                 driver_id,
#                 pay_amount
#             FROM
#                 fleet_financial_statements.financial_statement_entry
#             WHERE
#                 statement_id = %s
#                 AND driver_id = ANY(%s)
#             ORDER BY
#                 ordinal
#         """,
#             [DEFAULT_STATEMENT_ID, request_entries],
#         )
#         assert cursor.fetchall() == []


@pytest.mark.parametrize(
    ['request_json', 'expected_message'],
    [
        (
            {
                'commission_percent': str(
                    limits.MIN_COMMISSION_PERCENT - limits.DECIMAL2_EPSILON,
                ),
            },
            errors.EM_FIELD_NOT_GE.format(
                'commission_percent', limits.MIN_COMMISSION_PERCENT,
            ),
        ),
        (
            {
                'commission_percent': str(
                    limits.MAX_COMMISSION_PERCENT + limits.DECIMAL2_EPSILON,
                ),
            },
            errors.EM_FIELD_NOT_LE.format(
                'commission_percent', limits.MAX_COMMISSION_PERCENT,
            ),
        ),
        (
            {
                'commission_minimum': str(
                    limits.MIN_PAY_AMOUNT - limits.DECIMAL4_EPSILON,
                ),
            },
            errors.EM_FIELD_NOT_GE.format(
                'commission_minimum', limits.MIN_PAY_AMOUNT,
            ),
        ),
        (
            {
                'commission_minimum': str(
                    limits.MAX_PAY_AMOUNT + limits.DECIMAL4_EPSILON,
                ),
            },
            errors.EM_FIELD_NOT_LE.format(
                'commission_minimum', limits.MAX_PAY_AMOUNT,
            ),
        ),
        (
            {
                'entries': [
                    {'driver_profile_id': 'DRIVER-01', 'pay_amount': '1000'},
                    {'driver_profile_id': 'DRIVER-01', 'pay_amount': '2000'},
                ],
            },
            errors.EM_FIELD_NOT_UNIQUE_KEY.format(
                'entries.*.driver_profile_id',
            ),
        ),
        (
            {
                'entries': [
                    {'driver_profile_id': 'DRIVER-00', 'pay_amount': '1000'},
                ],
            },
            errors.EM_FIELD_NOT_DRIVER_PROFILE_ID.format(
                'entries.*.driver_profile_id',
            ),
        ),
        (
            {
                'entries': [
                    {
                        'driver_profile_id': 'DRIVER-01',
                        'pay_amount': str(
                            limits.MIN_PAY_AMOUNT - limits.DECIMAL4_EPSILON,
                        ),
                    },
                ],
            },
            errors.EM_FIELD_NOT_GE.format(
                'entries.*.pay_amount', limits.MIN_PAY_AMOUNT,
            ),
        ),
        (
            {
                'entries': [
                    {
                        'driver_profile_id': 'DRIVER-01',
                        'pay_amount': str(
                            limits.MAX_PAY_AMOUNT + limits.DECIMAL4_EPSILON,
                        ),
                    },
                ],
            },
            errors.EM_FIELD_NOT_LE.format(
                'entries.*.pay_amount', limits.MAX_PAY_AMOUNT,
            ),
        ),
    ],
)
async def test_invalid_argument(
        statement_edit,
        retrieve_driver_profiles,
        request_json,
        expected_message,
):
    response = await statement_edit(json=request_json)
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': errors.EC_INVALID_ARGUMENT,
        'message': expected_message,
    }


async def test_does_not_exists(statement_edit, retrieve_driver_profiles):
    response = await statement_edit(id='ffffffff-ffff-ffff-ffff-ffffffffffff')
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': errors.EC_DOES_NOT_EXIST,
        'message': errors.EM_DOES_NOT_EXIST,
    }

    assert retrieve_driver_profiles.times_called == 0


async def test_has_been_deleted(statement_edit, retrieve_driver_profiles):
    response = await statement_edit(id='00000000-0000-0000-0000-000000000002')
    assert response.status_code == 410, response.text
    assert response.json() == {
        'code': errors.EC_HAS_BEEN_DELETED,
        'message': errors.EM_HAS_BEEN_DELETED,
    }

    assert retrieve_driver_profiles.times_called == 0


async def test_has_been_changed(statement_edit, retrieve_driver_profiles):
    response = await statement_edit(revision=1)
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': errors.EC_HAS_BEEN_CHANGED,
        'message': errors.EM_HAS_BEEN_CHANGED,
    }

    assert retrieve_driver_profiles.times_called == 0


async def test_wrong_state(statement_edit, retrieve_driver_profiles):
    stmt_ext_id = '00000000-0000-0000-0000-000000000003'

    # should pass commission edit
    response = await statement_edit(
        id=stmt_ext_id, json={'commission_percent': '10'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'id': stmt_ext_id,
        'revision': 4,
        'status': 'executing',
    }
    assert retrieve_driver_profiles.times_called == 0

    # should not pass entries edit
    response = await statement_edit(
        id=stmt_ext_id,
        json={
            'entries': [
                {'driver_profile_id': 'DRIVER-01', 'pay_amount': '100'},
            ],
        },
    )
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': errors.EC_WRONG_STATE,
        'message': errors.EM_WRONG_STATE,
    }
    assert retrieve_driver_profiles.times_called == 1
