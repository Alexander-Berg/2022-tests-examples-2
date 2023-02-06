import datetime

import pytest


CORRECT_RULE_ID_1 = 'af31c824-066d-46df-0001-000000000001'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'


TASK_NAME = 'logistic-supply-conductor-workshift-rule-version-publisher'


GET_STATES_REQUEST = """
    SELECT id, "state"
    FROM logistic_supply_conductor.workshift_metadata
    ORDER BY id ASC
    """

GET_METADATA_REQUEST = """
    SELECT rule_id, revision, "state"
    FROM logistic_supply_conductor.workshift_metadata
    ORDER BY id ASC
"""

GET_VERSIONS_REQUEST = """
    SELECT rule_id, "version", publish_at, published_since,
           revision, removed_at
    FROM logistic_supply_conductor.workshift_rule_versions
    ORDER BY id ASC
"""

GET_RULES_REQUEST = """
    SELECT id, actual_version
    FROM logistic_supply_conductor.workshift_rules
    ORDER BY id ASC
"""

GET_EXACT_PUBLISHED_SINCE = """
    SELECT published_since
    FROM logistic_supply_conductor.workshift_rule_versions
    WHERE rule_id = 4 AND "version" = 1
"""

SECOND_FAILURE_INJECTION = """
    UPDATE logistic_supply_conductor.workshift_rules
    SET actual_version = 2
    WHERE id = 4
"""

THIRD_FAILURE_INJECTION = """
    UPDATE logistic_supply_conductor.workshift_metadata
    SET "state" = 'archiving'::logistic_supply_conductor.workshift_rule_state
    WHERE rule_id = 4
"""

CREATE_REQUEST = {
    'sensitive_settings': {
        'dispatch_priority': 42,
        'geoarea_ids': [{'name': 'first', 'geoarea_type': 'logistic_supply'}],
        'order_sources': ['b2b', 'c2c'],
        'allowed_employer_names': ['vkusvill'],
        'tags_on_subscription': ['moscow'],
        'workshift_schedule': {'schedule_type': 'weekdays_time', 'groups': []},
        'availability_rules': [
            {'requirement_names': ['x', 'y']},
            {'requirement_names': ['z']},
        ],
        'descriptive_items': [
            {'name': 'foo', 'value': 'bar'},
            {'name': 'baz', 'value': '42'},
        ],
        'free_time': 42,
    },
    'metadata': {
        'visibility_settings': {
            'is_visible': True,
            'visibility_duration': 3600,
            'visibility_end_date': '2021-03-30T18:14:00Z',
            'visibility_rules': [
                {'requirement_names': ['foo', 'bar']},
                {'requirement_names': ['baz']},
            ],
        },
    },
    'publish_at': '2050-03-29T18:14:00Z',
}

GET_VERSIONS_RESPONSE = [
    [1, 1, 1],
    [2, 1, 1],
    [2, 2, 1],
    [2, 3, 1],
    [2, 4, 1],
    [2, 5, 1],
    [3, 1, 1],
    [4, 1, 1],
    [5, 1, 1],
]


def check_versions(pg_versions_data, removed, archived, not_visible, failed):
    list_len = len(pg_versions_data)
    for i in range(list_len):
        if (
                i in removed
                or pg_versions_data[i][2]
                >= datetime.datetime.now(datetime.timezone.utc)
                or i in archived
                or i in failed
                or i in not_visible
        ):
            assert pg_versions_data[i][3] is None
            if i in removed:
                assert pg_versions_data[i][5] is not None
        else:
            assert pg_versions_data[i][3] < datetime.datetime.now(
                datetime.timezone.utc,
            ) + datetime.timedelta(seconds=5)
            assert pg_versions_data[i][3] > datetime.datetime.now(
                datetime.timezone.utc,
            ) - datetime.timedelta(seconds=5)

        pg_versions_data[i] = list(pg_versions_data[i])
        del pg_versions_data[i][2:4]
        del pg_versions_data[i][3]


def get_data(pgsql, get_request):
    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(get_request)
    return list(cursor)


