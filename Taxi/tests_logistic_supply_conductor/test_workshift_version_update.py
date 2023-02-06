import datetime

import pytest

CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000001'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'

NOW_PLUS_30_MINUTES_STR = (
    datetime.datetime.now(datetime.timezone.utc)
    + datetime.timedelta(minutes=30)
).isoformat()


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas.sql',
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
    'request_dict, response_code',
    [
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'version': 1,
                'revision': 1,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            200,
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'version': 1,
                'revision': 1,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '{NOW_PLUS_30_MINUTES_STR}',
            },
            400,
        ),
        (
            {
                'workshift_rule_id': INCORRECT_RULE_ID,
                'version': 1,
                'revision': 1,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            404,
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'version': 1,
                'revision': 2,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            409,
        ),
        pytest.param(
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'version': 1,
                'revision': 1,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            400,
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
                    'edits': {'enabled': False, 'threshold': 1},
                    'geoareas_types_of_interest': [],
                },
            ),
        ),
        pytest.param(
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'version': 1,
                'revision': 1,
                'sensitive_settings': {
                    'dispatch_priority': 60,
                    'tags_on_subscription': ['bar'],
                    'order_sources': ['b2b'],
                    'allowed_employer_names': ['grocery'],
                },
                'publish_at': '2033-07-21T17:32:28Z',
            },
            409,
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
                    'edits': {'enabled': True, 'threshold': 36000},
                    'geoareas_types_of_interest': ['logistic_supply'],
                },
            ),
        ),
    ],
)
async def test_update_version(
        taxi_logistic_supply_conductor, pgsql, request_dict, response_code,
):
    dry_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/update',
        json=request_dict,
        params={'dry_run': True},
    )
    assert dry_response.status_code == response_code

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/update', json=request_dict,
    )
    assert response.status_code == response_code

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """SELECT
            EXTRACT(epoch FROM dispatch_priority)::BIGINT,
            tags_on_subscription,
            LOWER(order_source::TEXT[]::TEXT)::TEXT[],
            employer_names::TEXT[]
           FROM logistic_supply_conductor.workshift_rule_versions
           WHERE id = 1""",
    )

    if response_code == 200:
        assert list(list(cursor)[0]) == list(
            request_dict['sensitive_settings'].values(),
        )
    else:
        assert list(list(cursor)[0]) != list(
            request_dict['sensitive_settings'].values(),
        )
