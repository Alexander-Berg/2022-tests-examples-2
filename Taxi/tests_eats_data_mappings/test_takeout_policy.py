import pytest


async def test_inaccessible_from_outside(taxi_eats_data_mappings):
    response = await taxi_eats_data_mappings.post(
        '/service/v1/takeout_policies', json={'takeout_policies': ['policy']},
    )
    assert response.status_code == 404


async def test_parsing_error(taxi_eats_data_mappings_monitor):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/takeout_policies', json={},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'db_state, request_json, db_expected',
    [
        pytest.param(
            [], {'takeout_policies': ['policy']}, ['policy'], id='add single',
        ),
        pytest.param(
            ['policy1', 'policy2'],
            {'takeout_policies': ['policy3']},
            ['policy1', 'policy2', 'policy3'],
            id='add multiple',
        ),
        pytest.param(
            ['policy1', 'policy2', 'policy3'],
            {'takeout_policies': ['policy3', 'policy4']},
            ['policy1', 'policy2', 'policy3', 'policy4'],
            id='add with intersections',
        ),
    ],
)
async def test_add_entity(
        taxi_eats_data_mappings_monitor,
        pgsql,
        db_state,
        request_json,
        db_expected,
):
    if db_state:
        values = ','.join('(\'{}\')'.format(x) for x in db_state)
        request = (
            'INSERT INTO eats_data_mappings.takeout_policy(name) VALUES {};'.format(
                values,
            )
        )
        cursor = pgsql['eats_data_mappings'].cursor()
        cursor.execute(request)

    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/takeout_policies', json=request_json,
    )
    assert response.status_code == 200

    cursor = pgsql['eats_data_mappings'].cursor()
    cursor.execute('SELECT name from eats_data_mappings.takeout_policy')
    entities = list(x[0] for x in cursor)

    assert set(db_expected) == set(entities)
