import pytest

SURGE_MAP_VALUE = 1.3851438760757446
SURGE_MAP_VALUES = [{'x': 0, 'y': 0, 'surge': SURGE_MAP_VALUE, 'weight': 1.0}]

POINT_IN_SURGE = [37.752806233, 55.9]
POINT_NOT_IN_SURGE = [27.752806233, 45.9]


@pytest.mark.parametrize('in_surge', [True, False])
@pytest.mark.surge_heatmap(
    cell_size_meter=500.123,
    envelope={
        'br': [POINT_IN_SURGE[0] - 0.00001, POINT_IN_SURGE[1] - 0.00001],
        'tl': [POINT_IN_SURGE[0] + 0.1, POINT_IN_SURGE[1] + 0.1],
    },
    values=SURGE_MAP_VALUES,
)
async def test(taxi_surge_calculator, in_surge, heatmap_storage_fixture):
    point = POINT_IN_SURGE if in_surge else POINT_NOT_IN_SURGE
    response = await taxi_surge_calculator.get(
        'v1/get-map-surge', params={'point': ','.join(map(str, point))},
    )

    assert response.status == 200, response.text

    in_surge_expected = [
        {'name': '__default__', 'value': SURGE_MAP_VALUE},
        {'name': 'econom', 'value': SURGE_MAP_VALUE},
    ]

    actual = response.json()

    in_surge_expected = sorted(in_surge_expected, key=lambda x: x['name'])
    actual['classes'] = sorted(actual['classes'], key=lambda x: x['name'])

    assert actual == {'classes': in_surge_expected if in_surge else []}


@pytest.mark.parametrize('in_surge', [True, False])
@pytest.mark.surge_heatmap(
    cell_size_meter=500.123,
    envelope={
        'br': [POINT_IN_SURGE[0] - 0.00001, POINT_IN_SURGE[1] - 0.00001],
        'tl': [POINT_IN_SURGE[0] + 0.1, POINT_IN_SURGE[1] + 0.1],
    },
    values=SURGE_MAP_VALUES,
)
@pytest.mark.config(HEATMAP_CACHE_NGROUPS_FETCH_SOURCE={'__default__': 's3'})
async def test_s3(taxi_surge_calculator, in_surge, heatmap_storage_fixture):
    point = POINT_IN_SURGE if in_surge else POINT_NOT_IN_SURGE
    response = await taxi_surge_calculator.get(
        'v1/get-map-surge', params={'point': ','.join(map(str, point))},
    )

    assert response.status == 200, response.text

    in_surge_expected = [
        {'name': '__default__', 'value': SURGE_MAP_VALUE},
        {'name': 'econom', 'value': SURGE_MAP_VALUE},
    ]

    actual = response.json()

    in_surge_expected = sorted(in_surge_expected, key=lambda x: x['name'])
    actual['classes'] = sorted(actual['classes'], key=lambda x: x['name'])

    assert actual == {'classes': in_surge_expected if in_surge else []}
