import pytest

from tests_heatmap_sample_storage import common


@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        'rpush',
        'test_type0:1552003494',
        common.build_sample(
            0.123,
            0.456,
            'test_type0',
            'test_map_name',
            42,
            43,
            {'value': 'test_meta0'},
            1552003495000,
        ),
    ],
)
@pytest.mark.config(
    HEATMAP_SAMPLES_TYPES=['test_type0'],
    HEATMAP_SAMPLES_CACHE_UPDATE_CONCURRENCY=2,
)
async def test_get_samples(taxi_heatmap_sample_storage):
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples', params={'format': 'json', 'types': 'test_type0'},
    )
    assert response.status_code == 200
    data = response.json()
    samples = data['samples']
    assert len(samples) == 1
