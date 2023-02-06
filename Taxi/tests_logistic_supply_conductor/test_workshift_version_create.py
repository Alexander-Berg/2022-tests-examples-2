import datetime

import dateutil.parser
import pytest


CORRECT_RULE_ID_1 = 'af31c824-066d-46df-0001-000000000001'
CORRECT_RULE_ID_2 = 'af31c824-066d-46df-0001-000000000002'

NOW_PLUS_30_MINUTES_STR = (
    datetime.datetime.now(datetime.timezone.utc)
    + datetime.timedelta(minutes=30)
).isoformat()

ACTUAL_DATA = [
    (
        1,
        1,
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=90),
        None,
        datetime.timedelta(seconds=60),
        [],
        '{}',
        1,
        1,
        None,
        '{}',
        '{}',
        datetime.timedelta(seconds=60),
        '{}',
        [],
        1,
        datetime.datetime.now(datetime.timezone.utc),
    ),
    (
        2,
        2,
        datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(days=30),
        datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(days=30),
        datetime.timedelta(seconds=60),
        [],
        '{}',
        1,
        1,
        None,
        '{}',
        '{}',
        datetime.timedelta(seconds=60),
        '{}',
        ['vkusvill'],
        2,
        datetime.datetime.now(datetime.timezone.utc),
    ),
    (
        3,
        2,
        datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(minutes=30),
        datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(minutes=30),
        datetime.timedelta(seconds=120),
        ['foo', 'bar', 'baz'],
        '{}',
        1,
        2,
        None,
        '{"(\\"{foo,bar}\\")"}',
        '{"(name,42)"}',
        datetime.timedelta(seconds=3600),
        '{"(1,\\"(\\"\\"{wednesday,friday,sunday}\\"\\",08:30,01:00:00)\\")"}',
        [],
        3,
        datetime.datetime.now(datetime.timezone.utc),
    ),
]


def compare_db_contents(actual_db_contents, expected_db_contents):
    assert len(actual_db_contents) == len(expected_db_contents)

    for actual_tuple, expected_tuple in zip(
            actual_db_contents, expected_db_contents,
    ):
        actual = list(actual_tuple)
        expected = list(expected_tuple)
        assert len(actual) == len(expected)
        assert abs((actual[16] - expected[16]).total_seconds()) < 1800
        assert abs((actual[2] - expected[2]).total_seconds()) < 1800
        assert (actual[3] is None and expected[3] is None) or abs(
            (actual[3] - expected[3]).total_seconds(),
        ) < 1800
        del actual[16:17]
        del expected[16:17]
        del actual[2:4]
        del expected[2:4]
        assert actual == expected


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_correct_descriptive_items.sql',
        'pg_geoareas.sql',
        'pg_courier_requirements_x_y_z.sql',
    ],
)
@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
        'edits': {'enabled': True, 'threshold': 3600},
        'geoareas_types_of_interest': ['logistic_supply'],
    },
)
@pytest.mark.parametrize(
    'request_dict, response_code, expected_db_contents',
    [
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID_2,
                'last_known_version': 2,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            200,
            ACTUAL_DATA
            + [
                (
                    5,
                    2,
                    dateutil.parser.isoparse('2033-07-21T17:32:28Z'),
                    None,
                    datetime.timedelta(seconds=60),
                    ['bar'],
                    '{B2B}',
                    1,
                    3,
                    None,
                    '{"(\\"{foo,bar}\\")"}',
                    '{"(name,42)"}',
                    datetime.timedelta(seconds=3600),
                    '{"(1,\\"(\\"\\"{wednesday,friday,sunday}'
                    '\\"\\",08:30,01:00:00)\\")"}',
                    ['grocery'],
                    5,
                    datetime.datetime.now(datetime.timezone.utc),
                ),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID_2,
                'last_known_version': 2,
                'sensitive_settings': {
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [
                            {
                                'weekdays_time': {
                                    'selected_days_with_quota': [
                                        {'day': 'monday', 'quota': 1000001},
                                        {'day': 'wednesday', 'quota': 1000002},
                                        {'day': 'friday', 'quota': 1000003},
                                        {'day': 'sunday', 'quota': 1000004},
                                    ],
                                    'time_start': '12:34',
                                    'duration': 3600,
                                },
                                'siblings_group_id': 2,
                            },
                        ],
                    },
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            400,
            ACTUAL_DATA,
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID_2,
                'last_known_version': 2,
                'sensitive_settings': {
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [
                            {
                                'weekdays_time': {
                                    'selected_days_with_quota': [
                                        {'day': 'monday', 'quota': 1000001},
                                        {'day': 'wednesday', 'quota': 1000002},
                                        {'day': 'friday', 'quota': 1000003},
                                        {'day': 'sunday', 'quota': 1000004},
                                    ],
                                    'time_start': '12:34',
                                    'duration': 3600,
                                },
                                'siblings_group_id': 1,
                            },
                        ],
                    },
                    'availability_rules': [
                        {'requirement_names': ['x', 'y']},
                        {'requirement_names': ['z']},
                    ],
                    'descriptive_items': [
                        {'name': 'foo', 'value': 'bar'},
                        {'name': 'baz', 'value': '42'},
                    ],
                    'free_time': 7200,
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            200,
            ACTUAL_DATA
            + [
                (
                    5,
                    2,
                    dateutil.parser.isoparse('2033-07-21T17:32:28Z'),
                    None,
                    datetime.timedelta(seconds=120),
                    ['foo', 'bar', 'baz'],
                    '{}',
                    1,
                    3,
                    None,
                    '{"(\\"{x,y}\\")","({z})"}',
                    '{"(foo,bar)","(baz,42)"}',
                    datetime.timedelta(seconds=7200),
                    '{"(1,\\"(\\"\\"{monday,wednesday,friday,sunday}'
                    '\\"\\",12:34,01:00:00)\\")"}',
                    [],
                    5,
                    datetime.datetime.now(datetime.timezone.utc),
                ),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID_2,
                'last_known_version': 1,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            409,
            ACTUAL_DATA,
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID_2,
                'last_known_version': 100500,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            404,
            ACTUAL_DATA,
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID_1,
                'last_known_version': 1,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '{NOW_PLUS_30_MINUTES_STR}',
            },
            400,
            ACTUAL_DATA,
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID_2,
                'last_known_version': 0,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            400,
            ACTUAL_DATA,
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID_2,
                'last_known_version': 2,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['unknown_employer'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            400,
            ACTUAL_DATA,
        ),
    ],
)
async def test_create_version(
        taxi_logistic_supply_conductor,
        pgsql,
        request_dict,
        response_code,
        expected_db_contents,
):
    await taxi_logistic_supply_conductor.invalidate_caches()

    dry_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/create',
        json=request_dict,
        params={'dry_run': True},
    )

    assert dry_response.status_code == response_code

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
        SELECT *
        FROM logistic_supply_conductor.workshift_rule_versions
        ORDER BY id
        """,
    )
    compare_db_contents(list(cursor), ACTUAL_DATA)

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/create', json=request_dict,
    )

    assert response.status_code == response_code

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
        SELECT *
        FROM logistic_supply_conductor.workshift_rule_versions
        ORDER BY id
        """,
    )
    compare_db_contents(list(cursor), expected_db_contents)
