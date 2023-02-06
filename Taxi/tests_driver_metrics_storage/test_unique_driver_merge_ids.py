import pytest


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('drivermetrics', files=['common.sql'])
async def test_unique_driver_merge_ids_handle(
        taxi_driver_metrics_storage, pgsql,
):
    cursor = pgsql['drivermetrics'].conn.cursor()
    cursor.execute('SELECT udid_id, merged_udid_id FROM common.merged_udids')
    result = cursor.fetchall()
    assert result == []

    for _ in range(2):
        response = await taxi_driver_metrics_storage.post(
            'internal/v1/unique_drivers/merge_ids',
            json={
                'events': [
                    {
                        'unique_driver': {'id': '110000000000000000000000'},
                        'merged_unique_driver': {
                            'id': '200000000000000000000000',
                        },
                    },
                    {
                        'unique_driver': {'id': '100000000000000000000000'},
                        'merged_unique_driver': {
                            'id': '220000000000000000000000',
                        },
                    },
                    {
                        'unique_driver': {'id': '100000000000000000000000'},
                        'merged_unique_driver': {
                            'id': '200000000000000000000000',
                        },
                    },
                ],
            },
        )
        assert response.status_code == 200
        assert response.json() == {}

        cursor = pgsql['drivermetrics'].conn.cursor()
        cursor.execute(
            'SELECT udid_id, merged_udid_id FROM common.merged_udids',
        )
        result = cursor.fetchall()
        # new indexes for udids 11000... and 22000...
        assert result == [(1, 1002), (1001, 2), (1001, 1002)]


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('drivermetrics', files=['common.sql'])
async def test_unique_driver_merged_ids(taxi_driver_metrics_storage):
    # TODO: check merged udids in handles EFFICIENCYDEV-18150
    pass
