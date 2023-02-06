import pytest

CONTENT_KEY = 'taxi_polygon_surge/__default__/default'


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.parametrize(
    'point, expected',
    [
        pytest.param([32.151, 51.121], 1.3),
        pytest.param([30.151, 51.121], 0.0),
        pytest.param([32.151, 55.121], 0.0),
    ],
)
async def test_get_surge(
        taxi_surge_calculator, s3_polygon_storage, point, expected,
):
    s3_polygon_storage.add_map(
        content_key=CONTENT_KEY,
        s3version='2',
        created='2019-01-02T03:00:00+0000',
        expires='2019-01-02T04:00:00+0000',
    )
    await taxi_surge_calculator.invalidate_caches()
    request = {'point_a': point}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200, response.json()
    data = response.json()
    actual = data['classes'][0]
    assert actual['value_raw'] == expected
    assert actual['surge']['value'] == expected
