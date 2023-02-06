import datetime

import pytest

JOB_NAME = 'cargo-claims-claims-cleaner'


def get_config(enabled, status, target_status):
    config = {
        'enabled': enabled,
        'expiration-rules': {
            status: {
                'expiration-time-hours': 1,
                'target-status': target_status,
            },
        },
        'query-limit': 1,
        'sleep-time-ms': 1000,
    }
    return config


EXPECTED = {'$meta': {'solomon_children_labels': 'claims_cleaner_statistics'}}


async def wait_iteration(taxi_cargo_claims, testpoint, expected_finish_status):
    @testpoint(JOB_NAME + '-finished')
    def finished(data):
        return data

    async with taxi_cargo_claims.spawn_task(JOB_NAME):
        finish_status = (await finished.wait_call())['data']
        assert finish_status == expected_finish_status
        return finish_status


NOW = datetime.datetime.now(datetime.timezone.utc)
NOW_STR = NOW.isoformat()


def insert_for_clean(cursor):
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.claims
        (id, corp_client_id, status, uuid_id,
        emergency_fullname,
        emergency_personal_phone_id, updated_ts, created_ts,
        idempotency_token, due)
        VALUES (2, '01234567890123456789012345678912',
                   'estimating',
                   'b04a64bb1d0147258337412c01176fa5',
                   'emergency_name',
                   '+79098887777_id',
                   '{NOW_STR}',
                   '{NOW_STR}',
                   'idempotency_token_hardcode_1',
                   '{NOW_STR}'
                ),
               (3, '01234567890123456789012345678912',
                   'estimating_failed',
                   'b04a64bb1d0147258337412c01176fa6',
                   'emergency_name',
                   '+79098887777_id',
                   '{NOW_STR}',
                   '{NOW_STR}',
                   'idempotency_token_hardcode_2',
                     NULL
                ),
               (4, '01234567890123456789012345678912',
                   'failed',
                   'b04a64bb1d0147258337412c01176fa7',
                   'emergency_name',
                   '+79098887777_id',
                   '{NOW_STR}',
                   '{NOW_STR}',
                   'idempotency_token_hardcode_3',
                     NULL
                )""",
    )
    assert cursor.rowcount == 3


@pytest.mark.parametrize('status', ('new', 'ready_for_approval'))
@pytest.mark.config(
    CARGO_CLAIMS_CLAIMS_CLEANER_WORKMODE=get_config(False, 'new', 'canceled'),
)
async def test_claims_cleaner(
        taxi_cargo_claims,
        testpoint,
        pgsql,
        create_default_claim,
        taxi_config,
        status,
):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        DROP TRIGGER claims_set_updated_ts ON cargo_claims.claims;
    """,
    )
    cursor.execute(
        f"""
        UPDATE cargo_claims.claims
        SET updated_ts = NOW() - INTERVAL '2 hours';
    """,
    )
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT updated_ts
        FROM cargo_claims.claims
    """,
    )
    taxi_config.set_values(
        dict(
            CARGO_CLAIMS_CLAIMS_CLEANER_WORKMODE=get_config(
                True, status, 'cancelled',
            ),
        ),
    )
    await taxi_cargo_claims.invalidate_caches()
    if status == 'ready_for_approval':
        EXPECTED['ready_for_approval'] = 0
    else:
        EXPECTED['new'] = 1
    await wait_iteration(taxi_cargo_claims, testpoint, EXPECTED)
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT status
        FROM cargo_claims.claims
    """,
    )
    assert list(cursor) == [('cancelled' if status == 'new' else 'new',)]
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT old_status, new_status, comment
        FROM cargo_claims.claim_audit
    """,
    )
    if status == 'new':
        assert list(cursor)[-1] == ('new', 'cancelled', 'expired status')
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        CREATE TRIGGER claims_set_updated_ts
    BEFORE UPDATE ON cargo_claims.claims
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_set_updated_ts();
    """,
    )


@pytest.mark.parametrize('status', ('estimating',))
@pytest.mark.config(
    CARGO_CLAIMS_CLAIMS_CLEANER_WORKMODE=get_config(
        False, 'estimating', 'failed',
    ),
)
async def test_specific_claims_cleaner(
        taxi_cargo_claims, testpoint, pgsql, taxi_config, status,
):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        DROP TRIGGER claims_set_updated_ts ON cargo_claims.claims;
    """,
    )

    cursor = pgsql['cargo_claims'].cursor()
    insert_for_clean(cursor)

    cursor.execute(
        f"""
        UPDATE cargo_claims.claims
        SET updated_ts = NOW() - INTERVAL '2 hours';
        """,
    )

    taxi_config.set_values(
        dict(
            CARGO_CLAIMS_CLAIMS_CLEANER_WORKMODE=get_config(
                True, status, 'failed',
            ),
        ),
    )
    await taxi_cargo_claims.invalidate_caches()
    EXPECTED[status] = 1

    await wait_iteration(taxi_cargo_claims, testpoint, EXPECTED)

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT status
        FROM cargo_claims.claims
        ORDER BY id
    """,
    )

    assert list(cursor) == [('failed',), ('estimating_failed',), ('failed',)]

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT old_status, new_status, comment
        FROM cargo_claims.claim_audit
    """,
    )

    assert cursor.fetchall()[-1] == ('estimating', 'failed', 'expired status')

    cursor.execute(
        f"""
        CREATE TRIGGER claims_set_updated_ts
    BEFORE UPDATE ON cargo_claims.claims
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_set_updated_ts();
    """,
    )
