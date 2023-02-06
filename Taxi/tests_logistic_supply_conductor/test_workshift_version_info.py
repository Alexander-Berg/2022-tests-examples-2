import pytest

CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000001'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'


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
async def test_workshift_version_info(taxi_logistic_supply_conductor, pgsql):
    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
        ALTER SEQUENCE schedule_siblings_group_id_seq RESTART WITH 1;
        """,
    )

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/update',
        json={
            'workshift_rule_id': CORRECT_RULE_ID,
            'version': 1,
            'revision': 1,
            'sensitive_settings': {
                'dispatch_priority': 60,
                'tags_on_subscription': ['bar'],
                'order_sources': ['b2b'],
                'allowed_employer_names': ['grocery'],
                'workshift_schedule': {
                    'schedule_type': 'weekdays_time',
                    'groups': [
                        {
                            'weekdays_time': {
                                'selected_days_with_quota': [
                                    {
                                        'day': 'monday',
                                        'quota': 1000001,
                                        'quota_revision': 1,
                                    },
                                    {
                                        'day': 'wednesday',
                                        'quota': 1000002,
                                        'quota_revision': 1,
                                    },
                                    {
                                        'day': 'friday',
                                        'quota': 1000003,
                                        'quota_revision': 1,
                                    },
                                    {
                                        'day': 'sunday',
                                        'quota': 1000004,
                                        'quota_revision': 1,
                                    },
                                ],
                                'time_start': '12:34',
                                'duration': 3600,
                            },
                        },
                    ],
                },
            },
            'publish_at': '2033-07-21T17:32:28Z',
        },
    )

    assert response.status_code == 200

    response = await taxi_logistic_supply_conductor.get(
        'admin/v1/workshift-rule/version/info',
        params={
            'workshift_rule_id': CORRECT_RULE_ID,
            'workshift_rule_version': 1,
        },
    )

    response_dict = response.json()
    assert response.status_code == 200

    assert response_dict == {
        'sensitive_settings': {
            'tags_on_subscription': ['bar'],
            'order_sources': ['b2b'],
            'allowed_employer_names': ['grocery'],
            'dispatch_priority': 60,
            'workshift_schedule': {
                'schedule_type': 'weekdays_time',
                'groups': [
                    {
                        'weekdays_time': {
                            'selected_days_with_quota': [
                                {
                                    'day': 'monday',
                                    'quota': 1000001,
                                    'quota_revision': 1,
                                },
                                {
                                    'day': 'wednesday',
                                    'quota': 1000002,
                                    'quota_revision': 1,
                                },
                                {
                                    'day': 'friday',
                                    'quota': 1000003,
                                    'quota_revision': 1,
                                },
                                {
                                    'day': 'sunday',
                                    'quota': 1000004,
                                    'quota_revision': 1,
                                },
                            ],
                            'time_start': '12:34',
                            'duration': 3600,
                        },
                        'siblings_group_id': 1,
                    },
                ],
            },
            'availability_rules': [],
            'descriptive_items': [],
            'free_time': 60,
            'revision': 2,
            'geoarea_ids': [
                {'name': 'second', 'geoarea_type': 'logistic_supply'},
            ],
        },
    }

    response = await taxi_logistic_supply_conductor.get(
        'admin/v1/workshift-rule/version/info',
        params={'workshift_rule_id': INCORRECT_RULE_ID},
    )
    assert response.status_code == 404

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/remove',
        json={
            'workshift_rule_id': CORRECT_RULE_ID,
            'version': 1,
            'revision': 2,
        },
    )

    response = await taxi_logistic_supply_conductor.get(
        'admin/v1/workshift-rule/version/info',
        params={'workshift_rule_id': CORRECT_RULE_ID},
    )
    assert response.status_code == 404
