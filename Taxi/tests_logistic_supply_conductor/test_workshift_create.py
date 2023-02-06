import datetime

import psycopg2
import pytest


WORHSHIFT_METADATA_CHECK = """
    SELECT *
    FROM logistic_supply_conductor.workshift_metadata
    ORDER BY id;
    """

WORHSHIFT_RULES_CHECK = """
    SELECT id, workshift_rule_id
    FROM logistic_supply_conductor.workshift_rules
    ORDER BY id;
    """

WORHSHIFT_RULE_VERSIONS_CHECK = """
    SELECT id, rule_id, removed_at,
           dispatch_priority, tags_on_subscription,
           order_source, employer_names,
           revision, "version"
    FROM logistic_supply_conductor.workshift_rule_versions
    ORDER BY id;
    """

GEOAREAS_CHECK = """
    SELECT g.id, g.ref_id, g.polygon, v.id, v.workshift_rule_version_id
    FROM
        logistic_supply_conductor.stored_geoareas g
        JOIN logistic_supply_conductor.workshift_rule_version_stored_geoareas v
            ON g.id = v.stored_geoarea_id
    ORDER BY g.id;
    """

DB_TIME = datetime.datetime(
    2033,
    4,
    9,
    3,
    0,
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
)

REQUEST_TIME = datetime.datetime(
    2021,
    3,
    30,
    21,
    14,
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
)

