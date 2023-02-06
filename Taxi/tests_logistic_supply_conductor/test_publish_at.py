import pytest

CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000002'

CREATE_REQUEST = {
    'sensitive_settings': {
        'dispatch_priority': 42,
        'geoarea_ids': [{'name': 'second', 'geoarea_type': 'logistic_supply'}],
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
            'visibility_rules': [{'requirement_names': ['foo', 'bar']}],
        },
        'alias': 'kazan auto',
    },
}

CREATE_VERSION_REQUEST = {
    'workshift_rule_id': CORRECT_RULE_ID,
    'last_known_version': 2,
    'sensitive_settings': {
        'dispatch_priority': 60,
        'tags_on_subscription': ['bar'],
        'order_sources': ['b2b'],
        'allowed_employer_names': ['grocery'],
    },
}

UPDATE_VERSION_REQUEST = {
    'workshift_rule_id': CORRECT_RULE_ID,
    'version': 3,
    'revision': 1,
    'sensitive_settings': {
        'dispatch_priority': 120,
        'tags_on_subscription': ['bar'],
        'order_sources': ['b2b'],
        'allowed_employer_names': ['grocery'],
    },
}


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_correct_descriptive_items.sql',
        'pg_geoareas.sql',
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
async def test_publish_at(taxi_logistic_supply_conductor, pgsql):
    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/create', json=CREATE_REQUEST,
    )

    assert response.status_code == 200

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/create', json=CREATE_VERSION_REQUEST,
    )

    assert response.status_code == 200

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/update', json=UPDATE_VERSION_REQUEST,
    )

    assert response.status_code == 200
