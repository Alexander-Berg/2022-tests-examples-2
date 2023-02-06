import pytest


async def test_statistics_not_found(
        taxi_cargo_performer_fines, default_dbid_uuid,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']
    response = await taxi_cargo_performer_fines.post(
        '/performer/statistics',
        params={'driver_id': driver_id, 'park_id': park_id},
    )
    assert response.status_code == 200
    assert response.json() == {'driver_id': driver_id, 'park_id': park_id}


@pytest.mark.pgsql('cargo_performer_fines', files=['statistics.sql'])
async def test_performer_statistics(
        taxi_cargo_performer_fines, default_dbid_uuid,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']
    response = await taxi_cargo_performer_fines.post(
        '/performer/statistics',
        params={'driver_id': driver_id, 'park_id': park_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_id': driver_id,
        'park_id': park_id,
        'cancellations_statistics': {
            'cancellation_count_after_last_reset': 1,
            'completed_orders_count_after_last_cancellation': 4,
            'updated_ts': '2020-02-03T13:33:54.827958+00:00',
        },
    }
