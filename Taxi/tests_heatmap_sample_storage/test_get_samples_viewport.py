# pylint: disable=consider-using-enumerate
# pylint: disable=len-as-condition
import json

import pytest

from tests_heatmap_sample_storage import common


# +5 min after samples' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        'rpush',
        'test_type0:1552003200',
        common.build_sample(
            0.123,
            0.456,
            'test_type0',
            'test_map_name',
            42,
            43,
            {'value': 'test_meta0'},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'test_type0:1552003200',
        common.build_sample(
            10.124,
            10.457,
            'test_type0',
            'test_map_name',
            44,
            45,
            {'value': 'test_meta1'},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'test_type1:1552003200',
        common.build_sample(
            20.125,
            20.458,
            'test_type1',
            'test_map_name',
            46,
            47,
            {'value': 'test_meta2'},
            1552003200000,
        ),
    ],
    ['rpush', 'test_key3', 'invalid'],
)
@pytest.mark.config(HEATMAP_SAMPLES_TYPES=['test_type0', 'test_type1'])
async def test_get_samples(taxi_heatmap_sample_storage):
    # invalid format
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport', params={'format': 42},
    )
    assert response.status_code == 400

    # missing type (flatbuffer)
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={'format': 'fb', 'tl': '123,456', 'br': '123,456'},
    )
    assert response.status_code == 400

    # missing type (json)
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={'format': 'json', 'tl': '123,456', 'br': '123,456'},
    )
    assert response.status_code == 400

    # invalid tl (flatbuffer)
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'fb',
            'types': 'test_type0',
            'tl': '123',
            'br': '123,456',
        },
    )
    assert response.status_code == 400

    # invalid tl (json)
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'json',
            'types': 'test_type0',
            'tl': '123',
            'br': '123,456',
        },
    )
    assert response.status_code == 400

    # invalid br (flatbuffer)
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'fb',
            'types': 'test_type0',
            'tl': '123,456',
            'br': 'abc',
        },
    )
    assert response.status_code == 400

    # invalid br (json)
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'json',
            'types': 'test_type0',
            'tl': '123,456',
            'br': 'abc',
        },
    )
    assert response.status_code == 400

    # none match (flatbuffer)
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'fb',
            'types': 'missing_type',
            'tl': '123,456',
            'br': '123,456',
        },
    )
    assert response.status_code == 200
    samples = common.parse_samples(response.content)
    assert not samples

    # none match (json)
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'json',
            'types': 'missing_type',
            'tl': '123,456',
            'br': '123,456',
        },
    )
    assert response.status_code == 200
    data = response.json()
    samples = data['samples']
    assert len(samples) == 0

    # some match (viewport) (flatbuffer)
    expected_meta = {'test_meta0': True}
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'fb',
            'types': 'test_type0',
            'tl': '-5,7',
            'br': '5,-7',
        },
    )
    assert response.status_code == 200
    samples = common.parse_samples(response.content)
    for i in range(0, len(samples)):
        assert expected_meta.pop(
            json.loads(samples[i].Meta().decode())['value'],
        )
    assert not expected_meta

    # some match (viewport) (json)
    expected_meta = {'test_meta0': True}
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'json',
            'types': 'test_type0',
            'tl': '-5,7',
            'br': '5,-7',
        },
    )
    assert response.status_code == 200
    data = response.json()
    samples = data['samples']
    for i in range(0, len(samples)):
        assert expected_meta.pop(samples[i]['meta']['value'])
    assert not expected_meta

    # some match (types) (flatbuffer)
    expected_meta = {'test_meta0': True, 'test_meta1': True}
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'fb',
            'types': 'test_type0',
            'tl': '-50,70',
            'br': '50,-70',
        },
    )
    assert response.status_code == 200
    samples = common.parse_samples(response.content)
    for i in range(0, len(samples)):
        assert expected_meta.pop(
            json.loads(samples[i].Meta().decode())['value'],
        )
    assert not expected_meta

    # some match (types) (json)
    expected_meta = {'test_meta0': True, 'test_meta1': True}
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'json',
            'types': 'test_type0',
            'tl': '-50,70',
            'br': '50,-70',
        },
    )
    assert response.status_code == 200
    data = response.json()
    samples = data['samples']
    for i in range(0, len(samples)):
        assert expected_meta.pop(samples[i]['meta']['value'])
    assert not expected_meta

    # all match (flatbuffer)
    expected_meta = {
        'test_meta0': True,
        'test_meta1': True,
        'test_meta2': True,
    }
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'fb',
            'types': 'test_type0,test_type1,test_type2',
            'tl': '-50,70',
            'br': '50,-70',
        },
    )
    assert response.status_code == 200
    samples = common.parse_samples(response.content)
    for i in range(0, len(samples)):
        assert expected_meta.pop(
            json.loads(samples[i].Meta().decode())['value'],
        )
    assert not expected_meta

    # all match (json)
    expected_meta = {
        'test_meta0': True,
        'test_meta1': True,
        'test_meta2': True,
    }
    response = await taxi_heatmap_sample_storage.get(
        'v1/get_samples/viewport',
        params={
            'format': 'json',
            'types': 'test_type0,test_type1,test_type2',
            'tl': '-50,70',
            'br': '50,-70',
        },
    )
    assert response.status_code == 200
    data = response.json()
    samples = data['samples']
    for i in range(0, len(samples)):
        assert expected_meta.pop(samples[i]['meta']['value'])
    assert not expected_meta
