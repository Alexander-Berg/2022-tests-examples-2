from tests_fleet_financial_statements.common import defaults


TR_CATERGORY_ID = 'partner_service_financial_statement'

TR_E_KEY = defaults.SERVICE_NAME + '/E/{}/{}'

TR_R_KEY = defaults.SERVICE_NAME + '/R/{}/{}'


EXPECTED_ENTRIES = [
    (5, 'DRIVER-07', 100),
    (7, 'DRIVER-06', 200),
    (9, 'DRIVER-05', 300),
]


async def test_fleet_transactions_api_01(
        std_handlers, stq_perform_worker, pg_database,
):
    stmt_id = 1
    await stq_perform_worker(stmt_id=stmt_id, do_revert=False)

    handler = std_handlers[
        (
            '/fleet-transactions-api'
            '/v1/parks/driver-profiles/transactions/by-platform'
        )
    ]
    assert handler.times_called == len(EXPECTED_ENTRIES)
    for (ent_id, driver_id, pay_amount) in EXPECTED_ENTRIES:
        request = handler.next_call()['request']
        headers, body = request.headers, request.json
        idempotency_token = TR_E_KEY.format(stmt_id, ent_id)
        assert headers['X-Ya-Service-Name'] == defaults.SERVICE_NAME
        assert headers['X-Idempotency-Token'] == idempotency_token
        assert body['park_id'] == defaults.PARK_ID
        assert body['driver_profile_id'] == driver_id
        assert body['category_id'] == TR_CATERGORY_ID
        assert body['amount'] == str(-pay_amount)
        assert body['description'] == f'{stmt_id}'


async def test_fleet_transactions_api_02(
        std_handlers, stq_perform_worker, pg_database,
):
    stmt_id = 2
    await stq_perform_worker(stmt_id=stmt_id, do_revert=True)

    handler = std_handlers[
        (
            '/fleet-transactions-api'
            '/v1/parks/driver-profiles/transactions/by-platform'
        )
    ]
    assert handler.times_called == len(EXPECTED_ENTRIES)
    for (ent_id, driver_id, pay_amount) in EXPECTED_ENTRIES:
        request = handler.next_call()['request']
        headers, body = request.headers, request.json
        idempotency_token = TR_R_KEY.format(stmt_id, ent_id)
        assert headers['X-Ya-Service-Name'] == defaults.SERVICE_NAME
        assert headers['X-Idempotency-Token'] == idempotency_token
        assert body['park_id'] == defaults.PARK_ID
        assert body['driver_profile_id'] == driver_id
        assert body['category_id'] == TR_CATERGORY_ID
        assert body['amount'] == str(+pay_amount)
        assert body['description'] == f'{stmt_id}'


async def test_postgres_01(std_handlers, stq_perform_worker, pg_database):
    await stq_perform_worker(stmt_id=1, do_revert=False)

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                stmt_revision,
                stmt_status
            FROM
                fleet_financial_statements.finstmt
            WHERE
                park_id = %s
                AND stmt_id = %s
        """,
            [defaults.PARK_ID, 1],
        )
        assert cursor.fetchone() == (6, 'executed')


async def test_postgres_02(std_handlers, stq_perform_worker, pg_database):
    await stq_perform_worker(stmt_id=2, do_revert=True)

    with pg_database.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                stmt_revision,
                stmt_status
            FROM
                fleet_financial_statements.finstmt
            WHERE
                park_id = %s
                AND stmt_id = %s
        """,
            [defaults.PARK_ID, 2],
        )
        assert cursor.fetchone() == (6, 'reverted')


async def test_reschedule_01(
        std_handlers, stq_perform_worker, stq_perform_client,
):
    await stq_perform_worker(park_id='PARK_XX')

    assert stq_perform_client.times_called == 1, (
        'Financial statement does not exist in the database, so the task'
        ' needs to be rescheduled'
    )


async def test_reschedule_02(
        std_handlers, stq_perform_worker, stq_perform_client,
):
    await stq_perform_worker(stmt_id=100)

    assert stq_perform_client.times_called == 1, (
        'Financial statement does not exist in the database, so the task'
        ' needs to be rescheduled'
    )


async def test_reschedule_03(
        std_handlers, stq_perform_worker, stq_perform_client,
):
    await stq_perform_worker(stmt_revision=6)

    assert stq_perform_client.times_called == 1, (
        'The revision of financial statement in the database is less than'
        ' required, so the task needs to be rescheduled'
    )
