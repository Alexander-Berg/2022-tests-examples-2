import pytest


async def test_inaccessible_from_outside(taxi_eats_data_mappings):
    response = await taxi_eats_data_mappings.post(
        '/service/v1/entities', json={'entities': ['some']},
    )
    assert response.status_code == 404


async def test_parsing_error(taxi_eats_data_mappings_monitor):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entities', json={},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'db_state, request_json, db_expected',
    [
        pytest.param([], {'entities': ['some']}, ['some'], id='add single'),
        pytest.param(
            ['some1', 'some2'],
            {'entities': ['some3']},
            ['some1', 'some2', 'some3'],
            id='add multiple',
        ),
        pytest.param(
            ['some1', 'some2', 'some3'],
            {'entities': ['some3', 'some4']},
            ['some1', 'some2', 'some3', 'some4'],
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
            'INSERT INTO eats_data_mappings.entity(name) VALUES {};'.format(
                values,
            )
        )
        cursor = pgsql['eats_data_mappings'].cursor()
        cursor.execute(request)

    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entities', json=request_json,
    )
    assert response.status_code == 200

    cursor = pgsql['eats_data_mappings'].cursor()
    cursor.execute('SELECT name from eats_data_mappings.entity')
    entities = list(x[0] for x in cursor)

    assert set(db_expected) == set(entities)
