import pytest

CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000002'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_workshift_quotas.sql',
        'pg_two_geoareas_with_slots.sql',
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
                'geoarea_ids': [
                    {'name': 'second', 'geoarea_type': 'logistic_supply'},
                ],
            },
            200,
        ),
        (
            {
                'workshift_rule_id': INCORRECT_RULE_ID,
                'geoarea_ids': [
                    {'name': 'second', 'geoarea_type': 'logistic_supply'},
                ],
            },
            404,
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'geoarea_ids': [
                    {'name': 'error', 'geoarea_type': 'logistic_supply'},
                ],
            },
            400,
        ),
    ],
)
async def test_workshift_rule_split(
        taxi_logistic_supply_conductor, pgsql, request_dict, response_code,
):
    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
        ALTER SEQUENCE schedule_siblings_group_id_seq RESTART WITH 2;
        """,
    )

    dry_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/split',
        json=request_dict,
        params={'dry_run': True},
    )

    assert dry_response.status_code == response_code

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM logistic_supply_conductor.workshift_rules
    """,
    )
    assert len(list(cursor)) == 2

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/split', json=request_dict,
    )

    assert response.status_code == response_code
    if response_code != 200:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(
            """
        SELECT *
        FROM logistic_supply_conductor.workshift_rules
        """,
        )
        assert len(list(cursor)) == 2
        return

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM logistic_supply_conductor.workshift_rules
    """,
    )

    workshift_rules = list(cursor)

    for i, _ in enumerate(workshift_rules):
        workshift_rules[i] = list(workshift_rules[i])
        del workshift_rules[i][0:3]

    assert workshift_rules[1] == workshift_rules[2]

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM logistic_supply_conductor.workshift_metadata
    """,
    )

    workshift_metadata = list(cursor)

    for i, _ in enumerate(workshift_metadata):
        workshift_metadata[i] = list(workshift_metadata[i])
        del workshift_metadata[i][0:2]

    assert workshift_metadata[1] == workshift_metadata[2]

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM logistic_supply_conductor.workshift_rule_versions
    """,
    )

    workshift_rule_versions = list(cursor)

    for i, _ in enumerate(workshift_rule_versions):
        workshift_rule_versions[i] = list(workshift_rule_versions[i])
        del workshift_rule_versions[i][0:2]
        del workshift_rule_versions[i][11:15]

    assert workshift_rule_versions[1] == workshift_rule_versions[3]
    assert workshift_rule_versions[2] == workshift_rule_versions[4]

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT (tmp.schedule).siblings_group_id
    FROM (
        SELECT UNNEST(schedule) AS schedule
        FROM logistic_supply_conductor.workshift_rule_versions
        ) AS tmp
    """,
    )

    siblings_group_ids = list(cursor)

    assert siblings_group_ids == [(1,), (3,)]

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT workshift_rule_version_id
    FROM logistic_supply_conductor.workshift_rule_version_stored_geoareas
    """,
    )

    version_geoareas_version_ids = list(cursor)

    assert version_geoareas_version_ids == [(1,), (2,), (7,)]

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT workshift_rule_version_id, siblings_group_id
    FROM logistic_supply_conductor.workshift_slots
    """,
    )

    slots_version_ids_with_s_g_id = list(cursor)

    assert slots_version_ids_with_s_g_id == [(7, 3), (7, 3), (7, 3)]

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT id, week_day, quota
    FROM logistic_supply_conductor.slot_quotas
    """,
    )

    slots_quotas = list(cursor)

    assert slots_quotas == [
        (1, 'wednesday', 1001),
        (2, 'friday', 1002),
        (3, 'sunday', 1003),
        (7, 'wednesday', 1001),
        (8, 'friday', 1002),
        (9, 'sunday', 1003),
    ]

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT quota_id, id, siblings_group_ref_id
    FROM logistic_supply_conductor.slot_quota_refs
    """,
    )

    slots_quota_refs = list(cursor)

    assert slots_quota_refs == [
        ('af31c824-066d-46df-0001-100000000002', 2, 2),
        ('af31c824-066d-46df-0001-100000000003', 3, 3),
        ('af31c824-066d-46df-0001-100000000001', 1, 7),
    ]

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
        SELECT NEXTVAL('schedule_siblings_group_id_seq')
    """,
    )

    assert list(cursor) == [(4,)]
