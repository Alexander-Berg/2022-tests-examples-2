import pytest


@pytest.mark.now('2021-09-17T12:00:00+0000')
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.parametrize(
    'unique_driver_id, priority_value',
    (
        pytest.param('100000000000000000000000', 5),
        pytest.param('200000000000000000000000', 0),
        pytest.param('300000000000000000000000', -1),
        pytest.param('400000000000000000000000', -1),
    ),
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_priority_fetch_bulk(
        taxi_driver_metrics_storage,
        experiments3,
        load_json,
        unique_driver_id,
        priority_value,
):
    await taxi_driver_metrics_storage.invalidate_caches()
    await taxi_driver_metrics_storage.run_task('dist-version-refresher')

    exp3_recorder = experiments3.record_match_tries('completion_scores_levels')
    response = await taxi_driver_metrics_storage.post(
        '/v1/priority/fetch-bulk',
        json={
            'chunks': [
                {
                    'tariff_zone': 'custom-tariff_zone-1',
                    'drivers': [
                        {
                            'unique_driver_id': unique_driver_id,
                            'tags': ['custom-tag-1', 'someone-else-tag'],
                        },
                    ],
                },
            ],
        },
    )

    await exp3_recorder.get_match_tries(ensure_ntries=1)

    assert response.status_code == 200
    assert response.json() == {
        'priority_values': [
            {'unique_driver_id': unique_driver_id, 'value': priority_value},
        ],
    }


@pytest.mark.now('2021-09-17T12:00:00+0000')
@pytest.mark.experiments3(filename='exp3_out_of_exp.json')
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_priority_fetch_bulk_few_chunks(
        taxi_driver_metrics_storage, experiments3,
):
    await taxi_driver_metrics_storage.invalidate_caches()
    await taxi_driver_metrics_storage.run_task('dist-version-refresher')

    exp3_recorder = experiments3.record_match_tries('completion_scores_levels')
    response = await taxi_driver_metrics_storage.post(
        '/v1/priority/fetch-bulk',
        json={
            'chunks': [
                {
                    'tariff_zone': 'custom-tariff_zone-1',
                    'drivers': [
                        {
                            'unique_driver_id': '100000000000000000000000',
                            'tags': ['custom-tag-1', 'someone-else-tag'],
                        },
                        {
                            'unique_driver_id': '200000000000000000000000',
                            'tags': ['custom-tag-1', 'someone-else-tag'],
                        },
                    ],
                },
                {
                    'tariff_zone': 'custom-tariff_zone-1',
                    'drivers': [
                        {
                            'unique_driver_id': '300000000000000000000000',
                            'tags': ['custom-tag-1', 'someone-else-tag'],
                        },
                        {
                            'unique_driver_id': '400000000000000000000000',
                            'tags': ['custom-tag-1', 'someone-else-tag'],
                        },
                    ],
                },
            ],
        },
    )

    await exp3_recorder.get_match_tries(ensure_ntries=4)

    assert response.status_code == 200
    assert response.json() == {
        'priority_values': [
            {'unique_driver_id': '100000000000000000000000', 'value': 5},
            {'unique_driver_id': '200000000000000000000000'},
            {'unique_driver_id': '300000000000000000000000'},
            {'unique_driver_id': '400000000000000000000000'},
        ],
    }
