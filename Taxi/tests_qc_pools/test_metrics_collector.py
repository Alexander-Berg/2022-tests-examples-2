import pytest


@pytest.mark.now('2020-01-01T00:00:20+00:00')
@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
async def test_db_metrics_collector(taxi_qc_pools, testpoint):
    @testpoint('qc_pools_metrics_collector::metrics_collected')
    def task_finished(data):
        return data

    await taxi_qc_pools.run_periodic_task('qc_pools_metrics_collector')

    response = await task_finished.wait_call()
    assert response['data'] == {
        'pool1': {
            '$meta': {'solomon_children_labels': 'exam'},
            'dkvu': {
                'pass_count': 3,
                'pass_max_age_ms': 20000,
                'pass_min_age_ms': 10000,
            },
        },
        'pool2': {
            '$meta': {'solomon_children_labels': 'exam'},
            'dkk': {
                'pass_count': 1,
                'pass_max_age_ms': 15000,
                'pass_min_age_ms': 15000,
            },
        },
        'pool3': {
            '$meta': {'solomon_children_labels': 'exam'},
            'dkvu': {
                'pass_count': 1,
                'pass_max_age_ms': 19000,
                'pass_min_age_ms': 19000,
            },
        },
        '$meta': {'solomon_children_labels': 'pool'},
    }
