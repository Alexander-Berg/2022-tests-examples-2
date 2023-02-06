import json

import pytest


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_add_samples(
        taxi_heatmap_sample_storage, redis_store, load_binary,
):
    # invalid body
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(42),
    )
    assert response.status_code == 400

    # missing samples
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps({}),
    )
    assert response.status_code == 400

    # invalid samples
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps({'samples': 42}),
    )
    assert response.status_code == 400

    # missing meta
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 'test_type',
                        'map_name': 'test_name',
                        'value': 42,
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # invalid meta
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': 'abc',
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 'test_type',
                        'map_name': 'test_name',
                        'value': 42,
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # missing point
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'type': 'test_type',
                        'map_name': 'test_name',
                        'value': 42,
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # invalid point
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3},
                        'type': 'test_type',
                        'map_name': 'test_name',
                        'value': 42,
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # missing type
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'map_name': 'test_name',
                        'value': 42,
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # invalid type
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 41,
                        'map_name': 'test_name',
                        'value': 42,
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # missing map_name
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 'test_type',
                        'value': 42,
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # invalid map_name
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 'test_type',
                        'map_name': 41,
                        'value': 42,
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # missing value
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 'test_type',
                        'map_name': 'test_id',
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # invalid value
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 'test_type',
                        'map_name': 'test_name',
                        'value': 'abc',
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # missing weight
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 'test_type',
                        'map_name': 'test_name',
                        'value': 42,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # invalid weight
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 'test_type',
                        'map_name': 'test_name',
                        'value': 42,
                        'weight': 'abc',
                    },
                ],
            },
        ),
    )
    assert response.status_code == 400

    # insert
    response = await taxi_heatmap_sample_storage.put(
        'v1/add_samples',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'samples': [
                    {
                        'meta': {},
                        'point': {'lon': 12.3, 'lat': 45.6},
                        'type': 'test_type',
                        'map_name': 'test_name',
                        'value': 42,
                        'weight': 43,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    assert 'timestamp' in data

    assert redis_store.keys() == [b'test_type:1552003200']
    samples_in_redis = redis_store.lrange('test_type:1552003200', 0, -1)
    assert len(samples_in_redis) == 1
    assert samples_in_redis[0] == load_binary('sample.bin')
