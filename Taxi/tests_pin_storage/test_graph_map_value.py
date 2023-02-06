import pytest

CONTENT_KEY = 'taxi_graph_surge/__default__/default'


@pytest.mark.parametrize(
    'point, value',
    [['37.655740,55.750098', 2.0], ['37.667603,55.748344', 1.1]],
)
async def test_graph_map(taxi_pin_storage, s3_polyline_storage, point, value):
    s3_polyline_storage.add_map(
        content_key=CONTENT_KEY,
        s3version='2',
        created='2019-01-02T03:00:00+0000',
        expires='2019-01-02T04:00:00+0000',
    )
    await taxi_pin_storage.invalidate_caches()
    response = await taxi_pin_storage.get(
        '/v1/graph-map/get-value',
        headers={'Content-Type': 'application/json'},
        params={'point': point, 'categories': ['econom']},
    )
    assert response.status_code == 200

    data = response.json()
    assert data['values']['econom'] == value
