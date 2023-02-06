import pytest


CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000002'


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
async def test_create_version_smoke(taxi_logistic_supply_conductor):
    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/create',
        json={
            'workshift_rule_id': CORRECT_RULE_ID,
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
                                'duration': 3600 + x * 3600,
                            },
                        }
                        for x in range(20)
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
        params={'dry_run': True},
    )

    assert response.status_code == 200
