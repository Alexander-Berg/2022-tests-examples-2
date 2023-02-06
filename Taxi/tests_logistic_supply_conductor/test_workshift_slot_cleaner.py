import pytest


TASK_NAME = 'logistic-supply-conductor-workshift-slot-cleaner'


async def impl(
        taxi_logistic_supply_conductor,
        pgsql,
        expected_db_slots,
        expected_db_quota_refs,
):
    await taxi_logistic_supply_conductor.invalidate_caches()

    await taxi_logistic_supply_conductor.run_task(TASK_NAME)

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT id, removed_at IS NULL
    FROM logistic_supply_conductor.workshift_slots
    ORDER BY id
    """,
    )
    actual_db_slots = list(cursor)
    assert actual_db_slots == expected_db_slots

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT id, removed_at IS NULL
    FROM logistic_supply_conductor.slot_quota_refs
    ORDER BY id
    """,
    )
    actual_db_quota_refs = list(cursor)
    assert actual_db_quota_refs == expected_db_quota_refs


@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_WORKSHIFT_SLOT_CLEANER_SETTINGS={
        'clean_period': 1,
        'clean_threshold': 86400,
        'enabled': True,
    },
)
@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots_outdated.sql',
    ],
)
@pytest.mark.parametrize(
    'expected_db_slots, expected_db_quota_refs',
    [
        pytest.param(
            [(1, False), (2, False), (3, False), (4, False), (5, False)],
            [(1, False), (2, False), (3, False)],
            id='clear all',
        ),
        pytest.param(
            [(1, False), (2, False), (3, True), (4, False), (5, False)],
            [(1, False), (2, False), (3, True)],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor',
                files=['pg_workshift_slot_subscribers.sql'],
            ),
            id='do not clear slots with subscribers',
        ),
    ],
)
async def test_workshift_slot_cleaner(
        taxi_logistic_supply_conductor,
        pgsql,
        expected_db_slots,
        expected_db_quota_refs,
):
    await impl(
        taxi_logistic_supply_conductor,
        pgsql,
        expected_db_slots,
        expected_db_quota_refs,
    )


@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_WORKSHIFT_SLOT_CLEANER_SETTINGS={
        'clean_period': 1,
        'clean_threshold': 86400,
        'enabled': True,
    },
)
@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots_outdated.sql',
    ],
)
@pytest.mark.parametrize(
    'expected_db_slots, expected_db_quota_refs',
    [
        pytest.param(
            [(1, True), (2, False), (3, False), (4, False), (5, False)],
            [(1, True), (2, False), (3, False)],
            id='clear all',
        ),
        pytest.param(
            [(1, True), (2, False), (3, True), (4, False), (5, False)],
            [(1, True), (2, False), (3, True)],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor',
                files=['pg_workshift_slot_subscribers.sql'],
            ),
            id='do not clear slots with subscribers',
        ),
    ],
)
async def test_workshift_slot_cleaner_with_reservations(
        taxi_logistic_supply_conductor,
        pgsql,
        expected_db_slots,
        expected_db_quota_refs,
):
    await impl(
        taxi_logistic_supply_conductor,
        pgsql,
        expected_db_slots,
        expected_db_quota_refs,
    )