@pytest.mark.parametrize(
    'removed, archived, not_visible, failed,'
    ' actual_versions, get_metadata_response',
    [
        (
            [1, 2, 3, 4],
            [6],
            [8],
            [],
            [(1, 1), (2, 5), (3, 1), (4, 1), (5, 1)],
            [
                (1, 1, 'pending'),
                (2, 1, 'active'),
                (3, 1, 'archiving'),
                (4, 1, 'active'),
                (5, 1, 'pending'),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'logistic_supply_conductor', files=['pg_workshift_rule_publish.sql'],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_WORKSHIFT_RULE_VERSION_PUBLISHER_SETTINGS={
        'publish_period': 1,
        'enabled': True,
    },
    LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
        'edits': {'enabled': True, 'threshold': 3600},
        'publications': {'threshold': 1},
    },
)
async def test_version_publisher(
        taxi_logistic_supply_conductor,
        pgsql,
        removed,
        archived,
        not_visible,
        failed,
        actual_versions,
        get_metadata_response,
):

    assert get_data(pgsql, GET_STATES_REQUEST) == [
        (1, 'pending'),
        (2, 'pending'),
        (3, 'archiving'),
        (4, 'pending'),
        (5, 'pending'),
    ]

    assert get_data(pgsql, GET_RULES_REQUEST) == [
        (1, 1),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
    ]

    await taxi_logistic_supply_conductor.run_task(TASK_NAME)

    assert get_data(pgsql, GET_METADATA_REQUEST) == get_metadata_response

    pg_versions_data = get_data(pgsql, GET_VERSIONS_REQUEST)
    check_versions(pg_versions_data, removed, archived, not_visible, failed)
    assert pg_versions_data == GET_VERSIONS_RESPONSE

    assert get_data(pgsql, GET_RULES_REQUEST) == actual_versions


@pytest.mark.pgsql(
    'logistic_supply_conductor', files=['pg_workshift_rule_publish.sql'],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_WORKSHIFT_RULE_VERSION_PUBLISHER_SETTINGS={
        'publish_period': 1,
        'enabled': True,
    },
    LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
        'edits': {'enabled': True, 'threshold': 3600},
        'publications': {'threshold': 1},
    },
)
@pytest.mark.parametrize(
    'injection, actual_version',
    [(SECOND_FAILURE_INJECTION, 2), (THIRD_FAILURE_INJECTION, 1)],
)
async def test_version_publisher_rolled_back(
        taxi_logistic_supply_conductor,
        testpoint,
        pgsql,
        injection,
        actual_version,
):
    @testpoint('race_imitation')
    def race_imitation(data):
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(injection)

    await taxi_logistic_supply_conductor.run_task(TASK_NAME)

    assert race_imitation.times_called > 0

    assert get_data(pgsql, GET_EXACT_PUBLISHED_SINCE)[0][0] is None

    assert get_data(pgsql, GET_RULES_REQUEST) == [
        (1, 1),
        (2, 5),
        (3, 1),
        (4, actual_version),
        (5, 1),
    ]


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_visible.sql',
        'pg_workshift_rule_versions_unpublished.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
    ],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_WORKSHIFT_RULE_VERSION_PUBLISHER_SETTINGS={
        'publish_period': 1,
        'enabled': True,
    },
)
async def test_version_publisher_migration(
        taxi_logistic_supply_conductor, stq, pgsql,
):
    await taxi_logistic_supply_conductor.run_task(TASK_NAME)

    expected_close_stq_contents = sorted(
        [
            {'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3', 'version': 2},
            {'slot_id': '57079d82-fabd-4e70-9961-09a4733bbc57', 'version': 1},
            {'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508', 'version': 2},
        ],
        key=lambda k: k['slot_id'],
    )
    actual_close_stq_contents = sorted(
        [
            stq.logistic_supply_conductor_close_slot.next_call()['kwargs']
            for _ in range(
                stq.logistic_supply_conductor_close_slot.times_called,
            )
        ],
        key=lambda k: k['slot_id'],
    )
    assert len(actual_close_stq_contents) == len(expected_close_stq_contents)
    for actual_dict, expected_dict in zip(
            actual_close_stq_contents, expected_close_stq_contents,
    ):
        actual_dict.pop('log_extra')
        assert actual_dict == expected_dict

    expected_publish_stq_contents = [
        {
            'siblings_group_id': 1,
            'stored_geoarea_id': 1,
            'time_start': '2033-04-06T08:30:00+00:00',
            'time_stop': '2033-04-06T09:30:00+00:00',
            'timezone': 'Europe/Moscow',
            'week_day': 'wednesday',
            'workshift_rule_version_id': 4,
        },
    ]
    actual_publish_stq_contents = [
        stq.logistic_supply_conductor_publish_slot.next_call()['kwargs']
        for _ in range(stq.logistic_supply_conductor_publish_slot.times_called)
    ]
    assert len(actual_publish_stq_contents) == len(
        expected_publish_stq_contents,
    )
    for actual_dict, expected_dict in zip(
            actual_publish_stq_contents, expected_publish_stq_contents,
    ):
        actual_dict.pop('log_extra')
        assert actual_dict == expected_dict

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT slot_id, migration_state, new_version
    FROM logistic_supply_conductor.workshift_slots_migration_statuses
    ORDER BY slot_id
    """,
    )
    actual_audit_contents = list(cursor)
    assert actual_audit_contents == [
        (1, 'awaiting_migration', 3),
        (2, 'awaiting_cancellation', None),
        (3, 'awaiting_cancellation', None),
        (4, 'awaiting_cancellation', None),
    ]
