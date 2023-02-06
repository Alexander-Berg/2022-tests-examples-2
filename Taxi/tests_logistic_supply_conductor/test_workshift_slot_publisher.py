import datetime

import dateutil.parser
import pytest
import pytz


TASK_NAME = 'logistic-supply-conductor-workshift-slot-publisher'


def next_weekday(date, weekday):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


WED = next_weekday(
    datetime.datetime.now(pytz.timezone('utc')).replace(
        hour=8, minute=30, second=0, microsecond=0,
    ),
    2,
)
FRI = next_weekday(
    datetime.datetime.now(pytz.timezone('utc')).replace(
        hour=8, minute=30, second=0, microsecond=0,
    ),
    4,
)
SUN = next_weekday(
    datetime.datetime.now(pytz.timezone('utc')).replace(
        hour=8, minute=30, second=0, microsecond=0,
    ),
    6,
)
SUN_MSK = SUN - datetime.timedelta(hours=3)


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
    ],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_WORKSHIFT_SLOT_PUBLISHER_SETTINGS={
        'publish_period': 1,
        'enabled': True,
    },
)
@pytest.mark.parametrize(
    'init_sql, expected_stq_contents',
    [
        (
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true
            WHERE rule_id = 2
            """,
            [
                (
                    3,
                    1,
                    1,
                    'wednesday',
                    WED,
                    WED + datetime.timedelta(hours=1),
                    'Europe/Moscow',
                ),
                (
                    3,
                    1,
                    1,
                    'friday',
                    FRI,
                    FRI + datetime.timedelta(hours=1),
                    'Europe/Moscow',
                ),
                (
                    3,
                    1,
                    1,
                    'sunday',
                    SUN,
                    SUN + datetime.timedelta(hours=1),
                    'Europe/Moscow',
                ),
            ],
        ),
        (
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = false
            WHERE rule_id = 2
            """,
            [],
        ),
        (
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET state = 'archiving', is_visible = true
            WHERE rule_id = 2
            """,
            [],
        ),
        (
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET state = 'archived', is_visible = true
            WHERE rule_id = 2
            """,
            [],
        ),
        (
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET visibility_end_date = CURRENT_TIMESTAMP - '1 day'::INTERVAL,
                is_visible = true
            WHERE rule_id = 2
            """,
            [],
        ),
        (
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true
            WHERE rule_id = 2;
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true,
                visibility_end_date = CURRENT_TIMESTAMP + '1 year'::interval,
                state = 'active'
            WHERE rule_id = 1;
            UPDATE logistic_supply_conductor.workshift_rule_versions
            SET schedule = ARRAY[
                (
                    1,
                    (
                        ARRAY['wednesday', 'friday', 'sunday'],
                        '08:30',
                        '1 hour'
                    )::logistic_supply_conductor.weekdays_time_interval_without_quota__v1
                )
            ]::logistic_supply_conductor.workshift_schedule_siblings_group_without_quota__v1[]
            WHERE rule_id = 1;
            """,
            [
                (
                    1,
                    1,
                    1,
                    'wednesday',
                    WED,
                    WED + datetime.timedelta(hours=1),
                    'Europe/Moscow',
                ),
                (
                    1,
                    1,
                    1,
                    'friday',
                    FRI,
                    FRI + datetime.timedelta(hours=1),
                    'Europe/Moscow',
                ),
                (
                    1,
                    1,
                    1,
                    'sunday',
                    SUN,
                    SUN + datetime.timedelta(hours=1),
                    'Europe/Moscow',
                ),
                (
                    3,
                    1,
                    1,
                    'wednesday',
                    WED,
                    WED + datetime.timedelta(hours=1),
                    'Europe/Moscow',
                ),
                (
                    3,
                    1,
                    1,
                    'friday',
                    FRI,
                    FRI + datetime.timedelta(hours=1),
                    'Europe/Moscow',
                ),
                (
                    3,
                    1,
                    1,
                    'sunday',
                    SUN,
                    SUN + datetime.timedelta(hours=1),
                    'Europe/Moscow',
                ),
            ],
        ),
    ],
)
async def test_slot_publisher(
        taxi_logistic_supply_conductor,
        pgsql,
        stq,
        init_sql,
        expected_stq_contents,
):
    if init_sql is not None:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(init_sql)

    await taxi_logistic_supply_conductor.run_task(TASK_NAME)

    assert stq.logistic_supply_conductor_publish_slot.times_called == len(
        expected_stq_contents,
    )

    actual_stq_contents = sorted(
        [
            stq.logistic_supply_conductor_publish_slot.next_call()['kwargs']
            for _ in range(
                stq.logistic_supply_conductor_publish_slot.times_called,
            )
        ],
        key=lambda k: str(k['workshift_rule_version_id']) + k['week_day'][2],
    )
    for actual_dict, expected_tuple in zip(
            actual_stq_contents, expected_stq_contents,
    ):
        actual_dict.pop('log_extra')

        actual = list(actual_dict.values())
        expected = list(expected_tuple)

        actual[4] = dateutil.parser.isoparse(actual[4])
        actual[5] = dateutil.parser.isoparse(actual[5])

        assert len(actual) == len(expected)
        if (
                expected[4].weekday()
                == datetime.datetime.now(
                    pytz.timezone('Europe/Moscow'),
                ).weekday()
        ):
            # there can be some flaps, skipping date check for the same day
            # TODO : fix in CARGODEV-4417 (#4)
            del actual[4:6]
            del expected[4:6]
        del actual[0:1]
        del expected[0:1]
        assert actual == expected

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM logistic_supply_conductor.workshift_slots_migration_statuses
    """,
    )
    actual_audit_contents = list(cursor)
    assert actual_audit_contents == []


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_workshift_quotas.sql',
        'pg_geoareas_small.sql',
    ],
)
@pytest.mark.parametrize(
    'version_id, init_sql, expected_db_contents,'
    'expected_migrated_slots, expected_times_called, expected_audit_contents',
    [
        (
            3,
            None,
            [
                (
                    1,
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    'sunday',
                    SUN_MSK,
                    SUN_MSK + datetime.timedelta(hours=1),
                    3,
                    1,
                    4,
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    None,
                ),
            ],
            None,
            0,
            [],
        ),
        (
            3,
            """
            INSERT INTO logistic_supply_conductor.workshift_slots
                (workshift_slot_id, workshift_rule_version_id,
                stored_geoarea_id, siblings_group_id, week_day,
                time_start, time_stop, quota_ref_id)
            VALUES
            (
                'd361e7e0-728c-4ea6-8a68-591f7bfa93f5',
                3,
                1,
                1,
                'sunday',
                '{}',
                '{}',
                1
            );
            """.format(
                SUN_MSK.isoformat(),
                (SUN_MSK + datetime.timedelta(hours=1)).isoformat(),
            ),
            [
                (
                    1,
                    'd361e7e0-728c-4ea6-8a68-591f7bfa93f5',
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    'sunday',
                    SUN_MSK,
                    SUN_MSK + datetime.timedelta(hours=1),
                    3,
                    1,
                    1,
                    datetime.datetime.now(datetime.timezone.utc),
                    3,  # increased by 2 because of "insert on conflict update"
                    None,
                ),
            ],
            None,
            0,
            [],
        ),
        (
            3,
            """
            INSERT INTO logistic_supply_conductor.workshift_slots
                (workshift_slot_id, workshift_rule_version_id,
                stored_geoarea_id, siblings_group_id, week_day,
                time_start, time_stop, quota_ref_id)
            VALUES
            (
                'cb11228b-8ef1-42f2-beb7-6f5300c534aa',
                2,
                1,
                1,
                'sunday',
                '{}',
                '{}',
                1
            );
            """.format(
                SUN_MSK.isoformat(),
                (SUN_MSK + datetime.timedelta(hours=1)).isoformat(),
            ),
            [
                (
                    1,
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    'sunday',
                    SUN_MSK,
                    SUN_MSK + datetime.timedelta(hours=1),
                    2,
                    1,
                    1,
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    None,
                ),
                (
                    2,
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    'sunday',
                    SUN_MSK,
                    SUN_MSK + datetime.timedelta(hours=1),
                    3,
                    1,
                    1,
                    datetime.datetime.now(datetime.timezone.utc),
                    2,
                    None,
                ),
            ],
            [
                {
                    'slot_id': 'cb11228b-8ef1-42f2-beb7-6f5300c534aa',
                    'new_offer_info': {
                        'identity': {'slot_id': None, 'rule_version': 2},
                        'time_range': {
                            'begin': SUN_MSK.isoformat(),
                            'end': (
                                SUN_MSK + datetime.timedelta(hours=1)
                            ).isoformat(),
                        },
                    },
                },
            ],
            1,
            [(1, 1, 'migration_started', 2), (2, 1, 'migrated', 2)],
        ),
        (2, None, [], None, 0, []),
    ],
)
async def test_slot_publisher_stq(
        pgsql,
        stq_runner,
        mockserver,
        version_id,
        init_sql,
        expected_db_contents,
        expected_migrated_slots,
        expected_times_called,
        expected_audit_contents,
):
    if init_sql is not None:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(init_sql)

    @mockserver.json_handler(
        '/driver-mode-subscription/v1/logistic-workshifts/slots/change-offers',
    )
    def change_offers(request):
        actual_migrated_slots = request.json['changed']

        assert len(actual_migrated_slots) == len(expected_migrated_slots)

        response_changes = []

        for actual, expected in zip(
                actual_migrated_slots, expected_migrated_slots,
        ):
            assert actual['slot_id'] == expected['slot_id']
            assert (
                actual['new_offer_info']['identity']['rule_version']
                == expected['new_offer_info']['identity']['rule_version']
            )
            assert (
                actual['new_offer_info']['time_range']
                == expected['new_offer_info']['time_range']
            )

            response_changes.append(
                {
                    'slot_id': actual['slot_id'],
                    'new_identity': actual['new_offer_info']['identity'],
                    'status': 'success',
                },
            )

        return {'changed': response_changes, 'cancelled': []}

    await stq_runner.logistic_supply_conductor_publish_slot.call(
        task_id='foo',
        kwargs={
            'workshift_rule_version_id': version_id,
            'stored_geoarea_id': 1,
            'siblings_group_id': 1,
            'week_day': 'sunday',
            'time_start': SUN.isoformat(),
            'time_stop': (SUN + datetime.timedelta(hours=1)).isoformat(),
            'timezone': 'Europe/Moscow',
        },
        expect_fail=False,
    )

    assert change_offers.times_called == expected_times_called

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM logistic_supply_conductor.workshift_slots
    """,
    )
    actual_db_contents = list(cursor)

    assert len(actual_db_contents) == len(expected_db_contents)

    for actual_tuple, expected_tuple in zip(
            actual_db_contents, expected_db_contents,
    ):
        actual = list(actual_tuple)
        expected = list(expected_tuple)
        assert len(actual) == len(expected)
        assert abs((actual[10] - expected[10]).total_seconds()) < 1800
        del actual[10:11]
        del expected[10:11]
        assert abs((actual[2] - expected[2]).total_seconds()) < 1800
        del actual[2:3]
        del expected[2:3]
        if expected[1] is None:
            del actual[1:2]
            del expected[1:2]
        assert actual == expected

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT id, slot_id, migration_state, new_version
    FROM logistic_supply_conductor.workshift_slots_migration_statuses
    """,
    )
    actual_audit_contents = list(cursor)
    assert actual_audit_contents == expected_audit_contents


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
    ],
)
async def test_slot_closer_stq(pgsql, stq_runner, mockserver):
    expected_closed_slots = [
        {'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3'},
    ]
    expected_audit_contents = [
        (1, 3, 'cancellation_started', None),
        (2, 3, 'cancelled', None),
    ]

    @mockserver.json_handler(
        '/driver-mode-subscription/v1/logistic-workshifts/slots/change-offers',
    )
    def change_offers(request):
        actual_closed_slots = request.json['cancelled']
        assert actual_closed_slots == expected_closed_slots

        return {
            'changed': [],
            'cancelled': [
                {
                    'slot_id': actual_closed_slots[0]['slot_id'],
                    'status': 'success',
                },
            ],
        }

    await stq_runner.logistic_supply_conductor_close_slot.call(
        task_id='foo',
        kwargs={
            'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
            'version': 2,
        },
        expect_fail=False,
    )

    assert change_offers.times_called == 1

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT id, slot_id, migration_state, new_version
    FROM logistic_supply_conductor.workshift_slots_migration_statuses
    """,
    )
    actual_audit_contents = list(cursor)
    assert actual_audit_contents == expected_audit_contents