ALIAS_MOSCOW = 'moscow'
ALIAS_KAZAN = 'kazan'
ALIAS_REQUESTED = 'elabuga vkusvill walking'


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_correct_descriptive_items.sql',
        'pg_courier_requirements.sql',
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
    'request_dict, response_code, sql_query, expected_request_result',
    [
        (
            {
                'sensitive_settings': {
                    'dispatch_priority': 42,
                    'geoarea_ids': [
                        {'name': 'first', 'geoarea_type': 'logistic_supply'},
                    ],
                    'tags_on_subscription': ['moscow'],
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [],
                    },
                    'availability_rules': [
                        {'requirement_names': ['x', 'y']},
                        {'requirement_names': ['z']},
                    ],
                    'descriptive_items': [
                        {'name': 'foo', 'value': 'bar'},
                        {'name': 'baz'},
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
                        ],
                    },
                    'alias': ALIAS_REQUESTED,
                },
                'publish_at': '2050-03-29T18:14:00Z',
            },
            200,
            WORHSHIFT_METADATA_CHECK,
            [
                (
                    1,
                    1,
                    False,
                    1,
                    DB_TIME,
                    datetime.timedelta(days=90),
                    'pending',
                    '{}',
                    False,
                    ALIAS_MOSCOW,
                    '{}',
                ),
                (
                    2,
                    2,
                    False,
                    1,
                    DB_TIME,
                    datetime.timedelta(days=90),
                    'active',
                    '{}',
                    False,
                    ALIAS_KAZAN,
                    '{}',
                ),
                (
                    4,
                    4,
                    True,
                    1,
                    REQUEST_TIME,
                    datetime.timedelta(seconds=3600),
                    'pending',
                    '{"(\\"{foo,bar}\\")"}',
                    False,
                    ALIAS_REQUESTED,
                    '{}',
                ),
            ],
        ),
        (
            {
                'sensitive_settings': {
                    'dispatch_priority': 42,
                    'geoarea_ids': [
                        {'name': 'first', 'geoarea_type': 'logistic_supply'},
                    ],
                    'order_sources': ['b2b', 'c2c'],
                    'allowed_employer_names': ['vkusvill'],
                    'tags_on_subscription': ['moscow'],
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [],
                    },
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
                        ],
                    },
                    'alias': ALIAS_REQUESTED,
                },
                'publish_at': '2050-03-29T18:14:00Z',
            },
            200,
            WORHSHIFT_RULES_CHECK,
            [1, 2, 4],
        ),
        (
            {
                'sensitive_settings': {
                    'dispatch_priority': 42,
                    'geoarea_ids': [
                        {'name': 'first', 'geoarea_type': 'logistic_supply'},
                    ],
                    'order_sources': ['b2b', 'c2c'],
                    'allowed_employer_names': ['vkusvill'],
                    'tags_on_subscription': ['moscow'],
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [],
                    },
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
                        ],
                    },
                    'alias': ALIAS_REQUESTED,
                },
                'publish_at': '2050-03-29T18:14:00Z',
            },
            200,
            WORHSHIFT_RULE_VERSIONS_CHECK,
            [
                (
                    1,
                    1,
                    None,
                    datetime.timedelta(seconds=60),
                    [],
                    '{}',
                    [],
                    1,
                    1,
                ),
                (
                    2,
                    2,
                    None,
                    datetime.timedelta(seconds=60),
                    [],
                    '{}',
                    ['vkusvill'],
                    1,
                    1,
                ),
                (
                    3,
                    2,
                    None,
                    datetime.timedelta(seconds=120),
                    ['foo', 'bar', 'baz'],
                    '{}',
                    [],
                    1,
                    2,
                ),
                (
                    5,
                    4,
                    None,
                    datetime.timedelta(seconds=42),
                    ['moscow'],
                    '{C2C,B2B}',
                    ['vkusvill'],
                    1,
                    1,
                ),
            ],
        ),
        (
            {
                'sensitive_settings': {
                    'dispatch_priority': 42,
                    'geoarea_ids': [
                        {'name': 'first', 'geoarea_type': 'logistic_supply'},
                    ],
                    'order_sources': ['b2b', 'c2c'],
                    'allowed_employer_names': ['vkusvill'],
                    'tags_on_subscription': ['moscow'],
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [],
                    },
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
                        ],
                    },
                    'alias': ALIAS_REQUESTED,
                },
                'publish_at': '2050-03-29T18:14:00Z',
            },
            200,
            GEOAREAS_CHECK,
            [(2, 2, '((10,80),(80,80),(80,10),(10,10),(10,80))', 2, 5)],
        ),
        (
            {
                'sensitive_settings': {
                    'dispatch_priority': 42,
                    'geoarea_ids': [{'name': 'foo', 'geoarea_type': 'bar'}],
                    'order_sources': ['b2b', 'c2c'],
                    'allowed_employer_names': ['vkusvill'],
                    'tags_on_subscription': ['moscow'],
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [],
                    },
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
                        ],
                    },
                    'alias': ALIAS_REQUESTED,
                },
                'publish_at': '2050-03-29T18:14:00Z',
            },
            404,
            None,
            None,
        ),
        (
            {
                'sensitive_settings': {
                    'dispatch_priority': 42,
                    'geoarea_ids': [
                        {'name': 'first', 'geoarea_type': 'logistic_supply'},
                    ],
                    'order_sources': ['b2b', 'c2c'],
                    'allowed_employer_names': ['vkusvill'],
                    'tags_on_subscription': ['moscow'],
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [],
                    },
                    'availability_rules': [
                        {'requirement_names': ['x', 'y']},
                        {'requirement_names': ['z']},
                    ],
                    'descriptive_items': [
                        {'name': 'foo', 'value': 'bar'},
                        {'name': 'baz', 'value': '42'},
                        {'name': 'incorrect', 'value': 'incorrect'},
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
                        ],
                    },
                    'alias': ALIAS_REQUESTED,
                },
                'publish_at': '2050-03-29T18:14:00Z',
            },
            400,
            None,
            None,
        ),
        (
            {
                'sensitive_settings': {
                    'dispatch_priority': 42,
                    'geoarea_ids': [
                        {'name': 'first', 'geoarea_type': 'logistic_supply'},
                    ],
                    'order_sources': ['b2b', 'c2c'],
                    'allowed_employer_names': ['vkusvill'],
                    'tags_on_subscription': ['moscow'],
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [],
                    },
                    'availability_rules': [
                        {'requirement_names': ['x', 'incorrect']},
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
                        ],
                    },
                    'alias': ALIAS_REQUESTED,
                },
                'publish_at': '2050-03-29T18:14:00Z',
            },
            400,
            None,
            None,
        ),
        (
            {
                'sensitive_settings': {
                    'dispatch_priority': 42,
                    'geoarea_ids': [
                        {'name': 'first', 'geoarea_type': 'logistic_supply'},
                    ],
                    'order_sources': ['b2b', 'c2c'],
                    'allowed_employer_names': ['vkusvill'],
                    'tags_on_subscription': ['moscow'],
                    'workshift_schedule': {
                        'schedule_type': 'weekdays_time',
                        'groups': [],
                    },
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
                            {'requirement_names': ['incorrect', 'bar']},
                        ],
                    },
                    'alias': ALIAS_REQUESTED,
                },
                'publish_at': '2050-03-29T18:14:00Z',
            },
            400,
            None,
            None,
        ),
    ],
)
async def test_create_workshift(
        taxi_logistic_supply_conductor,
        pgsql,
        request_dict,
        response_code,
        sql_query,
        expected_request_result,
):
    await taxi_logistic_supply_conductor.invalidate_caches()

    dry_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/create',
        json=request_dict,
        params={'dry_run': True},
    )
    assert dry_response.status_code == response_code

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/create', json=request_dict,
    )
    assert response.status_code == response_code

    if sql_query is not None:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(sql_query)
        answer = list(cursor)
        if len(answer[0]) == 2:
            for i in range(3):
                assert None not in answer[i]
        else:
            assert answer == expected_request_result


