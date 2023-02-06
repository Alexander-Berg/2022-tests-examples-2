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
async def test_workshift_quota(taxi_logistic_supply_conductor, pgsql):
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
                                        'day': 'wednesday',
                                        'quota': 1007,
                                        'quota_revision': 1,
                                    },
                                    {
                                        'day': 'saturday',
                                        'quota': 1009,
                                        'quota_revision': 1,
                                    },
                                ],
                                'time_start': '20:34',
                                'duration': 1800,
                            },
                        },
                        {
                            'weekdays_time': {
                                'selected_days_with_quota': [
                                    {
                                        'day': 'monday',
                                        'quota': 1004,
                                        'quota_revision': 1,
                                    },
                                    {
                                        'day': 'sunday',
                                        'quota': 1006,
                                        'quota_revision': 1,
                                    },
                                ],
                                'time_start': '18:34',
                                'duration': 1800,
                            },
                        },
                        {
                            'weekdays_time': {
                                'selected_days_with_quota': [
                                    {
                                        'day': 'wednesday',
                                        'quota': 1001,
                                        'quota_revision': 1,
                                    },
                                    {
                                        'day': 'sunday',
                                        'quota': 1003,
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

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT siblings_group_id, week_day, quota, quota_revision
    FROM logistic_supply_conductor.slot_quotas
    ORDER BY id
    """,
    )

    assert list(cursor) == [
        (1, 'wednesday', 1007, 1),
        (1, 'saturday', 1009, 1),
        (2, 'monday', 1004, 1),
        (2, 'sunday', 1006, 1),
        (3, 'wednesday', 1001, 1),
        (3, 'sunday', 1003, 1),
    ]

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
                                    'day': 'wednesday',
                                    'quota': 1007,
                                    'quota_revision': 1,
                                },
                                {
                                    'day': 'saturday',
                                    'quota': 1009,
                                    'quota_revision': 1,
                                },
                            ],
                            'time_start': '20:34',
                            'duration': 1800,
                        },
                        'siblings_group_id': 1,
                    },
                    {
                        'weekdays_time': {
                            'selected_days_with_quota': [
                                {
                                    'day': 'monday',
                                    'quota': 1004,
                                    'quota_revision': 1,
                                },
                                {
                                    'day': 'sunday',
                                    'quota': 1006,
                                    'quota_revision': 1,
                                },
                            ],
                            'time_start': '18:34',
                            'duration': 1800,
                        },
                        'siblings_group_id': 2,
                    },
                    {
                        'weekdays_time': {
                            'selected_days_with_quota': [
                                {
                                    'day': 'wednesday',
                                    'quota': 1001,
                                    'quota_revision': 1,
                                },
                                {
                                    'day': 'sunday',
                                    'quota': 1003,
                                    'quota_revision': 1,
                                },
                            ],
                            'time_start': '12:34',
                            'duration': 3600,
                        },
                        'siblings_group_id': 3,
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

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/create',
        json={
            'workshift_rule_id': CORRECT_RULE_ID,
            'last_known_version': 1,
            'sensitive_settings': {
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
                                        'quota': 1001,
                                        'quota_revision': 1,
                                    },
                                    {
                                        'day': 'friday',
                                        'quota': 1000002,
                                        'quota_revision': 1,
                                    },
                                    {'day': 'saturday', 'quota': 1000004},
                                ],
                                'time_start': '12:34',
                                'duration': 3600,
                            },
                            'siblings_group_id': 3,
                        },
                        {
                            'weekdays_time': {
                                'selected_days_with_quota': [
                                    {'day': 'tuesday', 'quota': 1},
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

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT siblings_group_id, week_day, quota, quota_revision
    FROM logistic_supply_conductor.slot_quotas
    ORDER BY id
    """,
    )

    assert list(cursor) == [
        (1, 'wednesday', 1007, 1),
        (1, 'saturday', 1009, 1),
        (2, 'monday', 1004, 1),
        (2, 'sunday', 1006, 1),
        (3, 'wednesday', 1001, 1),
        (3, 'sunday', 1003, 1),
        (3, 'monday', 1000001, 1),
        (3, 'friday', 1000002, 1),
        (3, 'saturday', 1000004, 1),
        (4, 'tuesday', 1, 1),
    ]

    response = await taxi_logistic_supply_conductor.get(
        'admin/v1/workshift-rule/version/info',
        params={
            'workshift_rule_id': CORRECT_RULE_ID,
            'workshift_rule_version': 2,
        },
    )

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/quota/update',
        json={
            'quotas': [
                {
                    'revision': 1,
                    'quota': 10,
                    'siblings_id': 3,
                    'week_day': 'wednesday',
                },
            ],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT siblings_group_id, week_day, quota, quota_revision
    FROM logistic_supply_conductor.slot_quotas
    ORDER BY id
    """,
    )

    assert list(cursor) == [
        (1, 'wednesday', 1007, 1),
        (1, 'saturday', 1009, 1),
        (2, 'monday', 1004, 1),
        (2, 'sunday', 1006, 1),
        (3, 'wednesday', 10, 2),
        (3, 'sunday', 1003, 1),
        (3, 'monday', 1000001, 1),
        (3, 'friday', 1000002, 1),
        (3, 'saturday', 1000004, 1),
        (4, 'tuesday', 1, 1),
    ]

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/quota/update',
        json={
            'quotas': [
                {
                    'revision': 2,
                    'quota': 11,
                    'siblings_id': 3,
                    'week_day': 'wednesday',
                },
                {
                    'revision': 1,
                    'quota': 12,
                    'siblings_id': 3,
                    'week_day': 'monday',
                },
                {
                    'revision': 1,
                    'quota': 13,
                    'siblings_id': 2,
                    'week_day': 'monday',
                },
            ],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT siblings_group_id, week_day, quota, quota_revision
    FROM logistic_supply_conductor.slot_quotas
    ORDER BY id
    """,
    )

    assert list(cursor) == [
        (1, 'wednesday', 1007, 1),
        (1, 'saturday', 1009, 1),
        (2, 'monday', 13, 2),
        (2, 'sunday', 1006, 1),
        (3, 'wednesday', 11, 3),
        (3, 'sunday', 1003, 1),
        (3, 'monday', 12, 2),
        (3, 'friday', 1000002, 1),
        (3, 'saturday', 1000004, 1),
        (4, 'tuesday', 1, 1),
    ]


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
async def test_next_revision(taxi_logistic_supply_conductor, pgsql):
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
                                        'day': 'wednesday',
                                        'quota': 1007,
                                        'quota_revision': 1,
                                    },
                                ],
                                'time_start': '20:34',
                                'duration': 1800,
                            },
                        },
                    ],
                },
            },
            'publish_at': '2033-07-21T17:32:28Z',
        },
    )

    assert response.status_code == 200

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    UPDATE logistic_supply_conductor.slot_quotas
    SET quota_revision = 2
    """,
    )

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/create',
        json={
            'workshift_rule_id': CORRECT_RULE_ID,
            'last_known_version': 1,
            'sensitive_settings': {
                'workshift_schedule': {
                    'schedule_type': 'weekdays_time',
                    'groups': [
                        {
                            'weekdays_time': {
                                'selected_days_with_quota': [
                                    {
                                        'day': 'wednesday',
                                        'quota': 2,
                                        'quota_revision': 2,
                                    },
                                ],
                                'time_start': '12:34',
                                'duration': 3600,
                            },
                            'siblings_group_id': 1,
                        },
                    ],
                },
            },
            'publish_at': '2033-07-21T17:32:28Z',
        },
    )

    assert response.status_code == 200
