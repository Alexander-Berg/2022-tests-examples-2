import pytest


@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'park_id1_driver_id1', 'onfoot'),
        ('dbid_uuid', 'park_id1_driver_id1', 'qctaxidisable'),
        ('dbid_uuid', 'park_id1_driver_id2', 'onfoot'),
    ],
)
@pytest.mark.config(
    COURIER_REQUIRED_TAGS={
        '__default__': {'__default__': {'required_tags': []}},
        'walking_courier': {
            '__default__': {'required_tags': ['onfoot', 'qctaxidisable']},
        },
    },
    TAGS_INDEX={'enabled': True},
    COURIER_TAGS_MONITORING_SETTINGS={
        'enabled_tags_entities': ['dbid_uuid'],
        'driver_modified_lag_seconds': 600,
        'work_interval_seconds': 10,
    },
)
async def test_worker_finished(taxi_api_over_data_metrics, testpoint):
    @testpoint('courier-required-tags-finished')
    def finished(data):
        return data

    await taxi_api_over_data_metrics.enable_testpoints()
    result = (await finished.wait_call())['data']
    assert result['processed'] == 2
    assert result['without_tags'] == 1


async def test_worker_disabled(taxi_api_over_data_metrics, testpoint):
    @testpoint('courier-required-tags-disabled')
    def disabled(data):
        return data

    await taxi_api_over_data_metrics.enable_testpoints()
    result = await disabled.wait_call()
    assert result['data'] == {'status': 'disabled'}