CASUAL_REQUEST = {
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
            'visibility_duration': 0,
            'visibility_end_date': '',
            'visibility_rules': [{'requirement_names': ['foo', 'bar']}],
        },
        'alias': ALIAS_REQUESTED,
    },
    'publish_at': '2050-03-29T18:14:00Z',
}


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_correct_descriptive_items.sql',
    ],
)
@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
        'edits': {'enabled': True, 'threshold': 3600},
        'geoareas_types_of_interest': ['logistic_supply'],
    },
    LOGISTIC_SUPPLY_CONDUCTOR_VISIBILITY_SETTINGS={
        'lower_limit_visibility_end_date': {'threshold': 600, 'enabled': True},
        'upper_limit_visibility_end_date': {
            'threshold': 3600,
            'enabled': True,
        },
        'lower_limit_visibility_duration': {'threshold': 600, 'enabled': True},
        'upper_limit_visibility_duration': {
            'threshold': 1800,
            'enabled': True,
        },
    },
)
@pytest.mark.parametrize(
    'setting, response_code',
    [
        (
            {
                'end_date_addition': datetime.timedelta(minutes=1),
                'duration': 700,
            },
            400,
        ),
        (
            {
                'end_date_addition': datetime.timedelta(hours=2),
                'duration': 700,
            },
            400,
        ),
        (
            {
                'end_date_addition': datetime.timedelta(minutes=30),
                'duration': 60,
            },
            400,
        ),
        (
            {
                'end_date_addition': datetime.timedelta(minutes=30),
                'duration': 6000,
            },
            400,
        ),
        (
            {
                'end_date_addition': datetime.timedelta(minutes=30),
                'duration': 800,
            },
            200,
        ),
    ],
)
async def test_visibility_settings(
        taxi_logistic_supply_conductor, setting, response_code,
):
    request_dict = CASUAL_REQUEST
    now = datetime.datetime.now() - datetime.timedelta(hours=3)

    visibility_settings = request_dict['metadata']['visibility_settings']
    visibility_settings['visibility_end_date'] = (
        now + setting['end_date_addition']
    ).isoformat() + 'Z'
    visibility_settings['visibility_duration'] = setting['duration']

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/create', json=request_dict,
    )
    assert response.status_code == response_code
