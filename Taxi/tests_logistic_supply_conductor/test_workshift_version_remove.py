import pytest


CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000001'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'

CHECK_REMOVED = """SELECT id
    FROM logistic_supply_conductor.workshift_rule_versions
    WHERE removed_at IS NOT NULL
    ORDER BY id"""


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
    'request_dict, response_code',
    [
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'version': 1,
                'revision': 1,
            },
            200,
        ),
        (
            {
                'workshift_rule_id': INCORRECT_RULE_ID,
                'version': 1,
                'revision': 1,
            },
            404,
        ),
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'version': 1,
                'revision': 2,
            },
            409,
        ),
        pytest.param(
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'version': 1,
                'revision': 1,
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
            },
            409,
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
                    'edits': {'enabled': True, 'threshold': 36000},
                    'geoareas_types_of_interest': [],
                },
            ),
        ),
    ],
)
async def test_remove_version(
        taxi_logistic_supply_conductor, pgsql, request_dict, response_code,
):
    dry_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/remove',
        json=request_dict,
        params={'dry_run': True},
    )
    assert dry_response.status_code == response_code

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(CHECK_REMOVED)

    assert not list(cursor)

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/remove', json=request_dict,
    )
    assert response.status_code == response_code

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(CHECK_REMOVED)

    if response_code == 200:
        assert list(cursor)[0][0] == 1
    else:
        assert not list(cursor)
