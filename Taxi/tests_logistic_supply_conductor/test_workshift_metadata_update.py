import datetime

import psycopg2
import pytest


DEFAULT_ELEMENT_CHECK = """
    SELECT w_r.workshift_rule_id, w_m.is_visible
    FROM logistic_supply_conductor.workshift_metadata as w_m
    INNER JOIN logistic_supply_conductor.workshift_rules as w_r
    ON w_r.id = w_m.rule_id
    ORDER BY w_m.id;
    """

FULL_METADATA_CHECK = """
    SELECT w_r.workshift_rule_id, w_m.is_visible, w_m.visibility_end_date,
           w_m.visibility_duration, w_m.alias
    FROM logistic_supply_conductor.workshift_metadata as w_m
    INNER JOIN logistic_supply_conductor.workshift_rules as w_r
    ON w_r.id = w_m.rule_id
    ORDER BY w_m.id;
    """

VISIBILITY_RULES_CHECK = """
    SELECT w_r.workshift_rule_id, w_m.visibility_courier_requirements
    FROM logistic_supply_conductor.workshift_metadata as w_m
    INNER JOIN logistic_supply_conductor.workshift_rules as w_r
    ON w_r.id = w_m.rule_id
    ORDER BY w_m.id;
    """

AUDIT_CHECK = """
        SELECT *
        FROM logistic_supply_conductor.workshift_metadata_audit
        ORDER BY id;
        """

CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000001'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'

RESPONSE_TIME_1 = datetime.datetime(
    2021,
    3,
    26,
    21,
    14,
    0,
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
)

