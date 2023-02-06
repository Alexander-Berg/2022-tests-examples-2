import pytest


TASK_NAME = 'logistic-supply-conductor-workshift-rule-version-display-enabler'


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions_undisplayed.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
    ],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_WORKSHIFT_RULE_VERSION_PUBLISHER_SETTINGS={
        'publish_period': 1,
        'check_migrated_period': 1,
        'enabled': True,
    },
)
@pytest.mark.parametrize(
    'init_sql, expected_display_versions, expected_rules_display_versions',
    [
        pytest.param(
            None, [(1,), (2,)], [{'rule_id': 2, 'display_version': 2}],
        ),
        pytest.param(
            None,
            [(1,), (2,)],
            [{'rule_id': 2, 'display_version': 2}],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor',
                files=['pg_workshift_slots_with_previous_version.sql'],
            ),
        ),
        pytest.param(
            """
            INSERT INTO
                logistic_supply_conductor.workshift_slots_migration_statuses
                (slot_id, migration_state, new_version)
            VALUES
                (4, 'awaiting_migration', 2),
                (5, 'awaiting_migration', 2),
                (6, 'awaiting_migration', 2)
            """,
            [(1,), (1,)],
            [],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor',
                files=['pg_workshift_slots_with_previous_version.sql'],
            ),
        ),
        pytest.param(
            """
            INSERT INTO
                logistic_supply_conductor.workshift_slots_migration_statuses
                (slot_id, migration_state, new_version)
            VALUES
                (4, 'awaiting_migration', 2),
                (5, 'awaiting_migration', 2),
                (6, 'awaiting_migration', 2),
                (4, 'migrated', 2),
                (5, 'migrated', 2)
            """,
            [(1,), (1,)],
            [],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor',
                files=['pg_workshift_slots_with_previous_version.sql'],
            ),
        ),
        pytest.param(
            """
            INSERT INTO
                logistic_supply_conductor.workshift_slots_migration_statuses
                (slot_id, migration_state, new_version)
            VALUES
                (4, 'awaiting_migration', 2),
                (5, 'awaiting_migration', 2),
                (6, 'awaiting_migration', 2),
                (6, 'migration_skipped', 2),
                (4, 'migrated', 2),
                (5, 'migrated', 2)
            """,
            [(1,), (2,)],
            [{'rule_id': 2, 'display_version': 2}],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor',
                files=['pg_workshift_slots_with_previous_version.sql'],
            ),
        ),
        pytest.param(
            """
            INSERT INTO
                logistic_supply_conductor.workshift_slots_migration_statuses
                (slot_id, migration_state, new_version)
            VALUES
                (4, 'awaiting_migration', 2),
                (5, 'awaiting_migration', 2),
                (6, 'awaiting_migration', 2),
                (6, 'migration_skipped', 2),
                (4, 'migrated', 2),
                (5, 'migrated', 2);

            UPDATE
                logistic_supply_conductor.workshift_rules w_r
            SET
                display_version = actual_version;
            """,
            [(1,), (2,)],
            [],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor',
                files=['pg_workshift_slots_with_previous_version.sql'],
            ),
        ),
        pytest.param(
            """
            INSERT INTO logistic_supply_conductor.workshift_rule_versions
            (rule_id,"version",publish_at,published_since,dispatch_priority,
            tags_on_subscription, order_source, employer_names, schedule,
            availability_courier_requirements, descriptive_items, free_time)
            VALUES
            (
                2,
                3,
                (current_timestamp - interval '30 days'),
                (current_timestamp - interval '30 days'),
                interval '60 seconds',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                interval '60 seconds'
            );

            UPDATE logistic_supply_conductor.workshift_rules
            SET
                actual_version = 3,
                last_known_version = 3
            WHERE
                id = 2;

            INSERT INTO
                logistic_supply_conductor.workshift_rule_version_stored_geoareas
                (workshift_rule_version_id, stored_geoarea_id)
            VALUES (4, 1);

            INSERT INTO logistic_supply_conductor.workshift_slots
                (workshift_slot_id,workshift_rule_version_id,stored_geoarea_id,
                siblings_group_id,week_day,time_start,time_stop,quota_ref_id)
            VALUES
            (
                '298b2b5f-0466-4c96-8785-f225e1ad73ea',
                4,
                1,
                1,
                'wednesday',
                '2033-04-06T08:00:00Z',
                '2033-04-06T20:00:00Z',
                1
            );

            INSERT INTO
                logistic_supply_conductor.workshift_slots_migration_statuses
                (slot_id, migration_state, new_version)
            VALUES
                (4, 'awaiting_migration', 2),
                (5, 'awaiting_migration', 2),
                (6, 'awaiting_migration', 2),
                (6, 'migration_skipped', 2),
                (4, 'migrated', 2),
                (5, 'migrated', 2),
                (8, 'awaiting_migration', 3),
                (8, 'migrated', 3);
            """,
            [(1,), (3,)],
            [{'rule_id': 2, 'display_version': 3}],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor',
                files=['pg_workshift_slots_with_previous_version.sql'],
            ),
        ),
    ],
)
async def test_display_enabler(
        taxi_logistic_supply_conductor,
        pgsql,
        testpoint,
        init_sql,
        expected_display_versions,
        expected_rules_display_versions,
):
    if init_sql is not None:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(init_sql)

    @testpoint('updated_rules_display_versions')
    def _tp_updated_rules_display_versions(actual_rules_display_versions):
        assert len(actual_rules_display_versions) == len(
            expected_rules_display_versions,
        )

        for actual, expected in zip(
                actual_rules_display_versions, expected_rules_display_versions,
        ):
            assert actual == expected

    await taxi_logistic_supply_conductor.run_task(TASK_NAME)

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT display_version
    FROM logistic_supply_conductor.workshift_rules
    ORDER BY id ASC
    """,
    )
    assert list(cursor) == expected_display_versions
