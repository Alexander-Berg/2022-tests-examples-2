import pytest


CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000001'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'


TASK_NAME = 'logistic-supply-conductor-workshift-rule-archiver'


GET_STATES_REQUEST = """
    SELECT id, "state"
    FROM logistic_supply_conductor.workshift_metadata
    ORDER BY id ASC
    """


SET_STATE_REQUEST = """
    UPDATE logistic_supply_conductor.workshift_metadata
    SET "state"='{}'
    """


def get_states(pgsql):
    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(GET_STATES_REQUEST)
    return list(cursor)


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas.sql',
    ],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_WORKSHIFT_RULE_ARCHIVER_SETTINGS={
        'archive_period': 1,
        'enabled': True,
    },
)
@pytest.mark.parametrize(
    'initial_state, request_dict, response_code, resulting_state',
    [
        (
            'pending',
            {'workshift_rule_id': CORRECT_RULE_ID, 'metadata_revision': 1},
            200,
            'archived',
        ),
        (
            'pending',
            {'workshift_rule_id': INCORRECT_RULE_ID, 'metadata_revision': 1},
            404,
            None,
        ),
        (
            'pending',
            {'workshift_rule_id': CORRECT_RULE_ID, 'metadata_revision': 2},
            409,
            None,
        ),
        (
            'active',
            {'workshift_rule_id': CORRECT_RULE_ID, 'metadata_revision': 1},
            200,
            'archived',
        ),
        (
            'archived',
            {'workshift_rule_id': CORRECT_RULE_ID, 'metadata_revision': 1},
            409,
            None,
        ),
        pytest.param(
            'pending',
            {'workshift_rule_id': CORRECT_RULE_ID, 'metadata_revision': 1},
            200,
            'archiving',
            id='active reservations',
            marks=[
                pytest.mark.pgsql(
                    'logistic_supply_conductor',
                    files=[
                        'pg_workshift_quotas.sql',
                        'pg_workshift_slots.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            'pending',
            {'workshift_rule_id': CORRECT_RULE_ID, 'metadata_revision': 1},
            200,
            'archived',
            id='active reservations on different slot',
            marks=[
                pytest.mark.pgsql(
                    'logistic_supply_conductor',
                    files=[
                        'pg_workshift_quotas.sql',
                        'pg_workshift_slots_with_different_ids.sql',
                    ],
                ),
            ],
        ),
    ],
)
async def test_archiver(
        taxi_logistic_supply_conductor,
        pgsql,
        initial_state,
        request_dict,
        response_code,
        resulting_state,
):
    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(SET_STATE_REQUEST.format(initial_state))

    await taxi_logistic_supply_conductor.run_task(TASK_NAME)

    assert get_states(pgsql) == [(1, initial_state), (2, initial_state)]

    dry_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/archive',
        json=request_dict,
        params={'dry_run': True},
    )
    assert dry_response.status_code == response_code

    assert get_states(pgsql) == [(1, initial_state), (2, initial_state)]

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/archive', json=request_dict,
    )
    assert response.status_code == response_code

    if response_code == 200:
        assert get_states(pgsql) == [(1, 'archiving'), (2, initial_state)]

        await taxi_logistic_supply_conductor.run_task(TASK_NAME)

        assert get_states(pgsql) == [(1, resulting_state), (2, initial_state)]
