import pytest

from tests_driver_mode_index import utils


@pytest.mark.now('2020-01-07T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
@pytest.mark.pgsql('driver_mode_index', files=['init_db.sql'])
@pytest.mark.parametrize(
    'mode, drivers',
    (
        ('orders', []),
        ('driver_fix', ['dbid1_uuid1']),
        ('medic', ['dbid2_uuid2']),
        ('uberdriver', ['dbid3_uuid4', 'dbid3_uuid2', 'dbid3_uuid1']),
    ),
)
async def test_drivers(taxi_driver_mode_index, mode, drivers):
    response = await taxi_driver_mode_index.post(
        'v1/drivers', json={'mode': {'work_mode': mode}},
    )
    assert response.status_code == 200
    assert response.json() == {'drivers': drivers}


@pytest.mark.now('2020-01-07T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
@pytest.mark.pgsql('driver_mode_index', files=['init_db_limit_test.sql'])
async def test_drivers_limit(taxi_driver_mode_index):
    response = await taxi_driver_mode_index.post(
        'v1/drivers', json={'mode': {'work_mode': 'orders'}, 'limit': 3},
    )
    assert response.status_code == 200
    assert response.json() == {
        'drivers': ['dbid3_uuid1', 'dbid2_uuid1', 'dbid1_uuid1'],
        'next_cursor': '2',
    }
    response = await taxi_driver_mode_index.post(
        'v1/drivers',
        json={
            'mode': {'work_mode': 'orders'},
            'limit': 3,
            'cursor': response.json()['next_cursor'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'drivers': ['dbid6_uuid1', 'dbid5_uuid1', 'dbid4_uuid1'],
        'next_cursor': '5',
    }
    response = await taxi_driver_mode_index.post(
        'v1/drivers',
        json={
            'mode': {'work_mode': 'orders'},
            'limit': 3,
            'cursor': response.json()['next_cursor'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'drivers': ['dbid1_uuid2', 'dbid7_uuid1']}


@pytest.mark.now('2020-01-07T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
@pytest.mark.pgsql('driver_mode_index', files=['init_db_limit_test.sql'])
async def test_drivers_limit_equal_to_records_count(taxi_driver_mode_index):
    response = await taxi_driver_mode_index.post(
        'v1/drivers', json={'mode': {'work_mode': 'orders'}, 'limit': 8},
    )
    assert response.status_code == 200
    expected_response = {
        'drivers': [
            'dbid1_uuid2',
            'dbid7_uuid1',
            'dbid2_uuid1',
            'dbid6_uuid1',
            'dbid1_uuid1',
            'dbid4_uuid1',
            'dbid5_uuid1',
            'dbid3_uuid1',
        ],
        'next_cursor': '7',
    }
    response = response.json()
    assert response['next_cursor'] == expected_response['next_cursor']
    assert sorted(response['drivers']) == sorted(expected_response['drivers'])
    response = await taxi_driver_mode_index.post(
        'v1/drivers',
        json={
            'mode': {'work_mode': 'orders'},
            'limit': 3,
            'cursor': response['next_cursor'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'drivers': []}
