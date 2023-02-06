import pytest


CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000001'
CORRECT_RULE_ID_2 = 'af31c824-066d-46df-0001-000000000002'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'

ALIAS_MOSCOW = 'moscow'
ALIAS_KAZAN = 'kazan'


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas.sql',
    ],
)
@pytest.mark.parametrize(
    'limit_and_offset, request_dict, response_code, expected_response'
    ', total_items_count',
    [
        (
            {'offset': 0, 'limit': 2},
            {'filters': {}},
            200,
            [
                {
                    'workshift_rule_id': CORRECT_RULE_ID_2,
                    'last_known_version': 2,
                    'state': 'active',
                    'origin_typed_geoarea_ids': [
                        {'name': 'second', 'geoarea_type': 'logistic_supply'},
                    ],
                    'metadata': {
                        'visibility_settings': {
                            'is_visible': False,
                            'visibility_duration': 7776000,
                            'visibility_end_date': '2033-04-09T00:00:00+00:00',
                            'visibility_rules': [],
                        },
                        'revision': 1,
                        'transport_types': [],
                        'alias': ALIAS_KAZAN,
                    },
                },
                {
                    'workshift_rule_id': CORRECT_RULE_ID,
                    'last_known_version': 1,
                    'state': 'pending',
                    'origin_typed_geoarea_ids': [
                        {'name': 'second', 'geoarea_type': 'logistic_supply'},
                    ],
                    'metadata': {
                        'visibility_settings': {
                            'is_visible': False,
                            'visibility_duration': 7776000,
                            'visibility_end_date': '2033-04-09T00:00:00+00:00',
                            'visibility_rules': [],
                        },
                        'revision': 1,
                        'transport_types': [],
                        'alias': ALIAS_MOSCOW,
                    },
                },
            ],
            2,
        ),
        (
            {'offset': 1, 'limit': 1},
            {'filters': {}},
            200,
            [
                {
                    'workshift_rule_id': CORRECT_RULE_ID,
                    'last_known_version': 1,
                    'state': 'pending',
                    'origin_typed_geoarea_ids': [
                        {'name': 'second', 'geoarea_type': 'logistic_supply'},
                    ],
                    'metadata': {
                        'visibility_settings': {
                            'is_visible': False,
                            'visibility_duration': 7776000,
                            'visibility_end_date': '2033-04-09T00:00:00+00:00',
                            'visibility_rules': [],
                        },
                        'revision': 1,
                        'transport_types': [],
                        'alias': ALIAS_MOSCOW,
                    },
                },
            ],
            2,
        ),
        (
            {'offset': 0, 'limit': 2},
            {'filters': {'workshift_rule_id': CORRECT_RULE_ID}},
            200,
            [
                {
                    'workshift_rule_id': CORRECT_RULE_ID,
                    'last_known_version': 1,
                    'state': 'pending',
                    'origin_typed_geoarea_ids': [
                        {'name': 'second', 'geoarea_type': 'logistic_supply'},
                    ],
                    'metadata': {
                        'visibility_settings': {
                            'is_visible': False,
                            'visibility_duration': 7776000,
                            'visibility_end_date': '2033-04-09T00:00:00+00:00',
                            'visibility_rules': [],
                        },
                        'revision': 1,
                        'transport_types': [],
                        'alias': ALIAS_MOSCOW,
                    },
                },
            ],
            1,
        ),
        (
            {'offset': 0, 'limit': 2},
            {'filters': {'workshift_rule_id': INCORRECT_RULE_ID}},
            200,
            [],
            0,
        ),
        ({'offset': 0, 'limit': 2}, {}, 400, [], 0),
        ({}, {'filters': {'workshift_rule_id': 400}}, 400, [], 0),
    ],
)
@pytest.mark.now('2033-04-09T00:30:00Z')
async def test_get_list(
        taxi_logistic_supply_conductor,
        pgsql,
        limit_and_offset,
        request_dict,
        response_code,
        expected_response,
        total_items_count,
):
    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/list',
        json=request_dict,
        params=limit_and_offset,
    )

    assert response.status_code == response_code

    if response_code == 200:
        response_json = response.json()
        workshifts = response_json['workshifts']
        assert response_json['total_items_count'] == total_items_count
        for workshift in workshifts:
            if 'origin_typed_geoareas' in workshift.keys():
                for origin_typed_geoarea in workshift['origin_typed_geoareas']:
                    assert origin_typed_geoarea['stored_at'] is not None
                    origin_typed_geoarea['stored_at'] = '2033-04-09T00:30:00Z'
        assert workshifts == expected_response


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
async def test_last_known_version(taxi_logistic_supply_conductor, pgsql):
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
            'publish_at': '2033-07-21T17:32:28Z',
        },
    )

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT last_known_version
    FROM logistic_supply_conductor.workshift_rules
    """,
    )

    assert response.status_code == 200
    assert [(2,), (2,)] == list(cursor)