RESPONSE_TIME_2 = datetime.datetime(
    2033,
    4,
    9,
    3,
    0,
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
)


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_courier_requirements.sql',
    ],
)
@pytest.mark.parametrize(
    'request_dict, response_code, sql_query, expected_select',
    [
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {'is_visible': True},
                    'revision': 1,
                },
            },
            200,
            DEFAULT_ELEMENT_CHECK,
            [
                ('af31c824-066d-46df-0001-000000000001', True),
                ('af31c824-066d-46df-0001-000000000002', False),
            ],
        ),
        (
            {
                'workshift_rule_id': INCORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {'is_visible': True},
                    'revision': 1,
                },
            },
            404,
            DEFAULT_ELEMENT_CHECK,
            [
                ('af31c824-066d-46df-0001-000000000001', False),
                ('af31c824-066d-46df-0001-000000000002', False),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {'is_visible': True},
                    'revision': 409,
                },
            },
            409,
            DEFAULT_ELEMENT_CHECK,
            [
                ('af31c824-066d-46df-0001-000000000001', False),
                ('af31c824-066d-46df-0001-000000000002', False),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {'is_visible': True},
                    'revision': 1,
                },
            },
            200,
            AUDIT_CHECK,
            [
                (
                    1,
                    1,
                    False,
                    1,
                    RESPONSE_TIME_2,
                    datetime.timedelta(days=90),
                    'pending',
                    '{}',
                    'moscow',
                    '{}',
                ),
                (
                    2,
                    2,
                    False,
                    1,
                    RESPONSE_TIME_2,
                    datetime.timedelta(days=90),
                    'pending',
                    '{}',
                    'kazan',
                    '{}',
                ),
                (
                    3,
                    1,
                    True,
                    2,
                    RESPONSE_TIME_2,
                    datetime.timedelta(days=90),
                    'pending',
                    '{}',
                    'moscow',
                    '{}',
                ),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {
                        'visibility_end_date': '2021-03-26T18:14:00Z',
                    },
                    'revision': 1,
                },
            },
            200,
            FULL_METADATA_CHECK,
            [
                (
                    'af31c824-066d-46df-0001-000000000001',
                    False,
                    RESPONSE_TIME_1,
                    datetime.timedelta(days=90),
                    'moscow',
                ),
                (
                    'af31c824-066d-46df-0001-000000000002',
                    False,
                    RESPONSE_TIME_2,
                    datetime.timedelta(days=90),
                    'kazan',
                ),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {'visibility_duration': 42},
                    'revision': 1,
                },
            },
            200,
            FULL_METADATA_CHECK,
            [
                (
                    'af31c824-066d-46df-0001-000000000001',
                    False,
                    RESPONSE_TIME_2,
                    datetime.timedelta(seconds=42),
                    'moscow',
                ),
                (
                    'af31c824-066d-46df-0001-000000000002',
                    False,
                    RESPONSE_TIME_2,
                    datetime.timedelta(days=90),
                    'kazan',
                ),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {},
                    'alias': 'elabuga vkusvill walking',
                    'revision': 1,
                },
            },
            200,
            FULL_METADATA_CHECK,
            [
                (
                    'af31c824-066d-46df-0001-000000000001',
                    False,
                    RESPONSE_TIME_2,
                    datetime.timedelta(days=90),
                    'elabuga vkusvill walking',
                ),
                (
                    'af31c824-066d-46df-0001-000000000002',
                    False,
                    RESPONSE_TIME_2,
                    datetime.timedelta(days=90),
                    'kazan',
                ),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {
                        'is_visible': True,
                        'visibility_duration': 42,
                        'visibility_end_date': '2021-03-26T18:14:00Z',
                    },
                    'alias': 'elabuga vkusvill walking',
                    'revision': 1,
                },
            },
            200,
            FULL_METADATA_CHECK,
            [
                (
                    'af31c824-066d-46df-0001-000000000001',
                    True,
                    RESPONSE_TIME_1,
                    datetime.timedelta(seconds=42),
                    'elabuga vkusvill walking',
                ),
                (
                    'af31c824-066d-46df-0001-000000000002',
                    False,
                    RESPONSE_TIME_2,
                    datetime.timedelta(days=90),
                    'kazan',
                ),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {'is_visible': 'hello world!'},
                    'revision': 1,
                },
            },
            400,
            DEFAULT_ELEMENT_CHECK,
            [
                ('af31c824-066d-46df-0001-000000000001', False),
                ('af31c824-066d-46df-0001-000000000002', False),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {'visibility_settings': {}, 'revision': 1},
            },
            400,
            DEFAULT_ELEMENT_CHECK,
            [
                ('af31c824-066d-46df-0001-000000000001', False),
                ('af31c824-066d-46df-0001-000000000002', False),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {
                        'visibility_rules': [{'requirement_names': ['foo']}],
                    },
                    'revision': 1,
                },
            },
            200,
            VISIBILITY_RULES_CHECK,
            [
                ('af31c824-066d-46df-0001-000000000001', '{"({foo})"}'),
                ('af31c824-066d-46df-0001-000000000002', '{}'),
            ],
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'metadata': {
                    'visibility_settings': {
                        'visibility_rules': [
                            {'requirement_names': ['incorrect']},
                        ],
                    },
                    'revision': 1,
                },
            },
            400,
            VISIBILITY_RULES_CHECK,
            [
                ('af31c824-066d-46df-0001-000000000001', '{}'),
                ('af31c824-066d-46df-0001-000000000002', '{}'),
            ],
        ),
    ],
)
async def test_update_metadata(
        taxi_logistic_supply_conductor,
        pgsql,
        request_dict,
        response_code,
        sql_query,
        expected_select,
):
    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/metadata/update', json=request_dict,
    )

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(sql_query)

    assert response.status_code == response_code
    assert list(cursor) == expected_select


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_courier_requirements.sql',
    ],
)
async def test_update_archive_metadata(taxi_logistic_supply_conductor, pgsql):
    await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/archive',
        json={'workshift_rule_id': CORRECT_RULE_ID, 'metadata_revision': 1},
    )

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/metadata/update',
        json={
            'workshift_rule_id': CORRECT_RULE_ID,
            'metadata': {
                'visibility_settings': {'is_visible': True},
                'revision': 1,
            },
        },
    )

    assert response.status_code == 400
