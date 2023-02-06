import decimal

from tests_fleet_financial_statements.common import defaults


async def test_parks_01(stq_prepare_worker, std_handlers, pg_database):
    await stq_prepare_worker()

    handler = std_handlers['/parks/driver-profiles/list']
    assert handler.times_called == 1
    request = handler.next_call()['request']
    assert request.json['limit'] == 100000
    assert request.json['query']['park'] == {'id': defaults.PARK_ID}


async def test_parks_02(stq_prepare_worker, std_handlers, pg_database):
    await stq_prepare_worker(stmt_id=2)

    handler = std_handlers['/parks/driver-profiles/list']
    assert handler.times_called == 1
    request = handler.next_call()['request']
    assert request.json['limit'] == 100000
    assert request.json['query']['park'] == {
        'id': defaults.PARK_ID,
        'driver_profile': {'work_rule_id': ['WORK_RULE_A', 'WORK_RULE_B']},
    }


async def test_parks_03(stq_prepare_worker, std_handlers, pg_database):
    await stq_prepare_worker(stmt_id=3)

    handler = std_handlers['/parks/driver-profiles/list']
    assert handler.times_called == 1
    request = handler.next_call()['request']
    assert request.json['limit'] == 100000
    assert request.json['query']['park'] == {
        'id': defaults.PARK_ID,
        'driver_profile': {'work_status': ['working', 'not_working']},
    }


async def test_fleet_transactions_api_01(
        stq_prepare_worker, std_handlers, pg_database,
):
    await stq_prepare_worker()

    handler = std_handlers[
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list'
    ]
    assert handler.times_called == 1
    request = handler.next_call()['request']
    assert request.json['query']['park'] == {
        'id': defaults.PARK_ID,
        'driver_profile': {
            'ids': [
                'DRIVER-01',
                'DRIVER-02',
                'DRIVER-03',
                'DRIVER-04',
                'DRIVER-05',
                'DRIVER-06',
                'DRIVER-07',
                'DRIVER-08',
                'DRIVER-09',
                'DRIVER-10',
            ],
        },
    }
    assert request.json['query']['balance'] == {
        'accrued_ats': ['2020-01-01T09:00:00+00:00'],
    }


async def test_fleet_transactions_api_02(
        stq_prepare_worker, std_handlers, pg_database,
):
    await stq_prepare_worker(stmt_id=2)

    handler = std_handlers[
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list'
    ]
    assert handler.times_called == 1
    request = handler.next_call()['request']
    assert request.json['query']['park'] == {
        'id': defaults.PARK_ID,
        'driver_profile': {
            'ids': [
                'DRIVER-01',
                'DRIVER-02',
                'DRIVER-05',
                'DRIVER-06',
                'DRIVER-08',
                'DRIVER-09',
            ],
        },
    }
    assert request.json['query']['balance'] == {
        'accrued_ats': ['2020-01-01T09:00:00+00:00'],
    }


async def test_fleet_transactions_api_03(
        stq_prepare_worker, std_handlers, pg_database,
):
    await stq_prepare_worker(stmt_id=3)

    handler = std_handlers[
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list'
    ]
    assert handler.times_called == 1
    request = handler.next_call()['request']
    assert request.json['query']['park'] == {
        'id': defaults.PARK_ID,
        'driver_profile': {
            'ids': [
                'DRIVER-01',
                'DRIVER-02',
                'DRIVER-03',
                'DRIVER-04',
                'DRIVER-05',
                'DRIVER-06',
                'DRIVER-07',
            ],
        },
    }
    assert request.json['query']['balance'] == {
        'accrued_ats': ['2020-01-01T09:00:00+00:00'],
    }


async def test_postgres_01(stq_prepare_worker, std_handlers, pg_database):
    await stq_prepare_worker()

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                stmt_revision,
                stmt_status,
                next_ent_id,
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
        assert cursor.fetchone() == (
            2,
            'draft',
            8,
            7,
            decimal.Decimal(1600),
            decimal.Decimal(850),
        )

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
            ORDER BY
                ent_id ASC
        """,
            [defaults.PARK_ID, defaults.STMT_ID],
        )
        assert cursor.fetchall() == [
            (1, 'DRIVER-01', decimal.Decimal(100)),
            (2, 'DRIVER-07', decimal.Decimal(100)),
            (3, 'DRIVER-02', decimal.Decimal(200)),
            (4, 'DRIVER-06', decimal.Decimal(200)),
            (5, 'DRIVER-03', decimal.Decimal(300)),
            (6, 'DRIVER-05', decimal.Decimal(300)),
            (7, 'DRIVER-04', decimal.Decimal(400)),
        ], 'Expected all drivers sorted by pay amount.'


async def test_postgres_02(stq_prepare_worker, std_handlers, pg_database):
    await stq_prepare_worker(stmt_id=2)

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                driver_id
            FROM
                fleet_financial_statements.finstmt_entry
            WHERE
                park_id = %s
                AND stmt_id = %s
            ORDER BY
                driver_id ASC
        """,
            [defaults.PARK_ID, 2],
        )
        assert cursor.fetchall() == [
            ('DRIVER-01',),
            ('DRIVER-02',),
            ('DRIVER-05',),
            ('DRIVER-06',),
        ], 'Expected only drivers with work rules [WORK_RULE_A, WORK_RULE_B]'


async def test_postgres_03(stq_prepare_worker, std_handlers, pg_database):
    await stq_prepare_worker(stmt_id=3)

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                driver_id
            FROM
                fleet_financial_statements.finstmt_entry
            WHERE
                park_id = %s
                AND stmt_id = %s
            ORDER BY
                driver_id ASC
        """,
            [defaults.PARK_ID, 3],
        )
        assert cursor.fetchall() == [
            ('DRIVER-01',),
            ('DRIVER-02',),
            ('DRIVER-03',),
            ('DRIVER-04',),
            ('DRIVER-05',),
            ('DRIVER-06',),
            ('DRIVER-07',),
        ], 'Expected only drivers with work statuses [working, not_working]'


async def test_reschedule_01(stq_prepare_worker, stq_prepare_client):
    await stq_prepare_worker(park_id='00000000000000000000000000000000')

    assert stq_prepare_client.times_called == 1, (
        'Financial statement does not exist in the database, so the task'
        ' needs to be rescheduled'
    )


async def test_reschedule_02(stq_prepare_worker, stq_prepare_client):
    await stq_prepare_worker(stmt_id=100)

    assert stq_prepare_client.times_called == 1, (
        'Financial statement does not exist in the database, so the task'
        ' needs to be rescheduled'
    )


async def test_reschedule_03(stq_prepare_worker, stq_prepare_client):
    await stq_prepare_worker(stmt_revision=2)

    assert stq_prepare_client.times_called == 1, (
        'The revision of financial statement in the database is less than'
        ' required, so the task needs to be rescheduled'
    )
