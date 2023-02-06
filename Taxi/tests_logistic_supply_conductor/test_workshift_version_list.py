import pytest

CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000001'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
    ],
)
async def test_workshift_version_list(taxi_logistic_supply_conductor, pgsql):
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
            },
            'publish_at': '2033-07-24T17:32:28Z',
        },
    )

    assert response.status_code == 200

    response = await taxi_logistic_supply_conductor.get(
        'admin/v1/workshift-rule/version/list',
        params={'workshift_rule_id': CORRECT_RULE_ID},
    )

    response_dict = response.json()

    assert response_dict == {
        'actual_versions': [
            {
                'version': 1,
                'is_active_now': True,
                'publish_at': '2033-07-24T17:32:28+00:00',
            },
        ],
    }

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/create',
        json={
            'workshift_rule_id': CORRECT_RULE_ID,
            'last_known_version': 1,
            'sensitive_settings': {
                'dispatch_priority': 60,
                'tags_on_subscription': ['bar'],
                'order_sources': ['b2b'],
                'allowed_employer_names': ['grocery'],
            },
            'publish_at': '2033-07-25T17:32:28Z',
        },
    )

    response = await taxi_logistic_supply_conductor.get(
        'admin/v1/workshift-rule/version/list',
        params={'workshift_rule_id': CORRECT_RULE_ID},
    )

    response_dict = response.json()

    assert response_dict == {
        'actual_versions': [
            {
                'is_active_now': True,
                'publish_at': '2033-07-24T17:32:28+00:00',
                'version': 1,
            },
            {
                'is_active_now': False,
                'publish_at': '2033-07-25T17:32:28+00:00',
                'version': 2,
            },
        ],
    }

    response = await taxi_logistic_supply_conductor.get(
        'admin/v1/workshift-rule/version/list',
        params={'workshift_rule_id': INCORRECT_RULE_ID},
    )
    assert response.status_code == 404

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/remove',
        json={
            'workshift_rule_id': CORRECT_RULE_ID,
            'version': 2,
            'revision': 1,
        },
    )

    assert response.status_code == 200

    response = await taxi_logistic_supply_conductor.get(
        'admin/v1/workshift-rule/version/list',
        params={'workshift_rule_id': CORRECT_RULE_ID},
    )
    assert response.status_code == 200

    response_dict = response.json()

    assert response_dict == {
        'actual_versions': [
            {
                'version': 1,
                'is_active_now': True,
                'publish_at': '2033-07-24T17:32:28+00:00',
            },
        ],
    }
